# Hetu MCP Server

Current version: 0.0.3. See [CHANGELOG.md](./CHANGELOG.md). Recent unreleased changes are tracked under `Unreleased`.

用于读取、查询、校验和编辑 Hetu `.ws` 工作区文件的 MCP 服务。

当前公开 MCP 工具共 `29` 个，覆盖文件 I/O、`BlockScript` 片段操作、Block/MyBlock 结构编辑、资源查询校验、模块查询、文档生成、统计分析和整体验证。

## 概览

`hetu_mcp` 是面向 Hetu `.ws` 工程的本地 MCP 服务，主要用于在 AI/编辑工具中读取、查询、修改和校验工作区数据。

它目前支持：

- 读取和保存 `.ws` 文件
- 处理完整项目树，包括 `scene` / `agents` / `assets` 下的多个 `BlockScript`
- 查询、添加、删除、移动 fragment
- 创建和修改 block 结构
- 创建、更新、删除、查询 MyBlock
- 查询序列化模块、Block 文档和模块文档
- 查询和校验 Pangu3D 资源索引
- 对完整项目做结构、对象类型、项目模式、字段类型和 MyBlock 约束校验
- 按 Hetu 运行时反序列化要求校验模块属性、BlockScript 形状、block 参数载荷和 MyBlock 定义
- 统计工程中的脚本、模块、Block、类别等信息
- 用当前 MCP 链路导出参考工程统计和人类可读剧本

## 规则来源

当前实现通过已提交的 MCP 内部快照和明确的来源说明，与 Hetu 源码行为保持对齐：

- Block 定义/注册快照来源：`/script/Hetu/Block/Defines` 和 `/script/Hetu/Block/Modules/Internal`。
- 模块/对象序列化快照来源：`/script` 中的对象和服务类。
- 场景元素 Block 目标类型规则来源：`/script/Hetu/IDE/IDE/Sprite/SpriteAPI.cs`。
- 项目策略规则来源：`/script/Hetu/IDE/Data/HetuProject.cs` 和 `/script/Hetu/IDE/IDE/Mediators/BlockMediator.cs`。

实现上：

- `definitions/script_definition_data.py` 保存运行时使用的 MCP 内部 Block/module 元数据快照。
- `definitions/script_definitions.py` 保留源码提取逻辑，仅用于显式维护或重新生成流程。
- `definitions/workspace_schema.py` 维护 scene element -> block target type 表，并结合每个 block 定义中的 `object_types` 进行校验。

正常运行时不会读取 `/script` 或 `mcp/hetu_mcp` 外部的其他源码文件。如需更新 Block/module 元数据，需要重新生成并提交内部快照。资源数据是初始化例外：如果 `resource/resouce_summary.json` 或 `resource/resource_index.json` 缺失，server 会调用 `utils/export_resource_list.py` 拉取接口，并在 MCP 包内重新生成这些文件。

## 目录结构

- `server.py`: MCP server 入口，负责 29 个工具的注册与分发
- `version.py`: 包与 MCP server 的版本元数据
- `definitions/block_models.py`: Block 定义、类型元数据、对象类型约束、参数载荷形状与结构校验
- `definitions/script_definition_data.py`: 已提交的 MCP 内部 Block/module 元数据快照
- `definitions/script_definitions.py`: 元数据加载，以及显式源码提取/重新生成辅助逻辑
- `definitions/workspace_schema.py`: 项目/模块 schema、运行时字段类型校验、BlockScript 遍历、owner 目标类型解析、场景元素规则、对话和 `editorScene` 校验
- `definitions/resource_definitions.py`: 生成的资源枚举、索引读取、查询辅助和校验辅助
- `handlers/workspace_operations.py`: 文件 I/O、fragment 操作、MyBlock 操作和 workspace 写入辅助
- `handlers/block_operations.py`: block 创建和局部 block 结构编辑
- `handlers/validation_operations.py`: 查询、文档、统计、BlockScript/MyBlock 形状和完整 workspace 校验处理
- `handlers/resource_operations.py`: 资源查询和资源校验工具的 MCP handler 封装
- `resource/`: 运行时资源简表、完整索引、Sprite3D/Role/VFX 提取元数据和生成的资源报告
- `utils/export_reference_report.py`: 通过当前 MCP server 导出参考 `.ws` 报告和可读剧本
- `utils/export_resource_list.py`: 拉取并解析 Pangu3D 资源数据到 `resource/`，并重新生成 `definitions/resource_definitions.py`
- `utils/export_sprite3d_vfx_metadata.py`: 下载 Sprite3D/Role/VFX `.ab`，通过 Unity 解析额外元数据，并差量更新 `sprite_3d.json`、`vfx.json` 和 `resource_index.json`
- `utils/smoke_test.py`: 本地 stdio MCP smoke tests 和回归覆盖
- `requirements.txt`: 运行依赖

