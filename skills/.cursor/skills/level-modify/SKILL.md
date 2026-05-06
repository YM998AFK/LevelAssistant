---
name: level-modify
description: >-
  修改已有盘古3D关卡的主 agent 编排手册。当用户提到修改关卡、调整效果、改动已有包、
  基于XX包改、把XX改成YY、改挑战X、练习X改成YY时触发。
  新架构：主 agent 只负责决策与编排，各专属子 agent 执行具体工作。
  四步流程：策划输入 → 扫包+状态对比卡 → dispatch 改造员 → dispatch 审查员。
  需要资源查找时强制先派遣 level-resource 子 agent。
  输出 output/modify/{ORIG_NAME}-v{N}.zip。
  所有规则 / 编码禁忌在 level-common/SKILL.md，模式库在 level-common/modify_playbook.md。
---

# 盘古3D关卡修改 · 主 Agent 编排手册

> **主 agent 职责**：决策、编排、质检、交付。不亲自跑脚本、不亲自改 JSON、不亲自审查。

---

## ⛔ 开工前置（不可跳过）

**必须先完整读** `level-common/SKILL.md`，重点：

- **第零章 MUST / NEVER**：M1-8 + N1-12 共 20 条硬红线
- **子 Agent 派遣路由**：哪个工作派哪个子 agent
- **0.8 编码禁忌** / **0.0.2 输出精简硬上限**（确认单 ≤10 行 / 交付摘要 ≤15 行）

### 子 agent SKILL 文件位置（主 agent 派遣时告知子 agent 读哪个文件）

| 子 agent | 读哪个 SKILL | 派遣模板 |
|---------|------------|---------|
| 资源搜索员 | `level-resource/SKILL.md` | `level-resource/resource_prompt.md` |
| 扫描员 | `level-modify/scanner_skill.md` | `level-modify/scanner_prompt.md` |
| 改造员 | `level-modify/modifier_skill.md` | `level-modify/modifier_prompt.md` |
| 审查员 | `level-common/reviewer_skill.md` | `level-modify/reviewer_prompt.md` |

---

## 触发条件

- 修改关卡、调整效果、改动已有包
- 基于 XX 包改、把 XX 改成 YY
- 改挑战 X、练习 X 改成 YY、抽查 XX

**全新创建** → 跳 `level-new/SKILL.md`。**判断不了** → 向设计师确认。

---

## 路径判断

| 情况 | 判断条件 | 走哪条路径 |
|------|---------|----------|
| **标准路径** | 新 session 打开已有包，或当前 session 尚未分析过该包 | 完整 4 步（见下方） |
| **同 session 轻量修复** | 当前 session 中 agent 刚完成该包的生成或修改，设计师指出具体问题 | 见下方"轻量修复路径" |

> 判断不了 → 默认走**标准路径**。

---

### 同 session 轻量修复路径

**触发条件**（同时满足）：
1. 当前 session 中 agent 刚完成该包的生成或修改（S1-S3 扫描结果全在上下文中）
2. 设计师指出具体问题（"这里效果不对"、"这个角色朝向错了"）

**免除项**：S1 / S2 / S3 扫包三步（包结构已在上下文，重扫是纯浪费）。

**不可免除项**：

| 步骤 | 内容 |
|------|------|
| 轻量确认单 | 输出 ≤5 行微型确认单（格式见下），等设计师明确 OK 后才动手（**M7 不免**） |
| dispatch 改造员 | 填写 modifier_prompt.md 模板，dispatch 改造员子 agent（读 modifier_skill.md） |
| dispatch 审查员 | 改完必须新开审查员复审（**不可跳过**） |

**轻量确认单格式**：
```
【问题】<设计师指出的问题，一句话>
【改法】<agent 打算怎么改，一句话>
【改后效果】<改完后这段演出是什么样>
确认？(y/n)
```

---

## 流程总览（标准路径 · 4 步）

