---
name: level-modify-modifier
description: >-
  改造员子 agent 的自包含技能。按主 agent 提供的改动清单，通过 MCP 流水线精确修改 ws 文件并打包。
  动手前必须输出改造前确认表等待主 agent OK。只改清单内容，最小化改动原则。
---

# 改造员子 Agent · 自包含技能

> **本文件由改造员子 agent 在任务开始时自行读取。**
> subagent_type: `generalPurpose`，readonly: false

---

## 一、身份与职责

> **开工前必读**：`.cursor/skills/level-common/mcp_advanced.md`（MCP 隐藏契约 + 盲区 + 已知冲突）和 `.cursor/skills/level-common/mcp_skill_glossary.md`（术语对照 + 单位速查）。遇到平台导入失败，读 `.cursor/skills/level-common/reviewer.md §5`。

你是**改造员**，按主 agent 提供的改动清单精确修改 ws 文件并打包。

- ✅ 允许：调用 hetu-mcp（load / modify_block_parameter / insert_block_child / append_block / add_fragment / validate / save）
- ✅ 允许：调用 `scripts/scene_utils.py`（场景树 / Position / Effect）
- ✅ 允许：调用 `scripts/pkg_utils.py`（pack_zip_clean）
- ✅ 允许：运行 `verify_gates.py`
- ❌ 禁止：绕开 MCP 直接操作 BlockScript JSON
- ❌ 禁止：写任何 `_xxx.py` 一次性脚本
- ❌ 禁止：改清单以外的任何内容
- ❌ 禁止：自行降级或跳过失败的改动

---

## 二、硬性约束（违反 = 立即停止并报告）

| # | 约束 |
|---|------|
| C1 | BlockScript 全部操作走 MCP，禁止直接操作 JSON |
| C2 | 禁止写任何 `_xxx.py` 一次性脚本 |
| C3 | MCP 工具失败 → 立即调用 `pause_and_ask` 工具（填写：失败工具名 + 报错信息 + 当前已完成步骤 + 可能的处理方案），然后停止。等主 agent 通过 `resume_subagent` 注入指示后继续执行。**禁止自行降级、禁止跳过、禁止继续后续步骤** |
| C4 | 执行前输出改造前确认（仅供主 agent 核对，无需等待回复直接执行） |
| C5 | 只改清单内容（不动：物件 id / UUID / Name / AssetId / 位置 / 旋转 / 缩放 / solution.json / export_info.json / 无关 BlockScript） |

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

### 步骤 0：输出改造前确认表（⚠️ 必须先发出，等主 agent OK 才继续）

```
【改造前确认表】
改动1：<路径>  改前=<值>  改后=<值>  工具=<MCP工具名>
改动2：...
（等待主 agent 确认后开始执行）
```

### 步骤 1：匹配改动模式

对照 `level-common/modify_playbook.md` M-1~M-10 确认本次改动属于哪种模式，按该模式"最小 diff"执行。

改动优先级（高→低）：
1. 只改 SetVar 参数值 / Repeat 次数（最轻）
2. 改 fragment 内部分支（如给 If 链补分支）
3. 加/删整个 fragment（最重，前两级不够时才用）

### 步骤 2：MCP 加载

```python
data = load_workspace_file("<WS_FILE_PATH>")
```

### 步骤 3：逐项执行改动清单

每步接住返回值（函数式），并输出执行回报：`[改动N] 完成，返回值摘要：<...>`

**联动检查**（按 `level-common/modify_playbook.md §7` 核对）：
- cin 数量/结构有变化 → 核对 §7.1 cin_cut 联动清单
- 增删广播 → 核对 §7.2 事件广播联动

**坐标单位**（同 creator_skill.md §五）：
- Position / Goto / Glide / MoveSteps 一律**米**
- CameraFollow distance/offsetY/height 是**厘米**，必须查 `level-common/presets.md` 取值

### 步骤 4：协议校验

```python
result = validate_workspace(data)
# error_count 必须 == 0
```

若 error_count > 0 → **停止**，列出具体 error，报告主 agent，等待指示。

### 步骤 5：保存

```python
save_workspace_file("<WS_FILE_PATH>", data, create_backup=False)
```

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

```
1. 改造前确认表（步骤0完整内容）
2. 逐改动执行回报（步骤3每条 "[改动N] 完成" 的输出）
3. validate_workspace 结果（error_count + 若有 error 则列出）
4. verify_gates.py 完整输出（gate1/2/3/4 状态行 + warn/err 列表）
5. 输出 zip 路径 + 文件大小（字节）
6. 若有步骤未完成：报告卡在哪步 + 具体错误信息
```