说明：

- 旧的独立 `mcp_config.json` 已删除，本 README 中的示例是当前维护的配置入口。

## 工具总览

### 文件工具

- `load_workspace_file`
  - 加载并解析 `.ws` 文件
  - 只允许读取 `.ws`
  - 如果启动时传入了 `workspace_root`，路径不能逃逸出该根目录
- `save_workspace_file`
  - 把 JSON 保存回文件
  - 默认 `create_backup=true`，会生成 `.backup_YYYYMMDD_HHMMSS.ws`
  - 默认 `validate_before_save=true`，保存前会先执行 `validate_workspace`
  - 如确实需要落盘中间态/历史坏数据，可显式传 `validate_before_save=false`

### Fragment 工具

- `get_fragments`
- `add_fragment`
- `remove_fragment`
- `update_fragment_position`

### Block 工具

- `create_block`
- `get_block_info`
- `modify_block_parameter`
- `append_block`
- `insert_block_child`

### MyBlock 工具

- `create_myblock`
- `get_myblocks`
- `remove_myblock`
- `update_myblock_fragment`
- `create_myblock_call`
- `find_myblock_usages`

### 查询/校验/文档工具

- `validate_block`
- `find_blocks_by_type`
- `get_block_documentation`
- `get_modules`
- `validate_module`
- `find_modules_by_type`
- `get_module_documentation`
- `analyze_workspace_statistics`
- `validate_workspace`

### 资源工具

- `get_resource`
  - 按 `resource_id` 返回完整资源记录
  - 数据来源：`mcp/hetu_mcp/resource/resource_index.json`
- `find_resources`
  - 按 `resource_id/resource_name/resource_type/entry_id/entry_name/entry_kind/entry_class_id/entry_type/entry_category_id/entry_category` 查询资源
  - 默认最多返回 20 条，可通过 `limit` 调整
- `validate_resource`
  - 校验资源 ID、类型、entry class/category 等组合是否存在且一致
  - 可选 `require_primary_url=true` 校验资源是否有主下载地址

## 输入形态

多数查询和校验工具支持三种输入形态：

### 1. 完整 `.ws` 项目

推荐真实使用时优先传完整项目根对象。

优点：

- 能识别多个 `BlockScript`
- 能获得脚本 owner 类型
- 能执行 end-user mode / `showmyblock` / `whitelist` 校验
- 能同时校验 `scene`、`agents`、`assets`、`dialogues`、`editorScene`

### 2. 模块子树

适合只拿某个 `Scene` / `Character` / `CameraService` 子树来做局部验证。

优点：

- 仍然保留 owner 类型上下文
- 仍可触发场景元素类型限制

### 3. 独立 `BlockScript`

适合只做结构级编辑或查询。

限制：

- 没有 owner 类型上下文
- 不会知道这个脚本挂在哪个场景元素上
- 不能完整执行“该对象类型允许哪些 Block”的限制
- 不能执行完整项目级策略校验

结论：

- 要做真实工程编辑与最终验证，请传完整 `.ws`
- 只传裸 `BlockScript` 时，拿到的是“结构正确性”，不是“工程上下文正确性”

## 多脚本工作区与 `script_id`

`scene` / `agents` / `assets` 里可能有多个 `BlockScript`。在这种情况下，部分编辑工具必须显式传 `script_id`，否则会报错。

当工作区内有多个 `BlockScript` 时，以下工具要求 `script_id`：

- `add_fragment`
- `remove_fragment`
- `update_fragment_position`
- `create_myblock`
- `remove_myblock`
- `update_myblock_fragment`

查询类工具通常会在结果里返回 `source`，这个值就是对应脚本的 `script_id`。

## 当前已实现的关键约束

### 1. Block 结构校验

`validate_block` 和 `validate_workspace` 会检查：

- `define` 是否存在
- `sections / params / children / next` 结构是否合法
- 自定义 myblock 是否已声明
- 常见兼容别名是否可识别，例如 `WhenClicked`、`SayForSeconds`、`ThinkForSeconds`、`GetDistanceTo`