```
第1步  策划输入（包路径 + 需求描述）
  ↓
第2步  【并行】dispatch 扫描员 + 主 agent 推导改造方案
        → 扫描员返回 §1~§8 + 表A(三栏) + 表B(变量覆盖)
        → 若需要资源查找：派遣资源搜索员（强制）
        → 主 agent 合并信息，制定改造方案，输出状态对比卡
        → 等设计师确认（M7 强制卡点）
  ↓
第3步  dispatch 改造员（填 modifier_prompt.md 模板）
        → 改造员返回：确认表 + 逐项执行回报 + validate 结果 + verify_gates 结果
        → 主 agent 质检返回值
  ↓
第4步  dispatch 审查员（填 reviewer_prompt.md 模板）
        → 审查员返回：7项 PASS/FAIL + 总体判定
        → 全 PASS 才交付
        FAIL → 主 agent 决策修法 → 新开改造员 → 新开审查员（不 resume）
```

---

## 第1步 · 策划输入单

策划输入只需包含（**1 必填 + 1 语义描述**）：

| 字段 | 必填 | 示例 |
|------|------|------|
| **要改的包** | ✅ | `参考-extracted/练习6.zip` / `output/modify/xxx-v1.zip` |
| **语义描述** | ✅ | 原效果描述 / 目标效果描述 / 答案页 cpp / 目标题干 |

**主 agent 收到后**：
- 语义不清 → 追问，不擅自假设
- 语义清晰 → 进入第2步（并行 dispatch 扫描员 + 推导改造方案）

### 快速推断规则（以下情况直接进入第2步，无需追问）

| 用户提供 | 推断结论 | 对应模式 |
|---------|---------|---------|
| zip + 答案页.cpp（含 `▼▲` 折叠标记，或文件名含"答案页"） | 修正关卡代码/折叠区与 cpp 对齐 | M-10 / M-11 |
| zip + "改 N 范围" / "范围改成 a~b" | 调整循环上界 | M-4 |
| zip + "换[角色名]" | 族内替换主角 | M-6 |
| zip + "练习X改成练习Y" | cid 切分 | M-1 |
| zip + "再加一关" / "加挑战N" | 同族加关 | M-7 |

**附加规则**：
- 提供 cpp 文件数 ≥ 2，且文件名分别对应不同挑战 → **默认所有对应挑战都要对齐，不询问**
- 用户说"按你的推测" → **直接给出推断并说明理由**，等用户否定后再调整
- 如需追问，**一次性列出所有疑问**，不轮番追问

---

## 第2步 · 扫包 + 状态对比卡

### ⛔ 扫包完整性硬闸门（三项全完成才允许输出对比卡）

| # | 必做项 | 完成标志 |
|---|--------|---------|
| S1 | 读 `参考-extracted/<母本>/_analysis.md`（不存在则先跑 `python scripts/ref_ingest.py --json`） | 文件已读，或已确认生成成功 |
| S2 | 按 `level-common/modify_playbook.md §6` 扫描三栏（活代码 A / 候补 B1 / 遗留 B2）+ 变量覆盖影响表（表 B） | 两张表在扫描员返回结果中存在 |
| S3 | 用 `scripts/ref_diff.py <母本dir> <当前包dir>` 确认包结构全貌 | diff 输出已读取，无遗漏模块 |

**三项中任一未完成 → 禁止输出对比卡，禁止进入第3步。**

### 如何 dispatch 扫描员

1. 填写 `scanner_prompt.md` 模板（告知扫描员：读 `level-modify/scanner_skill.md`）：
   - `${ZIP_PATH}`：目标 zip 绝对路径
   - `${WORKDIR_PATH}`：解压后工作目录
   - `${WS_FILE_PATH}`：ws 文件绝对路径
   - `${TARGET_HANDLERS}`：根据用户需求推断的重点 handler（如 `cmd=cin 分支, 计算速度 handler`）
2. **与推导改造方案并行 dispatch**（同一消息批次，不串行等待）

### 需要资源查找时（强制派遣资源搜索员）

