# MCP 实测契约与盲区（2026-04-23 实测更新）

> **触发条件**：首次用 MCP 改一个新关卡时、遇到 MCP 报错搞不清楚原因时读本文件。
> 日常增量改造参考 `level-new/agents/creator_agent.md §MCP 函数式 API 规则`。

本节基于 2026-04-23 对参考包 `S低L14-1-3-练习19`（94KB / 18 场景子节点 / 13 BlockScript / 60 fragments / 579 积木实例）的 MCP 全链路实测，记录工具对照表和已知冲突**没覆盖到的隐藏契约**和**架构级瓶颈**。完整实测报告见 `output/_mcp_test_rebuild/mcp_capability_report.md`。

## (1) 隐藏契约（tool description 没写，但不写会 FAIL）

| 场景 | 契约 | 不写的报错 |
|---|---|---|
| `add_fragment` 的 fragment 对象 | 必须含 `pos: ["x", "y"]`（画布坐标，字符串数组）| `Fragment must have 'pos' field` |
| 合法空白 ws 的顶层字段 | `showmyblock` 必须 `boolean`（**不是 dict**）；`dialogues` 必须 `dict`（**不是 list**）；`res` 必须 `list[int]`；`agents`/`assets` 必须是含 `type:"Folder"` 的节点 | `must be a serialized module object` / `must be a list of integers` / `must be a boolean` |
| 错误返回格式 | MCP 目前 3 种格式并存：JSON 对象 / 裸字符串 / Python 异常 | agent 要对每个 tool 单独写错误解析 |

**起步模板参考**：想从零开始构建合法空白 ws 时，直接抄 `output/_mcp_test_rebuild/v0_empty.ws`（已 `validate_workspace` PASS 认证）。

## (2) 大 workspace_data 搬运瓶颈（架构级）

MCP 所有 edit/query tool（除 `load_workspace_file` / `save_workspace_file`）都要求 `workspace_data` 作为完整 JSON 对象参数。在 Cursor agent 里调用 MCP 时：

- Agent 必须在 `CallMcpTool` 的 `arguments` 字段**手写**完整 ws JSON
- `load_workspace_file` 返回的大 data 会被 Cursor 写到 agent-tools 临时文件，agent **无法自动"引用"** 上次返回，只能手工 copy 过来

**实测边界**：

| ws 规模 | agent 手拼 arguments | 可用性 |
|---|---|---|
| 空白模板（~1KB / ~50 行）| 轻松 | ✅ |
| 中等骨架（~60KB / 1600+ 行）| 极度吃力 | ⚠️ 能做但不推荐 |
| 原包规模（94KB / 11270 行 JSON）| 拼不出 | ❌ 不可行 |

**规避策略（按首选顺序）**：

1. **增量改优先于从零造**：原 ws 已存在时，`load_workspace_file` 后**小改几处**再 save。不要"从空白 ws 重建"。
2. **每一步接住返回值**：`add_fragment` / `modify_block_parameter` 连续调用时，上一次的 data 返回对象就是下一次的入参。**见本文冲突 5 的函数式模板**。
3. **按 BlockScript 分批处理**：关卡 >50KB 时，先从原包 load 完整 data，但每次只操作一个 BlockScript 子树的内容，不要在 agent 对话里反复粘贴完整 data。
4. **退化为 Python 直接操作**：ws 实在太大时，agent 写 Python 脚本用标准 `json` 模块直接读写（本质等于绕过 MCP，丢失校验能力，但能干活）。

> ⚠️ **已收敛（v0.0.3，2026-05-06）**：`modify_block_parameter` 传入 JSON Array 属于**非法操作**。v0.0.3 通过 `_ensure_block_param_value()` 统一拦截——凡是 `list` 类型一律 `raise ValueError`，错误信息明确指出：数组只能写入 `props2 SimpleList.value` 或 `res` 等 workspace 字段，**不能写入积木 `params`**。`build_param_value_entry()` 作为统一入口被 `create_block` 和 `create_myblock_call` 共用，确保所有参数构建路径都经过同一道类型守门。根本约束见 `_knowledge/blocks_reference.md §0` 常错陷阱表。

## (3) 已确认盲区清单（补充 §0.10.c 对照表）

**下列操作 MCP 当前都没有 tool，不要浪费时间找**，直接走 agent Python 方案：

| 盲区类别 | 具体操作 | agent 的 Python 方案 |
|---|---|---|
| **场景树节点创建** | 创建 Scene / Folder / MeshPart / Effect / ImageSet / Picture / Music / Sound / Character / **BlockScript 节点**（注意：BlockScript 节点 ≠ BlockScript 内的 fragment）| 手搓 JSON，参考原包结构 |
| **场景树 props 修改** | Position / Scale / Rotation / AssetId / Visible / Size | `scripts/scene_utils.py` |
| **包操作** | zip 解压 / zip 打包 / `solution.json` / `export_info.json` / `icon.png` | `scripts/pkg_utils.py` |
| **参数槽对照校验** | 对照 `scripts/params_registry.json` 查每个积木参数位数 | `scripts/verify_blocks.py`（硬闸门 ①）|
| **禁用 next 校验** | 检查 `block.next` 错误连接 | `scripts/verify_no_new_next.py`（硬闸门 ②）|
| **业务规则校验** | 动画名白名单 / 摄像机反向 / Effect.Visible / AssetId 真实性 等 | 靠 agent + `_shared/constraints.md` 自觉守 |
| **资源查询** | AssetId 搜索 / 角色动画查询 / 推荐主角 | 查 `_knowledge/asset_catalog.md` / `_knowledge/resource_index.jsonl` / `_knowledge/animation_dict.md`（由资源搜索员执行） |
| **空白 ws 模板生成** | 产出一个合法的最小 ws | 直接复用 `output/_mcp_test_rebuild/v0_empty.ws` |