注意：

- `validate_block` 更偏结构级
- `validate_workspace` 才会叠加 owner type 和项目策略限制

### 2. 场景元素类型可用 Block 校验

MCP 已按 `SpriteAPI.IsTargetBlock()` 规则执行“对象类型 -> 可用 Block”限制。

这套限制定义集中维护在 `definitions/workspace_schema.py`，操作层和校验层都会读取同一份定义。

当前使用的映射为：

- `Scene -> Scene`
- `CameraService -> CameraService`
- `ImageSet -> ImageSet`
- `MeshPart -> Part`
- `Avatar -> Avatar`
- `Character -> Character`
- `PartSet -> PartSet`
- `QuestObject -> QuestObject`
- `Quad -> Quad`

这套规则会在以下入口生效：

- `add_fragment`
- `update_myblock_fragment`
- `validate_workspace`

参考完整支持矩阵：

- Runtime support table: `mcp/hetu_mcp/definitions/workspace_schema.py`

### 3. end-user mode / 项目模式限制

当前 MCP 已对齐项目模式相关的核心限制。

`end-user mode` 的判定来自项目根字段 `type`：

- `0` = `Normal`
- `2` = `CreativeProduct`
- `4` = `CreativeStudent`

当项目处于 end-user mode 时：

- `magic` 类 block 会被禁用
- `experiment` 类 block 会被禁用
- 如果 `whitelist` 非空，则仅允许白名单中的内置 block
- 如果 `showmyblock=false`，则不允许自定义 MyBlock
- 如果 MyBlock 的 `displayName` 以 `#` 开头，也会被视为隐藏，不允许使用

这套规则会在以下入口生效：

- `create_myblock`
- `add_fragment`
- `update_myblock_fragment`
- `validate_workspace`

### 4. MyBlock 规则

当前 MyBlock 处理已经按现有 Hetu 数据格式整理为：

- 新写入的参数格式使用 `columns`
- 旧格式 `params` 仍可被读取，但不会作为新的输出格式
- 自动生成的 MyBlock 名称格式是 `script_id/<name>/myblockdefine`
- 同一个 `BlockScript` 内，`displayName` 不能重复
- `myblock.fragment.head.define` 必须与 MyBlock 自身 `name` 完全一致

注意：

- `remove_myblock` 只删除定义，不会自动修复现有调用
- 如果删掉定义但保留调用，后续 `validate_workspace` 会报“未定义 myblock”

### 5. 项目根与模块结构校验

`validate_workspace` 会同时覆盖：

- 项目根字段类型
- `scene` / `agents` / `assets` 模块结构
- 模块 `props`
- 模块 `props2` 自定义属性
- `operationUIs`
- `dialogues`
- `editorScene`
- `sceneData`
- 每个 `BlockScript` 的 fragments
- 每个 MyBlock 的 fragment

其中：

- `res` 必须是整数列表，且每个资源 ID 必须存在于 `resource/resouce_summary.json`
- `editorScene.cameras[*].position` 必须是 3D 向量
- `editorScene.cameras[*].rotation` 必须是 quaternion
- 数值字符串支持科学计数法，例如 `-1.012205E-08`

模块校验对兼容类型较宽松：

- 未识别的模块类型通常会给 warning，不一定直接报 error
- 未知项目根字段也会给 warning，便于兼容历史数据

## 工具行为说明

### `create_block` / `append_block` / `insert_block_child` 是结构级工具

这些工具只负责生成或拼接 block 结构，不知道它最终会挂到哪个对象上。

因此它们：

- 会检查 block define 是否存在
- 会按 block 元数据生成参数/分支外形
- 不会在此阶段检查 owner type
- 不会在此阶段检查项目白名单或 end-user mode

真正的上下文约束发生在：

- `add_fragment`
- `update_myblock_fragment`
- `validate_workspace`

### 编辑工具返回的是“更新后的完整 JSON”

除 `save_workspace_file` 外，大多数编辑工具都不会直接修改磁盘文件，而是返回一个新的 `workspace_data`。

推荐流程：

1. `load_workspace_file`
2. 通过编辑工具得到新的 `workspace_data`
3. `validate_workspace`
4. `save_workspace_file`

### 保存会重排 JSON 格式

`save_workspace_file` 使用的是标准 `json.dump(..., ensure_ascii=False, indent=2)`。

这意味着：

- 会重写缩进和换行
- 不保证保留原文件的数组单行/多行格式
- 不保证保留手工整理过的视觉格式