若改造方案涉及替换角色 / 换物件 / 查动画 / 查场景，**强制**在扫描阶段同步派遣资源搜索员：
- 填写 `level-resource/resource_prompt.md` 模板
- 与扫描员**同一批次**派遣

### 扫描员返回后的质检三问

收到扫描员返回，以下三项必须全 YES 才继续：
1. §1~§8 八个区段全部有内容？
2. 表 A（三栏分类）存在且每个 fragment 都有分类？
3. 表 B（变量覆盖影响表）存在且覆盖所有 SetVar/ListReplaceItemAt？

任一 NO → 打回扫描员重做（新开 Task，不 resume）。

### 状态对比卡格式（固定模板，主 agent 填写后发给设计师）

```
【当前效果】
<用自然语言描述当前关卡从头到尾的玩家体验：
 - 输入什么（演示值是什么）
 - 角色/场景发生了什么（每个关键动作都要写出来，不列动画名）
 - 最终结果是什么>

【改后效果】
<同样细度描述改后的体验。变更的部分用**加粗**标注。
 - 每个关键动作都要写（不能只写"同上"）
 - 循环变单次、分支增删、输入范围变化等逻辑改动要明确说>

【演示值】
当前：<值>
改后：<值>（说明为何选此值，如"能触发成功路线"）

确认后开始修改？（或告诉我需要调整的地方）
```

**粒度规则**：
- ✅ 写：角色做了什么、屏幕显示了什么、条件成不成立、最终结果
- ❌ 不写：动画名、积木名、fragment 编号、技术实现细节

> ⛔ **M7 强制卡点**：对比卡发出后，必须等人类明确回复"确认 / 可以 / OK"才允许进入第3步。

---

## 第3步 · dispatch 改造员

设计师确认后，主 agent 填写 `modifier_prompt.md` 并 dispatch 改造员子 agent（改造员读 `modifier_skill.md`）。

### 如何填写 modifier_prompt.md

1. **${WS_FILE_PATH}**：工作目录下的 uuid.ws 文件绝对路径
2. **${WORKDIR_PATH}**：解压工作目录
3. **${BASELINE_ZIP}**：母本 zip 绝对路径
4. **${OUTPUT_ZIP_PATH}**：`output/modify/{原包名}-v{N}.zip`（N 递增，不覆盖旧版）
5. **${CHANGE_LIST}**：根据扫描结果 + 设计师确认，逐条写出：
   ```
   改动N  路径：<scene.children[...].fragments[...]...>
          改前：<具体积木类型和参数值>
          改后：<目标值>
          工具：<MCP 工具名>
   ```
   - 路径要精确到具体 block（不能写"控制台的某处"）
   - 改前值来自扫描员 §5/§6/§7 的输出
   - 参照 `level-common/modify_playbook.md` M-1~M-10 的"最小 diff"

### 改造员返回 paused（MCP 失败暂停）的处理

改造员返回 `{"paused": true, "resume_id": "...", "question": "..."}` 时：

1. **读取 question**：了解改造员遇到的具体问题（失败工具名、报错、已完成步骤）
2. **主 agent 决策**：
   - 若有明确解法（如"改用 ws_set_value 直接写"）→ 调用 `resume_subagent(resume_id, instruction)` 注入指示
   - 若需要人类判断（如"该资源不存在，是否换用其他 AssetId"）→ 先向设计师说明，获得明确答复后再 `resume_subagent`
3. **resume 后**：改造员从断点继续执行，完成后返回正常结果

> ⚠️ `resume_subagent` 只能调用一次，调用后原 `resume_id` 失效（状态文件已删除）。若 resume 后再次 paused，会返回新的 `resume_id`，继续按上述流程处理。

### 改造员返回后的质检五问

收到改造员返回（非 paused），以下五项必须全 YES 才进入第4步：
1. 改造前确认表存在且每个改动都有列出？
2. 每个改动都有"[改动N] 完成"的执行回报？
3. validate_workspace error_count == 0？
4. verify_gates.py 输出中 gate1/gate2/gate3 均 PASS（或 FAIL 与母本一致）？
5. verify_gates.py 输出中 gate4（zip 完整性）PASS 或与母本 FAIL 一致（遗留）？

