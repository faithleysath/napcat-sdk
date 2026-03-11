# CLI / MCP Doc 重构实施方案

## 1. 背景

当前仓库里有两套面向“文档查询”的入口：

- CLI 命令：`napcat-sdk doc ...`
- MCP 服务：`napcat-sdk mcp doc`

两者已经共享了底层文档扫描与生成逻辑，核心集中在 `src/napcat/cli/doc/logic.py`，但在以下层面存在重复实现：

- 能力定义重复
  - CLI 维护 `apis / api / files / code / class`
  - MCP 维护 `list_apis / get_api_details / list_code_files / get_code_file / get_class_definition`
- 参数校验重复
  - `names` / `paths` 类型检查、非空检查、错误提示分别写了两份
- 输出包装重复
  - CLI 包装为终端文本或 `--json`
  - MCP 包装为 tool result / resource result
- 能力变更成本偏高
  - 新增或修改一个文档能力，通常需要同时改：
    - CLI parser
    - CLI handler
    - MCP tools/list
    - MCP tools/call
    - MCP resources/read 或 templates/list

这说明当前设计已经完成了“逻辑共享”，但还没有完成“能力层共享”。

## 2. 问题定义

### 2.1 现状中的重复

重复并不在文档内容生成本身，而在以下两层：

1. 应用服务层
   - 解释“某个文档能力是什么”
   - 解释“参数怎么校验”
   - 解释“结果里哪些属于错误”

2. 适配层
   - CLI 子命令分发
   - MCP tool / resource 分发

### 2.2 现状中的技术债

- `doc apis --json` 目前是先生成 markdown，再反解析成 JSON。
- `logic_get_*` 返回值主要是字符串，导致：
  - 结果类型不明确
  - 错误与正常结果混在一起
  - 不利于多输出格式复用
- MCP 里硬编码了工具元数据、工具分发逻辑、资源模板逻辑，维护成本高。

### 2.3 重构目标

本次重构的核心目标不是“功能变更多”，而是：

- 用一套共享服务层定义文档能力
- 让 CLI 和 MCP 都成为薄适配器
- 避免 markdown 字符串作为唯一中间表示
- 为后续新增能力保留单点扩展路径

## 3. 非目标

本次不做以下事情：

- 不重写文档扫描逻辑本身
- 不引入外部框架或复杂依赖
- 不把 `argparse` 全部改造成动态生成
- 不在第一阶段追求完全消灭所有重复
- 不改变现有 CLI 命令名和 MCP tool 名

## 4. 目标架构

建议将文档模块拆成 4 层：

1. 数据采集层
   - 保留在 `src/napcat/cli/doc/logic.py`
   - 负责扫描 API、源码、类定义、缓存

2. 服务层
   - 新增 `src/napcat/cli/doc/service.py`
   - 负责参数校验、统一错误模型、结构化结果输出

3. 渲染层
   - 新增 `src/napcat/cli/doc/render.py`
   - 负责将结构化结果渲染为：
     - CLI 纯文本
     - CLI JSON
     - MCP text content

4. 能力注册层
   - 新增 `src/napcat/cli/doc/registry.py`
   - 负责定义：
     - 有哪些文档能力
     - 每个能力的输入/描述/映射关系
     - MCP tool / resource / resource template 的元数据与分发映射

CLI 和 MCP 只使用 2/3/4 层，不直接自己拼接文档内容。

## 5. 目录调整建议

建议形成如下结构：

```text
src/napcat/cli/doc/
├── __init__.py
├── logic.py
├── models.py
├── service.py
├── render.py
└── registry.py
```

### 各文件职责

#### `logic.py`

保留以下职责：

- 扫描 API 元数据
- 扫描源码树
- 扫描类定义
- 缓存
- 提供尽量原子化的数据获取函数

建议从“面向字符串输出”逐步过渡到“面向原始结构输出”。

#### `models.py`

定义结构化结果模型，建议优先使用 `dataclass`：

- `DocProblem`
- `ApiIndexItem`
- `ApiDetailItem`
- `CodeIndexEntry`
- `CodeFileItem`
- `ClassDefinitionItem`
- `OperationResult[T]`

目标是把“成功结果”和“部分失败结果”表达清楚，而不是靠字符串前缀 `# Error` 判断。

#### `service.py`

定义统一服务接口，例如：