如果你有“短数组一行显示”之类的格式诉求，需要额外的格式化步骤；这不是 `save_workspace_file` 的当前职责。

## 已知限制

下面这些限制是当前实现下真实存在的，README 明确写出来，避免误用：

### 1. 不做运行时语义验证

当前 MCP 能校验结构、对象类型和项目策略，但不能判断：

- 事件链在运行时是否会卡住
- 广播/接收时序是否合理
- 镜头切换是否“演出正确”
- 对话是否自然
- 某个流程是否符合剧情预期

也就是说：

- `validate_workspace` 通过，不代表运行效果一定正确

### 2. 不做完整引用解析

当前不会系统验证以下内容是否在运行时真实可解析：

- `RunToTargetAndWait` / `TurnToTargetInSecs` 这类 block 参数中的目标对象名是否存在
- 广播消息名是否一定有接收者
- `PlayDialogueGroup` 的组名是否一定在所有上下文中可达
- 相机预设名是否一定可用
- 对话里的 `who` 是否对应场景里真实且可见的角色
- `audio` 名称是否一定存在于资源系统
- 资源 ID 与场景资源是否一一匹配

这些目前更多依赖上层工程约束和实际运行检查。

### 3. 删除操作不自动修复依赖

例如：

- 删除 MyBlock，不会自动删除调用点
- 删除 fragment，不会自动重接事件流

这些属于“结构编辑”，不是“语义修复”。

### 4. 单独传裸 `BlockScript` 会失去上下文

如果你只把一个 `BlockScript` 传给 MCP：

- 可以做结构编辑
- 但无法完整触发 owner type 限制
- 也无法执行完整项目模式限制

真实工程编辑请优先传完整 `.ws`。

## 能力边界矩阵

这一节专门回答一个常见问题：

- `hetu_mcp` 现在到底能不能“完整生成一个 .ws”？
- 能不能“完整校验一个 .ws”？
- 是否已经覆盖“每个参数、每层嵌套、每个引用”的合法性？

结论先写在前面：

- 完整 `.ws` 的结构级校验：`已支持`
- 完整 `.ws` 的保存落盘：`已支持`
- 基于现有工程做完整增量修改：`已支持`
- 从空白状态开始，仅靠 MCP 工具完整搭建一个可运行 `.ws`：`部分支持`
- 对 block 嵌套结构做递归合法性校验：`已支持`
- 对每个参数做严格语义校验：`部分支持`
- 对工程内引用关系做完整解析校验：`未完全支持`
- 对剧情/镜头/广播时序做运行时正确性验证：`未支持`

### 1. 生成能力矩阵

| 能力 | 当前状态 | 说明 |
| --- | --- | --- |
| 读取现有 `.ws` | 已支持 | `load_workspace_file` 可直接加载完整工程 |
| 保存完整 `.ws` | 已支持 | `save_workspace_file` 默认会先校验再把完整 JSON 保存回 `.ws` |
| 基于现有 `.ws` 增量编辑 | 已支持 | 可修改 fragments、MyBlock、block 链和部分结构 |
| 创建单个 block | 已支持 | `create_block` 支持按 block define 生成结构 |
| 创建 MyBlock 定义/调用 | 已支持 | 支持定义、更新实现、生成调用 block |
| 从空白创建完整项目根 | 未直接支持 | 没有 `create_workspace` / `init_workspace` 之类工具 |
| 从空白创建完整场景模块树 | 未直接支持 | 没有 `create_module` / `create_scene_object` 工具 |
| 从空白创建对白系统 | 未直接支持 | 没有 `create_dialogue_group` 级别工具 |
| 从空白创建 `editorScene` 相机配置 | 未直接支持 | 可手动构造 JSON，但没有专门 MCP 工具 |
| 从空白绑定资源/资源 ID | 未直接支持 | 可手写 JSON，但 MCP 不提供资源管理抽象 |

这意味着：

- 如果你已经有一个完整 `.ws`，`hetu_mcp` 很适合做“读 -> 改 -> 校验 -> 存”
- 如果你只有一个想法，想完全靠 MCP 从零搭出一个复杂项目，目前还不够顺手
- 真要从零生成，现阶段通常还是“先准备完整 JSON 模板，再用 MCP 校验和修补”

### 2. 校验能力矩阵

