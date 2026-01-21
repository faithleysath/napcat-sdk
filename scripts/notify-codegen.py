import subprocess
import shutil
import os
import glob
import re
import asyncio
import logging
from openai import AsyncOpenAI

# --- 配置 ---
TS_SOURCE_DIR = "./NapCatQQ/packages/napcat-onebot/event/notice"
PY_OUTPUT_DIR = "./src/napcat/types/events/notice"

IGNORE_FILES = {
    "OB11BaseNoticeEvent.ts", 
    "index.ts"
}

API_BASE = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "google/gemini-3-flash")
CONCURRENCY_LIMIT = 10

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# --- 核心 Prompt (优化版) ---
SYSTEM_PROMPT = """
You are a Python Transpiler specialized in converting TypeScript definitions to **modern Python 3.12+** dataclasses.

**Input Pre-processing Note:**
The prefix "OB11" has already been removed from the input code. "OB11GroupBanEvent" appears as "GroupBanEvent".

**Python 3.12+ Syntax Rules (STRICT):**
1.  **Generics**: Use `list[T]`, `dict[K, V]`, `type[T]`. (NO `typing.List`).
2.  **Unions**: Use `int | str`. (NO `typing.Union`).
3.  **Optionals**: Use `str | None = None`. (NO `typing.Optional`).
4.  **Mapping**: unknown / any -> Any

**Import Strategy:**
1.  **Standard Libs**: **DO NOT** import `dataclasses`, `typing`, or `__future__`. The wrapper script handles these.
2.  **Local Imports**:
    -   If extends `BaseNoticeEvent` -> Add `from .base import NoticeEvent` at the top.
    -   If extends `xxxNoticeEvent` -> Add `from .xxxNoticeEvent import xxxNoticeEvent`.

**Helper Structures (CRITICAL):**
1.  **Interfaces**: If the TS file defines an `interface` (e.g., `GroupUploadFile`) used by the main class:
    -   Convert it into a separate `@dataclass`.
    -   Place it **BEFORE** the main event class.
2.  **Types (Inline Strategy)**: 
    -   If a field uses a defined `type` alias (e.g., `sub_type: GroupDecreaseSubType`), **do NOT** generate a separate Python type alias.
    -   Instead, find the values of that type and **inline** them directly into the field definition.
    -   Example: `sub_type: Literal['leave', 'kick', 'kick_me'] = 'leave'`.

**Data Structure & Fields:**
1.  Use `@dataclass(slots=True, frozen=True, kw_only=True)`.
2.  **Field Extraction Rule (STRICT)**: 
    -   **Source of Truth**: Extract ONLY fields explicitly declared as **properties** in the TypeScript class body (e.g., `operator_id: number;`).
    -   **Ignore Constructor**: Do NOT extract fields from `constructor` parameters or `this.x = y` assignments inside the constructor. We assume if it's not declared in the class body, it belongs to the parent class.
    -   **Exception**: If a constructor parameter has `public` / `private` modifier (e.g. `constructor(public id: number)`), treat it as a class property and extract it.
3.  **Literals & Defaults (CRITICAL)**:
    -   **Strict Fields**: `notice_type` and `sub_type` MUST use strict `Literal["value"]` (e.g., `notice_type: Literal["group_ban"] = "group_ban"`). Do NOT add `| str`.
    -   **Open Literals (String Defaults)**: For ANY other string field that has a default value (e.g., `tag = 'BotOfflineEvent'`), you **MUST** use the "Open Literal" pattern:
        -   **Pattern**: `field_name: Literal['DefaultValue'] | str = 'DefaultValue'`
        -   **Example**: If TS has `tag = 'MyTag'`, Python output must be `tag: Literal['MyTag'] | str = 'MyTag'`.
    -   **Reasoning**: This tells type checkers the default is a specific literal, but allows users to override it with any string.

**Output:**
-   Return **ONLY** the valid Python code.
"""