- `list_apis()`
- `get_api_details(names: list[str])`
- `list_code_files()`
- `get_code_files(paths: list[str])`
- `get_class_definitions(names: list[str])`

这里负责：

- 语义级参数校验
- 调用 `logic.py`
- 把原始结果装配成结构化模型
- 区分：
  - 成功
  - 部分成功
  - 参数错误
  - 内部错误

这里的“参数校验”建议限定为业务语义相关的校验，例如：

- 非法路径
- 文件不存在
- API / class not found
- 输入类型不符合能力要求

而以下更靠近传输层/界面层的校验，建议保留在 CLI / MCP 适配层：

- CLI 子命令缺少位置参数时的 usage 输出
- MCP request 缺少必填字段时的 JSON-RPC / tool argument 错误包装

#### `render.py`

定义统一渲染函数，例如：

- `render_api_index_text(...)`
- `render_api_index_json(...)`
- `render_api_details_text(...)`
- `render_code_files_text(...)`
- `render_class_definitions_text(...)`
- `render_mcp_text(...)`

这层负责“如何展示”，不负责“展示什么”。

#### `registry.py`

用一份注册表描述能力，例如：

- 内部能力名
- CLI 子命令名
- MCP tool 名
- MCP resource URI / template
- 描述文本
- 参数 schema
- 对应 service handler

这样新增能力时，只需要改：

- service handler
- registry 条目
- 少量 CLI parser 壳层

## 6. 数据模型设计

建议先定义一套最小可用模型。

### 6.1 通用问题模型

```python
@dataclass(slots=True, frozen=True)
class DocProblem:
    kind: Literal["invalid_input", "not_found", "internal"]
    message: str
    target: str | None = None
```

### 6.2 API 索引

```python
@dataclass(slots=True, frozen=True)
class ApiIndexItem:
    name: str
    description: str
```

### 6.3 API 详情

```python
@dataclass(slots=True, frozen=True)
class ApiDetailItem:
    name: str
    found: bool
    signature: str | None
    description: str | None
    response_type: str | None
    typed_dict_codes: tuple[str, ...]
    problems: tuple[DocProblem, ...] = ()
```

### 6.4 源码索引

```python
@dataclass(slots=True, frozen=True)
class CodeIndexEntry:
    path: str
    summary: str | None
    category: Literal["module", "api-definitions", "typed-dicts"]
```
```

### 6.5 源码文件

```python
@dataclass(slots=True, frozen=True)
class CodeFileItem:
    path: str
    found: bool
    content: str | None
    problems: tuple[DocProblem, ...] = ()
```

### 6.6 类定义

```python
@dataclass(slots=True, frozen=True)
class ClassDefinitionSource:
    path: str
    code: str


@dataclass(slots=True, frozen=True)
class ClassDefinitionItem:
    name: str
    found: bool
    sources: tuple[ClassDefinitionSource, ...]
    problems: tuple[DocProblem, ...] = ()
```

### 6.7 操作结果包装

```python
@dataclass(slots=True, frozen=True)
class OperationResult[T]:
    ok: bool
    items: tuple[T, ...]
    problems: tuple[DocProblem, ...] = ()
```
```

说明：

- `ok` 表示整体是否成功
- `items` 允许批量查询结果
- `problems` 表示顶层问题
- 每个 item 自己也能带局部问题

## 7. 服务层接口草案

建议提供一个显式类，而不是只暴露散函数。

```python
class DocService:
    def list_apis(self) -> OperationResult[ApiIndexItem]: ...
    def get_api_details(self, names: Sequence[str]) -> OperationResult[ApiDetailItem]: ...
    def list_code_files(self) -> OperationResult[CodeIndexEntry]: ...
    def get_code_files(self, paths: Sequence[str]) -> OperationResult[CodeFileItem]: ...
    def get_class_definitions(
        self,
        names: Sequence[str],
    ) -> OperationResult[ClassDefinitionItem]: ...
```

### 设计理由

- 以后若要注入缓存策略、日志器、测试替身，会更方便
- 不强依赖 CLI 或 MCP
- 可直接做单元测试

## 8. `logic.py` 的改造策略

### 8.1 第一阶段原则

第一阶段不要大改扫描逻辑，优先增加“原始结构接口”。

例如：

- `_get_api_data()` 已经能返回结构化 `dict`
- 可以直接复用，不必先重写
- `logic_get_index()` / `logic_get_details()` 等保留一段时间，给过渡期用

