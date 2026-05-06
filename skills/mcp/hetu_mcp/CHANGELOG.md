# 更新日志

## 0.0.3

完善 Pangu3D 资源元数据导出，并强化 `.ws` 保存与运行时校验。

- 新增 Sprite3D/Role/VFX `.ab` 下载、解密和解析流程，统一缓存到 `mcp/temp/`，并生成或更新 `sprite_3d.json`、`vfx.json` 与 `resource_index.json`。
- Sprite3D 与 Role 共用 3D 资产解析和差量更新逻辑，提取根对象变换、MeshPartSettings 动画与包围信息；VFX 提取 `isLoop` 和 `vfxTime`。
- `export_resource_list.py` 会保留并回写已有 Sprite3D/Role/VFX 解析字段，并在资源 README 中列出新增元数据文件。
- `save_workspace_file` 默认保存前执行 `validate_workspace`，校验失败拒绝落盘，可通过 `validate_before_save=false` 显式跳过。
- 强化模块 `props` / `props2`、BlockScript 形状、block 参数载荷和 MyBlock 定义形状等运行时类型校验，提前暴露反序列化风险。
- 扩展 `utils/smoke_test.py`，覆盖资源元数据、运行时字段类型和保存前校验回归用例。

## 0.0.2

新增 Hetu 资源管理能力，并将 MCP 运行时整理为更自包含的结构。

- 新增 `utils/export_resource_list.py`，用于拉取和解析资源数据，并生成 `resource/resouce_summary.json`、`resource/resource_index.json` 和 `definitions/resource_definitions.py`。
- 新增资源查询/校验 MCP 工具，并在 workspace 校验中支持资源 ID 校验；资源文件缺失时支持初始化自动生成。
- 将 `defines/` 重命名为 `definitions/`，并同步更新引用、生成路径和文档说明。
- 拆分 workspace 辅助逻辑：结构/只读规则放到 `definitions/workspace_schema.py`，写入辅助放到 `handlers/workspace_operations.py`。
- 将场景元素目标类型支持表集成到 `workspace_schema.py`，校验时结合元素目标类型和 block 定义中的 `object_types`。
- 新增 `definitions/script_definition_data.py` 作为 MCP 内部 Block/workspace 元数据快照，运行时不再依赖 `mcp/hetu_mcp` 外部文件。
- 扩展 smoke test 覆盖，包括资源能力、场景元素校验、内部元数据加载和 workspace 校验。

## 0.0.1

- `.ws` 文件读取和保存。
- BlockScript fragment 列表查询、添加、删除和位置更新。
- Block 创建、参数修改、追加操作和子 Block 插入。
- MyBlock 创建、更新、删除、调用 Block 生成和使用位置查询。
- 序列化模块查询、模块校验和模块文档生成。
- Block 结构校验、Block 文档生成和 Block 查询。
- Workspace 结构校验、场景元素 owner 类型限制、项目策略限制和 MyBlock 规则校验。
- Workspace 统计分析和参考 workspace 报告导出。