| 校验层级 | 当前状态 | 说明 |
| --- | --- | --- |
| 项目根结构校验 | 已支持 | `name/type/version/scene/res/dialogues/editorScene/...` |
| 模块结构校验 | 已支持 | 模块 `type/id/props/children/props2` |
| `BlockScript` 结构校验 | 已支持 | `fragments/myblocks/uiState` 等上下文遍历 |
| fragment 结构校验 | 已支持 | `pos/head` 是否存在、head 是否是合法 block |
| block 结构校验 | 已支持 | `define/sections/children/child/next` |
| 嵌套 block 递归校验 | 已支持 | 递归覆盖参数嵌套、branch child、`next` |
| MyBlock 定义完整性校验 | 已支持 | 名称、displayName、fragment、head 绑定 |
| 场景元素 owner type 限制 | 已支持 | 按 `SpriteAPI.IsTargetBlock()` 规则 |
| end-user mode 项目策略 | 已支持 | `showmyblock` / `whitelist` / hidden category |
| 模块属性类型校验 | 已支持 | `string/integer/float/vector/quaternion/...` |
| 对话结构校验 | 已支持 | `DialogueGroups/items/who/content/audio/autoDelay` |
| `editorScene` 相机结构校验 | 已支持 | `position/rotation/fov` |
| 科学计数法数值兼容 | 已支持 | 支持如 `-1.012205E-08` |
| block 参数个数精确校验 | 部分支持 | 结构可用，但不是所有 block 都做严格参数个数/缺省约束 |
| block 参数类型精确校验 | 部分支持 | 不是每个参数都校验“必须数字/必须布尔/必须枚举” |
| 参数取值范围校验 | 未支持 | 例如数值上下限、字符串枚举值全集 |
| 对象名/相机名/对白组名引用校验 | 部分支持 | 个别结构可间接发现，未做统一引用解析 |
| 广播消息收发闭环校验 | 未支持 | 不检查“是否一定有接收者” |
| 运行时流程校验 | 未支持 | 不模拟执行顺序、等待、死锁、镜头演出 |

### 3. “完整 `.ws` 校验”到底已经覆盖到什么程度

如果传入的是完整项目根对象，`validate_workspace` 现在会做这几层：

#### 项目根

- 基础字段类型：`name`、`desc`、`icon`、`author`
- 数值字段类型：`created`、`modified`、`type`、`version`、`stageType`、`projectMode`
- 根模块存在性与类型：`scene`、`agents`、`assets`
- `res` 是否为整数列表，且资源 ID 是否存在于资源简表
- `showmyblock` 是否为布尔值
- `operationUIs`、`dialogues`、`editorScene`、`sceneData` 的结构是否正确

#### 模块树

- 每个模块是否有合法 `type`
- `id` 是否存在且非空
- `props` 是否是对象
- `props` 中已知字段是否匹配声明类型
- `props2` 自定义属性是否匹配 `Simple/SimpleList/Vector3/Quaternion/...`
- `children` 是否为列表，子模块是否递归合法

已知字段会按 Hetu 运行时实际读取方式做 JSON 类型校验：

- `string` 必须是字符串
- `boolean` 必须是布尔值
- `integer` 必须是 JSON 整数，不能用字符串数字替代
- `float` 必须是数字字符串，例如 `"1"`、`"-1.012205E-08"`
- `vector2` / `vector3` / `quaternion` 必须分别是 2/3/4 项数字字符串数组
- `color` 和 `object_ref` 必须是字符串
- `simple` 必须是基础标量，`simple_list` 必须是基础标量列表

#### BlockScript / fragment / MyBlock

- 每个 `fragment.pos` / `fragment.head` 是否存在
- `fragment.pos` 是否为 2 项数字字符串数组
- `uiState.pos` / `uiState.scroll` 是否为 2 项数字字符串数组
- `uiState.scale` 是否为数字字符串
- `head` 是否是合法 block
- block 嵌套结构是否递归合法
- block 参数/列载荷是否匹配运行时形状：`type=var` 的 `val` 必须是字符串，`type=block` 的 `val` / `value` 必须是对象
- MyBlock 是否有合法 `name` / `displayName` / `wrapBlockName` / `yield`
- MyBlock `columns[].type` / `columns[].data` 是否符合运行时定义形状
- MyBlock `fragment.head.define` 是否与 MyBlock 自身名字一致
- MyBlock 调用是否引用了已声明的 MyBlock

#### 工程上下文规则

- 该场景元素类型是否允许使用当前 block
- 当前项目若是 end-user mode，是否违反：
  - `magic` / `experiment` 类禁用
  - `whitelist`
  - `showmyblock=false`
  - `displayName` 以 `#` 开头的隐藏 myblock