### 8.2 具体建议

在 `logic.py` 内新增更底层的函数：

- `logic_list_api_items() -> list[ApiDocLike]`
- `logic_get_api_items(names: list[str]) -> list[ApiDocLike | Missing]`
- `logic_list_code_entries() -> list[CodeIndexRawItem]`
- `logic_get_code_file_item(path: str) -> CodeFileRawItem`
- `logic_get_class_sources(name: str) -> list[ClassSourceRawItem]`

然后服务层基于这些原始函数构建 `models.py` 里的结构化对象。

### 8.3 为什么不直接删除现有 `logic_get_*`

因为：

- CLI 和 MCP 当前都依赖它们
- 一步到位替换会让变更面过大
- 先并存更容易做小步重构和回归测试

建议采用：

1. 新增原始接口
2. service 改用原始接口
3. CLI / MCP 改用 service
4. 最后删除旧的字符串接口

## 9. CLI 侧重构方案

目标：让 `src/napcat/cli/commands/doc.py` 从“业务实现”变成“输入解析 + 输出委托”。

### 9.1 保留的职责

- 子命令分发
- `argparse` 对接
- 退出码转换

### 9.2 移除的职责

- 文档内容拼接
- 业务参数校验细节
- 自己维护 JSON 包装细节

### 9.3 重构后的调用形态

大致变为：

```python
service = DocService()
renderer = CliDocRenderer()

result = service.get_api_details(names)
print(renderer.render_api_details(result, json_output=json_output))
return 0 or 1
```

### 9.4 CLI 退出码约定

建议统一：

- `0`
  - 全部成功
- `1`
  - 参数合法，但存在 not found / 文件非法 / 局部失败 / 内部错误
- `2`
  - `argparse` 级别用法错误

现有语义大体如此，尽量保持兼容。

## 10. MCP 侧重构方案

目标：让 `src/napcat/cli/mcp/doc_server.py` 只负责 MCP 协议收发，不再硬编码文档能力细节。

### 10.1 保留的职责

- stdio JSON-RPC 循环
- MCP 协议能力声明
- request / notification 区分
- 错误包装

### 10.2 移除的职责

- 每个 tool 的业务分支
- 每个参数的业务校验
- tool metadata 手工拼接

### 10.3 registry 的作用

`registry.py` 提供统一能力定义，例如：

```python
DOC_OPERATIONS = {
    "list_apis": OperationSpec(...),
    "get_api_details": OperationSpec(...),
    ...
}
```

MCP 侧：

- `tools/list` 从 registry 自动生成
- `tools/call` 根据 registry 查 handler
- `resources/list` / `resources/templates/list` / `resources/read` 也从 registry 或同一份 resource spec 生成

这样新增 `doc` 能力时，MCP 不需要再写新的大分支。

### 10.4 resource 与 tool 的关系

建议暂时保留资源接口，但实现也从 registry / service 取数据。

原因：

- 某些 MCP 客户端更擅长资源读取
- 某些客户端更擅长 tools
- 两种接口并存没有问题，但应共享同一套 handler

## 11. registry 设计建议

建议先建最小版本。

其中 tool 和 resource 可以共用一份能力定义，也可以拆成两组 spec；关键是不要继续把 URI、模板名、`mimeType`、描述文本和 handler 映射散落在 `doc_server.py`。

例如：

```python
@dataclass(slots=True, frozen=True)
class OperationSpec:
    key: str
    cli_name: str | None
    mcp_tool_name: str | None
    description: str
    arg_schema: dict[str, Any]
    invoke: Callable[[DocService, dict[str, Any]], OperationResult[Any]]
```

```python
@dataclass(slots=True, frozen=True)
class ResourceSpec:
    key: str
    uri: str | None
    uri_template: str | None
    name: str
    mime_type: str
    description: str
    read: Callable[[DocService, dict[str, str]], OperationResult[Any]]
```

### 第一阶段 registry 需要承载的信息

- 名称映射
- 描述文本
- 输入 schema
- 调用入口
- resource 元数据与 URI 到 handler 的映射

### 第二阶段再考虑承载的信息

- CLI 帮助文案自动生成
- MCP resource template 自动生成
- JSON schema 进一步细化

第一阶段不建议把 `argparse` 生成也塞进去，复杂度太高。

