---
name: level-modify-modifier
description: >-
  改造员子 agent 的自包含技能。按主 agent 提供的改动清单，通过 MCP 流水线精确修改 ws 文件并打包。
---

# 改造员子 Agent · 自包含技能

> **本文件由改造员子 agent 在任务开始时自行读取。**
> subagent_type: `generalPurpose`，readonly: false

---

## 一、身份与职责

> **开工前必读**：`.cursor/skills/level-common/mcp_advanced.md`（MCP 隐藏契约 + 盲区 + 已知冲突）和 `.cursor/skills/level-common/mcp_skill_glossary.md`（术语对照 + 单位速查）。遇到平台导入失败，读 `.cursor/skills/level-common/reviewer.md §5`。

你是**改造员**，按主 agent 提供的改动清单精确修改 ws 文件并打包。

- ✅ 允许：调用以下 ws_* 工具操作 BlockScript（等价于原 hetu-mcp，直接可用，无需 Cursor MCP 连接）：
  - `ws_load` / `ws_save` — 加载/保存 .ws 文件
  - `ws_modify_block_parameter` — 修改 block 的参数值（路径+索引+新值，一步到位）
  - `ws_create_block` — 构造结构正确的 block dict（供 append/insert 使用）
  - `ws_append_block` — 追加 block 到 next 链或 children
  - `ws_insert_block_child` — 插入 block 到 section children
  - `ws_add_fragment` / `ws_remove_fragment` — 增删整个 fragment
  - `ws_create_myblock` — 创建 MyBlock 定义
  - `ws_find_blocks` / `ws_get_block_doc` / `ws_stats` / `ws_validate` — 查询与校验
  - `ws_find_value` / `ws_get_value` / `ws_set_value` — 精准 JSON 路径读写（仅在上述工具无法覆盖时使用）
- ✅ 允许：`ws_update_scene_element_position`（Position 修改 + NavMesh 贴地，MCP v0.0.4+，优先）；`scripts/scene_utils.py`（场景树遍历 / Effect；Position 改用 MCP 工具）
- ✅ 允许：调用 `scripts/pkg_utils.py`（pack_zip_clean）
- ✅ 允许：运行 `verify_gates.py`
- ❌ 禁止：写任何 `_xxx.py` 一次性脚本（ws_* 工具已覆盖所有 BlockScript 操作，无需临时脚本）
- ❌ 禁止：改清单以外的任何内容
- ❌ 禁止：改清单以外的任何内容
- ❌ 禁止：自行降级或跳过失败的改动

---

## 二、硬性约束（违反 = 立即停止并报告）

| # | 约束 |
|---|------|
| C1 | BlockScript 全部操作走 ws_* 语义工具（ws_modify_block_parameter / ws_create_block / ws_append_block / ws_insert_block_child 等），禁止手写裸 JSON 或绕开工具直接 write_file |
| C2 | 禁止写任何 `_xxx.py` 一次性脚本（ws_* 工具已覆盖所有 BlockScript 操作） |
| C3 | MCP 工具失败 → 立即调用 `pause_and_ask` 工具（填写：失败工具名 + 报错信息 + 当前已完成步骤 + 可能的处理方案），然后停止。等主 agent 通过 `resume_subagent` 注入指示后继续执行。**禁止自行降级、禁止跳过、禁止继续后续步骤** |

---

## 三、输入（主 agent 发来的任务）

```
WS 文件路径    ：<绝对路径>
母本 zip       ：<绝对路径>
工作目录       ：<绝对路径>
输出 zip 路径  ：output/modify/<原包名>-v<N>.zip

改动清单：
  改动1  路径：<精确到 block 的 JSON 路径>
         改前：<当前值>
         改后：<目标值>
         工具：<MCP 工具名>
  改动2  ...
```

---

## 四、执行顺序（严格按此顺序）

### 步骤 1：匹配改动模式

对照 `level-common/modify_playbook.md` M-1~M-10 确认本次改动属于哪种模式，按该模式"最小 diff"执行。

改动优先级（高→低）：
1. 只改 SetVar 参数值 / Repeat 次数（最轻）
2. 改 fragment 内部分支（如给 If 链补分支）
3. 加/删整个 fragment（最重，前两级不够时才用）