所以从“结构正确性”和“规则约束正确性”来说，`validate_workspace` 已经是完整工程级的，不只是单个 block 校验。

### 4. “每个参数是否合法”目前到了什么层级

这里最容易误解。`hetu_mcp` 现在对“参数”其实分成两层：

#### 第一层：结构级参数合法性

这一层是支持的。

已经覆盖的内容：

- `params` 必须是列表
- `columns` 必须是列表
- `params[i]` / `columns[i]` 必须是对象
- `params[i].type` / `columns[i].type` 如果存在，必须是字符串
- `type=var` 时 `val` 必须是字符串
- `type=block` 时 `val` 或 `value` 必须是嵌套 block 对象
- `name` 必须是字符串，`customPopup` 必须是整数
- 如果参数位里嵌了 block，会继续递归校验这个 block 本身是否合法
- `children`、`child`、`next` 里的嵌套 block 也会继续递归校验

也就是说，像这种结构：

- `If` 的条件参数里再嵌一个 operator block
- `SetVar` 的值里再嵌一个算术 block
- `BroadcastMessageAndWait` 后面再接 `next`

这些嵌套形态都会被递归检查。

#### 第二层：语义级参数合法性

这一层目前只做了部分。

当前没有统一严格覆盖的业务语义包括：

- 某个 block 的参数个数是否“刚好匹配定义”
- 某个参数值在业务上是否必须代表 number / boolean / string / enum
- 枚举值是否一定在允许选项中
- 数值是否在运行时允许范围内
- 某个 target 名字是否一定对应工程里的真实对象
- 某个相机 preset 名是否一定存在于 `editorScene`
- 某个 dialogue group 名是否一定存在于 `dialogues`

所以更准确地说：

- `hetu_mcp` 现在擅长做“结构级 + 上下文规则级”校验
- 还没有做到“所有参数都按业务语义逐项强约束”

### 5. 嵌套 block 校验已经覆盖到哪里

这部分当前是比较完整的。

`block` 的递归校验现在会向下遍历：

- `sections[].params[].val`
- `sections[].columns[].value`
- `sections[].children[]`
- `sections[].child`
- `next`

同时，`workspace` 级校验会把这套递归应用到：

- 普通 fragment 的 `head`
- MyBlock fragment 的 `head`
- 白名单里的 block 定义

所以“嵌套使用及其合法性验证”如果指的是：

- 嵌套 block 结构是否正确
- 嵌套 block define 是否合法
- 嵌套 block 是否违反 owner type
- 嵌套 block 是否违反项目模式限制

这些目前都已经支持。

### 6. 目前尚未统一覆盖的“引用关系”校验

下面这些经常是用户以为 `validate_workspace` 会做，但实际上当前还没有统一做完的：

#### 对象引用

- `GotoTarget("角色A")` 里的 `"角色A"` 是否真的存在
- `TurnToTargetInSecs("百灵")` 是否能在场景里解析到对象
- `CameraFollow("队长")` 是否跟随的是有效对象

#### 名称引用

- `PlayDialogueGroup("夺回龙蛋18")` 是否一定有对应对白组
- `TransitToCameraPreset("龙蛋全景1")` 是否一定有对应相机预设
- `BroadcastMessage("跑向出口")` 是否一定至少有一个接收脚本

#### 资源引用

- `audio` 是否对应真实音频
- `res` 列表与实际资源使用是否完全一致

已支持的资源校验：

- `validate_workspace` 会校验项目根 `res` 列表中的 ID 是否存在于资源简表
- `validate_resource` 可校验单个资源 ID、资源类型和 entry 分类组合是否合法
- `get_resource` / `find_resources` 可查询完整资源索引

这些不是当前架构做不到，而是目前还没有实现“统一引用解析层”。

### 7. 运行时正确性目前不在能力范围内

以下问题，当前 `hetu_mcp` 不会也不能直接证明：

- 某段剧情会不会在运行时卡住
- 某个 `PlayDialogueGroup` 是否会因为交互模式而停不下来
- 某个广播链是否存在死路
- 相机切换和角色走位是否在时间轴上协调
- 隐藏后的角色是否还会在视觉上“说话”
- 镜头是否拍对了对象

这类问题本质上属于：

- 运行时模拟
- 演出逻辑验证
- 剧情时序验证

它们超出了当前静态 MCP 校验器的边界。