def clean_filename(ts_filename: str) -> str:
    """OB11GroupBanEvent.ts -> GroupBanEvent.py"""
    name = ts_filename.replace(".ts", "")
    if name.startswith("OB11"):
        name = name[4:]
    return name + ".py"

async def process_file(client: AsyncOpenAI, sem: asyncio.Semaphore, ts_path: str) -> tuple[str, list[str], str]:
    filename = os.path.basename(ts_path)
    async with sem:
        try:
            with open(ts_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 预处理：去掉 OB11 前缀，减少 LLM 幻觉
            content = content.replace("OB11", "")
            
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"TS File: {filename}\nContent:\n{content}"}
                ],
                temperature=0.0
            )
            
            code = response.choices[0].message.content or ""
            
            # 清理 Markdown
            code = re.sub(r'^```python\s*', '', code, flags=re.MULTILINE)
            code = re.sub(r'^```\s*', '', code, flags=re.MULTILINE).strip()
            
            # 提取类名 (简单的正则，假设每行只有一个 class 定义)
            classes = re.findall(r'class\s+(\w+)', code)
            
            out_name = clean_filename(filename)
            return out_name, classes, code

        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            return "", [], ""

def run_ruff_formatting(target_dir: str):
    ruff_exe = shutil.which("ruff")
    if not ruff_exe:
        logger.warning("⚠️ Ruff not found in PATH. Skipping formatting. (pip install ruff)")
        return

    logger.info("🧹 Running Ruff to clean imports and format code...")

    try:
        subprocess.run(
            [ruff_exe, "check", "--fix", "--select", "I,F401", target_dir],
            check=True,
            capture_output=True,
            text=True
        )
        subprocess.run(
            [ruff_exe, "format", target_dir],
            check=True,
            capture_output=True, # 如果不想看Ruff的输出，可以捕获
            text=True
        )
        
        logger.info("✨ Ruff formatting complete!")

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Ruff failed:\n{e.stderr}")

async def main():
    if not API_KEY:
        logger.error("Error: Environment variable OPENAI_API_KEY is not set.")
        return

    client = AsyncOpenAI(api_key=API_KEY, base_url=API_BASE)
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

    ts_files = [
        f for f in glob.glob(os.path.join(TS_SOURCE_DIR, "*.ts")) 
        if os.path.basename(f) not in IGNORE_FILES
    ]
    
    logger.info(f"Detected {len(ts_files)} TypeScript files.")
    
    tasks = [process_file(client, sem, f) for f in ts_files]
    results = await asyncio.gather(*tasks)

    if not os.path.exists(PY_OUTPUT_DIR):
        os.makedirs(PY_OUTPUT_DIR)

    # 准备 __init__.py
    init_lines = ["from .base import NoticeEvent, UnknownNoticeEvent"]
    all_exports = ["NoticeEvent", "UnknownNoticeEvent"]

    for fname, classes, code in results:
        if not fname or not code:
            continue
        
        out_path = os.path.join(PY_OUTPUT_DIR, fname)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("# AUTO-GENERATED FILE. DO NOT EDIT.\n")
            f.write("# Generated by NapCat Python SDK Generator\n\n")
            
            # 统一写入标准头，不再依赖检测代码内容
            f.write("from __future__ import annotations\n")
            f.write("from dataclasses import dataclass\n")
            f.write("from typing import Literal, Any\n") 
            
            f.write("\n")
            f.write(code)
        
        mod_name = fname.replace(".py", "")
        if classes:
            init_lines.append(f"from .{mod_name} import {', '.join(classes)}")
            all_exports.extend(classes)

    # 生成 __init__.py
    init_path = os.path.join(PY_OUTPUT_DIR, "__init__.py")
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(init_lines))
        f.write("\n\n__all__ = [\n")
        unique_exports = sorted(list(set(all_exports)))
        for c in unique_exports:
            f.write(f"    '{c}',\n")
        f.write("]\n")

    logger.info(f"Success! Generated {len(results)} files in {PY_OUTPUT_DIR}")
    run_ruff_formatting(PY_OUTPUT_DIR)

if __name__ == "__main__":
    asyncio.run(main())