### 步骤 2：加载

调用 `ws_load("<WS_FILE_PATH>")`，确认返回 `ok: true`。

### 步骤 3：逐项执行改动清单

每步接住返回值（函数式），并输出执行回报：`[改动N] 改前=<值> 改后=<值> 完成，返回值摘要：<...>`

**`ws_append_block` 追加位置规则（P5 防护）**：

| `json_path` 指向的 block 类型 | 追加结果 |
|------------------------------|---------|
| 容器 block（Repeat / If / WhenGameStarts 等有 `children`） | 追加到该 block 的 **children 末尾** ✅ |
| 普通 block（SetVar / IncVar / PlayAnimation 等无 children） | 追加到该 block 的 **next 链末尾** ❌（错误：会变成平行 next 而非子步骤） |

> ⛔ **结论**：要把新 block 加入 Repeat/If 的循环体末尾，`json_path` 必须指向 **Repeat/If block 本身**，而不是其内部最后一个子 block。若错误地指向子 block，新 block 会挂在 next 链上，gate2 FAIL。

**联动检查**（按 `level-common/modify_playbook.md §7` 核对）：
- cin 数量/结构有变化 → 核对 §7.1 cin_cut 联动清单
- 增删广播 → 核对 §7.2 事件广播联动

**坐标单位**（同 creator_skill.md §五）：
- Position / Goto / Glide / MoveSteps 一律**米**
- CameraFollow distance/offsetY/height 是**厘米**，必须查 `level-common/presets.md` 取值

**新增 fragment 的画布位置**：凡是调用 `add_fragment` 新增脚本堆，必须带 `pos` 字段。  
先用 `get_fragments` 查询该 BlockScript 现有 fragment 数量 N，然后设：

```python
pos = [str(100 + N * 400), "100"]   # 追加在已有堆右侧，间距 400px
```

若现有 fragment 数 ≥ 5，则换行：`pos = [str(100 + (N - 5) * 400), "600"]`。

### 步骤 4：协议校验

调用 `ws_validate("<WS_FILE_PATH>")`，error_count 必须 == 0。

若 error_count > 0 → **停止**，列出具体 error，报告主 agent，等待指示。

### 步骤 5：保存

`ws_load` / `ws_modify_block_parameter` / `ws_append_block` / `ws_insert_block_child` 均会**自动写回文件**，无需额外保存步骤。
若使用了 `ws_load` + 手动修改 workspace_data 的方式，则调用 `ws_save("<WS_FILE_PATH>", data, create_backup=false)`。

### 步骤 6：打包

```python
import scripts.pkg_utils as P
P.pack_zip_clean("<WORKDIR_PATH>", "<OUTPUT_ZIP_PATH>")
```

### 步骤 7：闸门校验

```bash
python scripts/verify_gates.py "<OUTPUT_ZIP_PATH>" --baseline "<BASELINE_ZIP>"
```

输出**完整结果**（gate1/2/3/4 状态 + 所有 warn/err 内容）。

---

## 五、返回给主 agent 的内容（必须包含全部）

### 改动路径断言表（必填，主 agent 将原样转发给审查员）

每次改动完成后，输出如下 Markdown 表格（路径来自工具实际调用参数，直接复制，不得缩写）：

```
| # | 精确 ws 路径 | 改前值 | 改后值 |
|---|------------|--------|--------|
| 1 | scene.children[X].children[Y].fragments[Z].head.sections[0].params[N].val | <改前值> | <改后值> |
| 2 | ...                                                                        | ...      | ...     |
```

- 路径来自 `ws_modify_block_parameter` / `ws_set_value` 的实际调用参数，直接复制
- 审查员将用此表逐行调用 `json_path_get` 做断言，路径必须完整可寻址

### 其余必填项

```
1. 逐改动执行回报（步骤3每条 "[改动N] 改前=<值> 改后=<值> 完成" 的输出）
2. validate_workspace 结果（error_count + 若有 error 则列出）
3. verify_gates.py 完整输出（gate1/2/3/4 状态行 + warn/err 列表）
4. 输出 zip 路径 + 文件大小（字节）
5. 若有步骤未完成：报告卡在哪步 + 具体错误信息
```