### 8. 典型问题的最终结论

#### 问：现在是否支持整个 `.ws` 文件的生成？

答：

- `支持把完整 JSON 保存成 .ws`
- `支持基于现有 .ws 做大范围修改`
- `不支持仅靠现有 MCP 工具从空白一步步完整搭出工程的所有层级`

#### 问：现在是否支持整个 `.ws` 文件的校验？

答：

- `支持完整工程级结构校验`
- `支持模块/脚本/MyBlock/对话/editorScene 校验`
- `支持 owner type 和项目模式限制`
- `但不等于支持所有引用和运行时语义校验`

#### 问：是否包含内部每个参数以及嵌套使用及其合法性验证？

答：

- `嵌套使用的结构合法性验证：支持`
- `嵌套 block 的上下文规则验证：支持`
- `每个参数的业务语义级强校验：目前仅部分支持`

### 9. 如何理解当前最适合的使用方式

如果把能力边界说得最直白一点：

- 它已经是一个可靠的 `.ws` 静态编辑器和规则校验器
- 还不是一个完整的项目生成器
- 也还不是一个运行时模拟器

最适合它的场景是：

1. 加载完整 `.ws`
2. 做结构编辑
3. 跑 `validate_workspace`
4. 把剩余的“引用正确性 / 演出正确性 / 流程正确性”交给人工复核或真实运行验证

## 安装

```powershell
cd HetuAIGC
python -m pip install -r mcp\hetu_mcp\requirements.txt
```

当前唯一运行依赖：

```text
mcp>=0.9.0
```

## 在 Codex 中注册

```powershell
codex mcp add hetu-mcp -- <PYTHON_EXE> mcp\hetu_mcp\server.py .
```

查看注册结果：

```powershell
codex mcp get hetu-mcp
```

## MCP 配置示例

```json
{
  "mcpServers": {
    "hetu-mcp": {
      "type": "stdio",
      "command": "<PYTHON_EXE>",
      "args": [
        "mcp/hetu_mcp/server.py",
        "."
      ]
    }
  }
}
```

说明：

- 第二个参数是 `workspace_root`
- 相对路径 `.ws` 文件会相对这个根目录解析
- 读取和保存路径都不能逃逸出这个根目录

## 在 Cursor 中注册

建议在仓库根目录创建 `.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "hetu-mcp": {
      "type": "stdio",
      "command": "<PYTHON_EXE>",
      "args": [
        "${workspaceFolder}/mcp/hetu_mcp/server.py",
        "${workspaceFolder}"
      ]
    }
  }
}
```

## 推荐使用流程

### 1. 加载完整工程

```json
{
  "file_path": "reference/smoke/test-api-smoke.ws"
}
```

### 2. 先做查询

常用工具：

- `get_modules`
- `get_fragments`
- `get_myblocks`
- `analyze_workspace_statistics`
- `find_blocks_by_type`

### 3. 再做编辑

例如更新某个 fragment 位置：

```json
{
  "workspace_data": { "...": "workspace json" },
  "script_id": "dd99a91dd54b4fb7a8cc8ea09e561155",
  "fragment_index": 0,
  "position": ["999", "888"]
}
```

例如创建 block：

```json
{
  "block_define": "MoveSteps",
  "parameters": {
    "steps": "42"
  }
}
```

### 4. 在保存前做完整校验

```json
{
  "workspace_data": { "...": "updated workspace json" }
}
```

对应工具：

- `validate_workspace`

### 5. 最后保存

```json
{
  "file_path": "output/example.ws",
  "content": { "...": "validated workspace json" },
  "create_backup": true
}
```

## 本地验证

运行 smoke test：

```powershell
python mcp\hetu_mcp\utils\smoke_test.py
```

当前测试覆盖重点包括：

- 29 个公开 MCP 工具的基础可用性
- 资源查询、资源校验和 `workspace.res` 资源 ID 校验
- 多脚本工作区 `script_id` 行为
- MyBlock 创建/更新/调用/删除
- 模块 `props` / `props2` 运行时字段类型矩阵
- BlockScript `fragment.pos` / `uiState` 运行时形状校验
- block 参数载荷和 MyBlock 定义形状校验
- `save_workspace_file` 默认保存前校验拒绝坏数据
- 对象类型可用 Block 限制
- end-user mode 下的 `whitelist` / `showmyblock` 限制
- 科学计数法 quaternion 校验
- Smoke checks MCP internal Block/module metadata snapshots.