## 12. 渲染层设计建议

### 12.1 为什么需要 render 层

如果 service 已经返回结构化结果，那么：

- CLI 文本输出
- CLI `--json`
- MCP `content.text`

应该分别由 renderer 处理，而不是在 CLI / MCP 适配层自己手拼。

### 12.2 renderer 最低要求

建议先实现：

- `render_api_index_text`
- `render_api_index_json_obj`
- `render_api_details_text`
- `render_api_details_json_obj`
- `render_code_index_text`
- `render_code_files_text`
- `render_code_files_json_obj`
- `render_class_definitions_text`
- `render_class_definitions_json_obj`

MCP 其实可以直接复用 text 渲染结果，再包成：

```json
{"content": [{"type": "text", "text": "..."}]}
```

## 13. 分阶段实施计划

### Phase 0: 基线冻结

目标：

- 确保当前 CLI doc / MCP doc 测试完整可回归

动作：

- 记录当前支持能力
- 补齐必要测试与快照，至少覆盖：
  - `napcat-sdk doc apis --json`
  - `napcat-sdk doc code <PATH> --json`
  - `tools/list`
  - `tools/call`
  - `resources/read`
- 明确当前退出码语义

产出：

- 可对比的基线行为

### Phase 1: 引入结构化模型

目标：

- 新增 `models.py`
- 不改现有行为

动作：

- 定义 `DocProblem`
- 定义 `ApiIndexItem` / `ApiDetailItem` / `CodeFileItem` / `ClassDefinitionItem`
- 定义 `OperationResult[T]`

风险：

- 很低

### Phase 2: 提取 DocService

目标：

- 新增 `service.py`
- 让业务语义不再散在 CLI / MCP

动作：

- 基于 `logic.py` 封装 `DocService`
- 在 service 内统一校验：
  - 非法路径
  - 文件不存在
  - class/api not found
  - 类型不合法的输入
- 明确保留在适配层的校验：
  - CLI 缺参数时的 usage / exit code
  - MCP 缺字段时的 request / argument 错误

风险：

- 中低
- 需要小心保持现有错误语义

### Phase 3: 提取 renderer

目标：

- 新增 `render.py`
- 消除 CLI 侧 markdown 反解析 JSON 的逻辑

动作：

- 实现 text / json 两类 renderer
- CLI 先切到 renderer

风险：

- 中
- 输出文本可能出现细微差异

### Phase 4: 重构 CLI `doc`

目标：

- `commands/doc.py` 成为薄壳

动作：

- 子命令只负责挑选 service 方法
- 输出交给 renderer
- `_handle_*` 逻辑大幅简化

完成标准：

- `commands/doc.py` 不再直接调用 `logic_get_*`

### Phase 5: 引入 registry

目标：

- 建立统一能力声明

动作：

- 给现有 5 个能力建 registry 条目
- 让 MCP `tools/list` 基于 registry 自动生成
- 让 MCP `tools/call` 根据 registry 分发
- 为现有 API / code / class 资源建立 resource spec
- 让 `resources/list` / `resources/templates/list` / `resources/read` 也由 registry 或 resource spec 驱动

风险：

- 中
- 需要注意 MCP 现有 tool 名兼容性
- 需要注意现有 URI 与 template 兼容性

### Phase 6: 重构 MCP `doc_server`

目标：

- 去掉大段业务 if/match 分支

动作：

- `tools/list` 由 registry 驱动
- `tools/call` 参数解析尽量委托给 registry/service
- `resources/list` / `resources/templates/list` / `resources/read` 复用同一份 resource spec
- request 级错误与业务错误继续由协议层统一包装

完成标准：

- `doc_server.py` 主要剩协议处理

### Phase 7: 清理旧接口

目标：

- 删除不再使用的旧字符串接口

动作：

- 删除冗余 `logic_get_*` 包装函数，或降为兼容层
- 删除 CLI 内部重复的输出包装函数
- 删除旧测试中的实现细节断言，改为行为断言

## 14. 迁移顺序建议

推荐按以下顺序落地，确保每一步都可回滚：

1. 新增 `models.py`
2. 新增 `service.py`
3. 新增 `render.py`
4. 让 CLI `doc` 切到 service + render
5. 新增 `registry.py`
6. 让 MCP `doc_server` 切到 registry + service
7. 清理旧接口

原因：