任一 NO → 主 agent 决策修法，重新 dispatch 改造员（新开 Task）。

---

## 第4步 · dispatch 审查员 + 交付

主 agent 填写 `reviewer_prompt.md` 并 dispatch 审查员子 agent（审查员读 `level-common/reviewer_skill.md`）。

### 如何填写 reviewer_prompt.md

1. **${BASELINE_ZIP}**：母本 zip 绝对路径
2. **${NEW_ZIP}**：第3步输出的新包路径
3. **${STEP_TABLE}**：从状态对比卡的"改后效果"提炼的 step 变更表：
   ```
   | step | 状态 | 说明 |
   |------|------|------|
   | cmd=cin 初始化 | 变更 | SetVar(z) 从 ListGetItemAt 改为 '1' |
   | 外层循环换行 | 变更 | 外层 Repeat 内新增 BroadcastMessageAndWait('换行') |
   | 其余 handler | 同 | 未改动 |
   ```

### 审查员返回后的质检三问

1. `总体：PASS` 字面存在？
2. 第6项（MUST/NEVER）和第7项（观赏性）所有子条目都是 PASS？
3. M3/M6/N2/N6/N7/N8/N9/N12 的具体结论已在返回报告中？

全 YES → 进入交付。

任一 NO：
- 主 agent 决策修法
- 新开改造员（Task，不 resume）→ 新开审查员（Task，不 resume）
- 循环直到审查员全 PASS

### 路径与版本号（主 agent 自查）

- 路径：`output/modify/{原包名}-v{N}.zip`，不是 `output/` 根目录、不是 `output/new/`
- 不覆盖旧版：`-v{N}.zip` 已存在则递增为 `v{N+1}`

### 交付消息（主 agent 必须包含以下所有内容）

```
## 交付

包文件   : output/modify/{原包名}-v{N}.zip (<大小> KB)
改动摘要 : （引用 step 变更表，不超过 5 条）
遗留问题 : <有则列 / 无则写"无">
verify_gates : PASS(4/4) gate1✅ gate2✅ gate3✅ gate4✅
审查员结论 : 总体 PASS（M3: <具体> / N7: <具体> / 观赏性: <具体>）

MUST/NEVER 自检：M1-8 ✅ / N1-12 ✅
（🤖 verify_gates PASS / 🤖 MCP validate PASS / 🔍 审查员第6~7项 PASS / 👀 人工已确认 M4/M7）
```

**审查员报告里 M3/M6/N2/N6/N7/N8/N9 以及观赏性的具体结论，必须在交付消息里转述**，不能只写"审查员 PASS"。

---

## 最小化改动原则

只改设计师在第3步明确确认的 step，以下字段**一律不动**（除非它本身是改动目标）：

| 不动的字段 | 原因 |
|---------|------|
| 物件 `id` / UUID | 其他节点可能引用 |
| 物件 `Name` / `AssetId` | 影响资源加载和脚本定位 |
| 位置 / 旋转 / 缩放 | 影响场景布局 |
| `solution.json` / `export_info.json` | 元数据，改动无益 |
| 无关 `BlockScript` 片段 | 保持原有逻辑完整 |

---

## 与新建关卡的区别

| 维度 | 修改（本 skill） | 新建（level-new） |
|------|----------------|----------------|
| 触发词 | 修改/调整/改动/基于XX改 | 创建/生成/做一个/新建 |
| 流程 | 4 步：输入 → 扫包+对比卡 → 改造员 → 审查员 | 3 步：收集 → 资源搜索+确认 → 生成 |
| 输出 | `output/modify/{ORIG_NAME}-v{N}.zip` | `output/new/{LEVEL_NAME}.zip` |

若开工中发现是"全新制作"（根本没有母本）→ **立即切换到 level-new**，不硬走修改流程。