## 附带脚本与文档

### 参考工程导出脚本

`utils/export_reference_report.py` 会通过当前 MCP 服务分析 `reference` 下的工程，并生成：

- `output/REFERENCE_WS_MCP_REPORT.md`
- `output/REFERENCE_WS_SCREENPLAY.md`

运行方式：

```powershell
python mcp\hetu_mcp\utils\export_reference_report.py
```

### 资源列表导出脚本

`utils/export_resource_list.py` 会拉取 Pangu3D 资源列表接口，并生成：

- `mcp/hetu_mcp/resource/resouce_summary.json`
- `mcp/hetu_mcp/resource/resource_index.json`
- `mcp/hetu_mcp/resource/README.md`
- `mcp/hetu_mcp/definitions/resource_definitions.py`

如果已有 `sprite_3d.json` 和 `vfx.json`，脚本会在重写 `resource_index.json` 后按 `resource_id` 把已解析的 Sprite3D/Role/VFX 字段回写到最新索引。MCP server 初始化时会检查 `resouce_summary.json` 和 `resource_index.json`。如果任一文件缺失，会调用该导出脚本拉取接口，并在 `mcp/hetu_mcp/resource/` 内重新生成资源数据。

运行方式：

```powershell
python mcp\hetu_mcp\utils\export_resource_list.py --insecure
```

### Sprite3D / Role / VFX 元数据更新脚本

`utils/export_sprite3d_vfx_metadata.py` 会在资源列表更新之后，处理 Sprite3D、Role 和 VFX 的 `.ab` 文件，并生成或差量更新：

- `mcp/hetu_mcp/resource/sprite_3d.json`
- `mcp/hetu_mcp/resource/vfx.json`
- `mcp/hetu_mcp/resource/resource_index.json` 中对应资源的解析字段

默认 `.ab` 缓存在 `mcp/temp/`，该目录只作为运行缓存，可随时清空。最终 JSON 文件保存在 `mcp/hetu_mcp/resource/`，不会因为清空缓存丢失。

Role 资源属于 3D `.ab` 资源，和 Sprite3D 使用同一套 AssetBundle 解析逻辑。脚本会把 Sprite3D 与 Role 合并写入 `Sprite3D_manifest.tsv` 交给 Unity 解析，最终都按 `resource_id` 差量写入 `sprite_3d.json`；不会为 Role 生成单独的 JSON 文件。

Sprite3D/Role 写入字段：

- `resource_id`
- `rootRotation`
- `rootScale`
- `animations`
- `center`
- `size`
- `bodyType`
- `direction`

VFX 写入字段：

- `resource_id`
- `resource_name`
- `isLoop`
- `vfxTime`

运行方式：

```powershell
python mcp\hetu_mcp\utils\export_sprite3d_vfx_metadata.py --insecure --unity-project C:\Project\hetao\trunk\Creation\builder --unity-exe "E:\Unity\engine\Unity 2021.3.28f1c1\Editor\Unity.exe"
```

注意：

- 脚本会调用 `AssetBundle.SetAssetBundleDecryptKey("0123456789abcdef")`。
- `sprite_3d.json` 和 `vfx.json` 采用差量更新：本次未解析到的旧记录保留，同 `resource_id` 记录更新，新 `resource_id` 追加。
- 如果目标 Unity 工程已被桌面 Unity 打开，batchmode 不能再次打开同一工程；需要先关闭该工程，或通过已连接的 Unity MCP 实例执行解析逻辑。
- `export_resource_list.py` 只刷新接口资源索引并回写已有解析字段；`export_sprite3d_vfx_metadata.py` 才会下载 `.ab` 并重新解析 Sprite3D/Role/VFX 元数据。

### 场景元素支持矩阵

MCP 运行时使用的场景元素目标类型映射集中定义在 `definitions/workspace_schema.py`。

如果你要确认“某种场景元素到底允许哪些代码块”，请直接看：

- Runtime support table: `mcp/hetu_mcp/definitions/workspace_schema.py`

## 当前建议

如果你的目标是“尽量不破坏原工程规则地修改 `.ws`”，最佳实践是：

1. 始终加载完整 `.ws`
2. 所有修改后先跑 `validate_workspace`
3. 对剧情、镜头、广播时序等运行效果，仍然需要人工复核或实际运行验证

这也是当前 `hetu_mcp` 的设计边界：它已经覆盖了大部分结构和规则层约束，但还不是一个运行时模拟器。