- CLI 边界更简单，先改 CLI 风险更低
- MCP 协议层更复杂，后改更稳

## 15. 测试计划

### 15.1 保留的现有测试

继续保留：

- `src/tests/test_cli_doc.py`
- `src/tests/test_cli_gateway.py`
- `src/tests/test_cli_regressions.py`
- `src/tests/test_smoke_imports.py`

但这些测试目前不足以称为“基线冻结”，尤其 MCP 侧缺少协议级行为覆盖，因此需要在 Phase 0 先补基线用例，再进入结构重构。

### 15.2 新增的测试层级

建议新增：

#### `test_doc_service.py`

覆盖：

- `list_apis`
- `get_api_details`
- `list_code_files`
- `get_code_files`
- `get_class_definitions`
- not found / invalid path / empty input

#### `test_doc_render.py`

覆盖：

- text 渲染
- json 渲染
- 局部失败结果渲染

#### `test_doc_registry.py`

覆盖：

- registry 完整性
- CLI 名与 MCP tool 名映射
- tool schema 基本合法性

#### `test_cli_doc.py`

重点从“内部函数调用”转为“行为输出”测试。

#### `test_mcp_doc_server.py`

建议补足：

- `tools/list`
- `tools/call`
- `resources/list`
- `resources/templates/list`
- `resources/read`
- 非法参数返回

### 15.3 验证命令

建议每阶段至少执行：

```bash
uv run pytest -q src/tests/test_cli_doc.py src/tests/test_cli_regressions.py src/tests/test_smoke_imports.py
uv run ruff check src/napcat/cli src/tests
uv run pyright src/napcat/cli
```

## 16. 风险点与应对

### 风险 1：输出文本变化导致测试或用户脚本破坏

应对：

- 第一阶段优先保持文本输出尽量一致
- 新旧渲染结果做 snapshot 对比

### 风险 2：MCP tool 元数据变化导致客户端兼容性问题

应对：

- 保持现有 tool 名不变
- 保持输入参数结构不变
- 只改内部来源，不改外部协议名字
- 保持现有 resource URI / template / `mimeType` 不变

### 风险 3：旧 `logic_get_*` 删除过早

应对：

- 先并存
- 等 CLI 与 MCP 都切完再删

### 风险 4：过度抽象

应对：

- registry 第一阶段只承载最必要信息
- 不做动态生成 `argparse`
- 不把 renderer 和 service 过度泛型化

## 17. 验收标准

重构完成后，应满足：

1. CLI `doc` 对外功能不退化
2. MCP `mcp doc` 对外 tool / resource 名称不退化
3. 新增一个文档能力时：
   - 不需要在 CLI 和 MCP 各写一套业务逻辑
   - 至少能通过 service + registry / resource spec 单点接入
4. CLI 不再依赖“先渲染 markdown，再解析 JSON”
5. `doc_server.py` 不再维护大段重复的 tool / resource 能力分支

## 18. 推荐的最小首批提交拆分

为了降低 review 难度，建议按以下 commit 粒度拆：

### Commit 1

- 新增 `models.py`
- 新增 `service.py`
- 新增对应测试

### Commit 2

- 新增 `render.py`
- CLI `doc` 切到 service + render
- 更新 CLI 测试

### Commit 3

- 新增 `registry.py`
- MCP `doc_server` 切到 registry + service
- MCP resource 读取也切到统一 spec
- 更新 MCP 测试

### Commit 4

- 清理旧 `logic_get_*` 包装接口
- 清理多余测试与死代码

## 19. 我的实施建议

如果开始落地，我建议先做一个“小而稳”的第一步：

- 只引入 `models.py + service.py`
- 不改 `logic.py` 的扫描实现
- 先让 CLI `doc` 使用 service
- MCP 下一步再切

原因：

- 这样最容易 review
- 风险最小
- 能尽快验证“结构化服务层”是否合理
- 同时不把 CLI usage / MCP request 校验过早塞进 service，避免边界变糊

## 20. 待确认事项

开始实施前，建议确认以下点：

1. 是否接受新增 `docs/` 文档与 `src/napcat/cli/doc/` 下的新模块文件
2. CLI 文本输出是否必须保持字面兼容
3. MCP 的 `resource` 能力是否必须保留，还是只保留 `tools`
4. 是否接受分 3 到 4 个小提交逐步推进，而不是一次性改完