> **MCP 官方 README 对齐**：上述盲区清单中"从空白创建项目根 / 场景模块树 / 对白 / `editorScene` 相机配置 / 资源绑定"这 5 项，在 `mcp/hetu_mcp/README.md` 第 1 节"生成能力矩阵"里 MCP 团队已明确标为**"未直接支持"**，与本节实测一致。该 README 的"能力边界矩阵"整节是本节盲区清单的**官方权威来源**。

> 特别提醒：**"创建 BlockScript 节点"**（作为场景树的一个 node）和 **"往 BlockScript 里 add_fragment"** 是两件事。前者 MCP 不管（属场景树盲区），后者是 MCP 主场。

## (4) 从空白全重建一个复杂关卡 —— 不推荐路径

实测证实"从 0 用 MCP 构建 94KB 关卡"在 Cursor agent 模式下**不可行**：

- 18 个场景子节点：100% agent 手搓，MCP 零命中
- 13 个 BlockScript 节点（节点本身，不是 fragment）：100% agent 手搓
- 13 个 BlockScript 的 fragments / myblocks：MCP 能处理，但每次调用都要搬完整 data → 中途卡在 (2) 的瓶颈
- 约 580 个积木实例：即使 (2) 的瓶颈解决，也要 ~580 次 `CallMcpTool`，context 开销不可接受

**推荐路径**：找最近的**参考母本**（`参考-extracted/`）→ `pkg_utils.extract` → `load_workspace_file` → **增量改** → `save_workspace_file(create_backup=False)` → `pack_zip_clean`。这条路径 MCP 能发挥最大价值。

## (6) 已知冲突与解决（从 SKILL.md §0.10.e 迁入，2026-04-23）

**冲突 1 — 路径沙箱**：MCP server 只允许访问 workspace root 内的文件（`C:\...\AppData\Local\Temp\...` 会被拒）。
→ 统一解压到仓库内中转目录 `output/new/<name>_workdir/` 或 `output/modify/<name>_v{N}_workdir/`。`scripts/pkg_utils.py::extract_zip_into(zip_path, dest_dir)` 已封装，**禁用 AppData / Temp**。

**冲突 2 — 场景树无工具**：MCP 粒度只到 BlockScript 内部；**场景树节点**（Character / MeshPart / Effect / Folder）MCP 不管。
→ `scripts/scene_utils.py` 封装：`attach_effect` / `set_character_position`（单位米）/ `set_character_scale` / `duplicate_character` / `hide_node` / `show_node` / `find_node`。改场景树统一调此模块，**不要直接操作 JSON children**。

**冲突 3 — 打包胶水**：MCP 不处理 zip / solution.json / export_info.json / icon.png。
→ `scripts/pkg_utils.py` 封装：`extract_zip_into` / `write_pkg_metadata` / `pack_zip_clean`（自动清 `.bak`）。端到端流程：`pkg_utils.extract → MCP 改 → scene_utils 改 → pkg_utils.pack_zip_clean`。**禁止 agent 自己写 shutil/zipfile 胶水**。

**冲突 4 — 两套参数注册表**：MCP `block_models.py` 和 `scripts/params_registry.json` 互相独立，可能互相误报。
→ 交付前**双校验**（硬闸门 gate1 + gate3，任一 FAIL 不许交付）。

**冲突 5 — 函数式 API**：MCP 所有"改"型工具都**返回新数据对象**，**不原地改**传进去的对象。

```python
data = result["data"]                              # 初始 data
data = add_fragment(data, frag_a)                  # 每步都接住返回值
data = modify_block_parameter(data, ...)
save_workspace_file(path, data, create_backup=False)
```
最常见事故："改了 5 次只存了第 1 次" —— 某步没接住返回值，后续还在用旧 `data`。**每次调用必须覆盖 data**。

**冲突 6 — MCP 不校验业务规则**：MCP 只查**协议层**，不查业务。MCP 不检查：① AssetId 是否真实存在；② 动画名对该角色是否注册；③ Effect.Visible 缺失导致隐身；④ Position 写成厘米导致飞出场景；⑤ 角色动画混用。**MCP 绿灯 ≠ 关卡能跑对。**

**冲突 7 — 备份文件污染 zip**：`save_workspace_file` 默认 `create_backup=True` 产 `.backup_<ts>.ws`，不清理会混入 zip。
→ ① 每次显式传 `create_backup=False`；② `pack_zip_clean` 打 zip 前自动清理。

**冲突 8 — 术语对不上**：MCP 英文术语和 skill 中文术语不对应，agent 容易找错工具。
→ 写脚本前先查 `_knowledge/mcp_skill_glossary.md`（中英对照 + 字段键名）。

---

## (5) 未来改造方向

实测报告（`output/_mcp_test_rebuild/mcp_capability_report.md`）核心建议：

1. **P0（必做）**：给 9 个 edit tool 加 `file_path` 参数（MCP 内部读文件→改→写回），彻底解 (2) 的搬运瓶颈——**没做这个加任何新 tool 都白搭**
2. **P1**：交付闸门合流 `validate_level_package(zip_path, baseline_zip?)`（吃掉外部 `verify_blocks.py` + `verify_no_new_next.py`）
3. **P1**：场景树节点 CRUD（填 (3) 的头一格盲区）
4. **P1**：包操作（填 (3) 的第三格盲区）
