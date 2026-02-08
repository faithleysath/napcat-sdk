from __future__ import annotations

import shutil
import subprocess

import pytest


def _run(cmd: list[str]) -> tuple[int, str]:
    completed = subprocess.run(cmd, capture_output=True, text=True)
    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part).strip()
    return completed.returncode, output


@pytest.mark.static
def test_ruff_strict_all_rules() -> None:
    assert shutil.which("uv"), "uv not found in PATH"

    code, output = _run(["uv", "run", "ruff", "check", "src", "scripts"])
    assert code == 0, f"Ruff check failed (exit={code})\n\n{output}"


@pytest.mark.static
def test_pyright_strict_type_check() -> None:
    assert shutil.which("uv"), "uv not found in PATH"

    code, output = _run(["uv", "run", "pyright"])
    assert code == 0, f"Pyright type check failed (exit={code})\n\n{output}"
