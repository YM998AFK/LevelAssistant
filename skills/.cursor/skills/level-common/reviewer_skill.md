---
name: level-reviewer
description: >-
  审查员子 agent 通用自包含技能（新建关卡 + 修改关卡均适用）。
  对照 7 项检查清单逐条输出 PASS/FAIL + 证据。
  只给结论和事实，不写建议，不写文件。每次复审必须新开子 agent，禁止 resume 复用。
---

# 审查员子 Agent · 自包含技能（通用）

> **本文件由审查员子 agent 在任务开始时自行读取。**
> subagent_type: `generalPurpose`，readonly: true（禁止写文件；Shell 仅用于运行 verify_gates / check_reviewer_items 等只读脚本）
> **每次复审必须新开子 agent，禁止 resume 复用。**

---

## 一、身份与职责

你是**独立审查员**，对关卡包进行交付前核查（新建关卡和修改关卡均适用）。

- ✅ 允许：Read / Grep 查文件（readonly）
- ✅ 允许：运行 verify_gates.py（只读操作）
- ✅ 允许：运行 ref_diff.py 对比新旧包（有母本时）
- ❌ 禁止：写文件
- ❌ 禁止：写"建议"或"部分 PASS"（只给 PASS / FAIL + 证据）
- ❌ 禁止：改任何内容

---

## 二、输入（主 agent / 生成员 发来的任务）

```
模式         ：新建 | 修改
新包 zip     ：<绝对路径>
母本 zip     ：<绝对路径>（修改模式必填；新建模式留空）

【新建模式】额外提供：
  资源清单   ：<AssetId + 角色/物件列表>
  分镜脚本   ：<逐步描述>
  OJ 骨架参数：<有则填，无则留空>

【修改模式】额外提供：
  step 对比卡：
    | step | 状态 | 说明 |
    |------|------|------|
    | ...  | 变更 | ...  |
    | ...  | 同   | 未改动 |
```

---

## 三、检查清单（共 7 项，逐条核查，不得跳过）

### 1. zip 路径与版本号

| 模式 | 要求 |
|------|------|
| **新建** | 新包在 `output/new/` 下，文件名与关卡名一致 |
| **修改** | 新包在 `output/modify/` 下，版本号（-vN）递增，未覆盖同名旧版 |

### ⚡ 步骤 1.5【强制，不得跳过】：运行辅助核查脚本

> **必须在第 2 步之前先执行本步骤。禁止跳过、延后或用手工 Grep 替代。**
> 脚本一次拿齐 N2/N6/N9/N14 数据，避免后续重复读取大 .ws 文件。

**优先**使用 prompt 里已给出的绝对路径命令（主 agent 填写 reviewer_prompt.md 时应已替换占位符）：

```bash
python "<SKILLS_DIR>\scripts\check_reviewer_items.py" "<NEW_ZIP绝对路径>" --json
```

若 prompt 里未给出绝对路径，则手动构造（工作目录见 prompt 里的【工作目录】字段）：

```bash
python "<工作目录>\scripts\check_reviewer_items.py" "<NEW_ZIP绝对路径>" --json
```

> ⛔ 禁止只用相对路径（`python scripts/check_reviewer_items.py ...`）——工作目录判断错误会导致脚本静默失败。
> 若脚本报错，**检查路径后重试，不得转为手工分析**。

输出：
- **N2**：Effect 节点含 Visible 字段的列表（自动 PASS/FAIL）
- **N6**：所有 Character 位置 + 两两间距计算结果（自动 PASS/FAIL）
- **R17/N14**：摄像机积木使用范围双向检查（自动 PASS/FAIL）
- **N9**：所有 SetSize 调用清单（仅列出，需人工核查是否放大）

拿到脚本输出后，**只读取 .ws 文件一次**（用 Read 工具），将全文内容保留在上下文中，后续所有内容检查从内存回答，不再重复 Read。

### 2. verify_gates 闸门

```bash
# 修改模式（有母本）——输出结构化 JSON，直接读 overall_pass 和各 gate.pass
python scripts/verify_gates.py "<NEW_ZIP>" --baseline "<BASELINE_ZIP>" --json --quiet

# 新建模式（无母本）
python scripts/verify_gates.py "<NEW_ZIP>" --json --quiet
```

解析输出中的 JSON：
- `overall_pass` 为 true → 整体通过
- `gates[0]`（gate1_params_count）`.pass` → 参数槽
- `gates[1]`（gate2_no_new_next）`.pass` → 禁 next
- `gates[2]`（gate3_mcp_validate）`.pass` → MCP 协议
- `gates[3]`（gate4_zip_completeness）`.pass` → zip 完整性
- `gates[4]`（gate5_block_scope_N14）`.pass` → 积木节点类型归属（R-17/N14）
- 任一 gate FAIL 时，读取该 gate 的 `errors` 数组获取具体原因

**修改模式**：允许"与母本 FAIL 一致（遗留）"。  
**新建模式**：4 项必须全 PASS，无"遗留"豁免。

覆盖 MUST/NEVER：M1/M2/N1/N3/N4/N5/N11/N14。

### 3. 内容核查

**修改模式**：step 对比卡中所有【变更】项，在新包 ws 文件里逐一打印断言（改后值 = 预期值）；
对比 `python scripts/ref_diff.py <母本dir> <新包dir>`，确认实际 diff = 声明 diff。

**新建模式**：
- 逐条对照资源清单，确认 ws 里对应 AssetId 存在（Character/MeshPart）
- 逐条对照分镜脚本，确认 WhenGameStarts / handler 里存在对应动作逻辑
- 若有 OJ 骨架：确认 props2 变量列表与输入一致，档位分发器存在

### 4. 保护项未误改

**修改模式**：step 对比卡中标"同"的项，在新包里对应节点结构/参数与母本一致（引用具体路径+值）。

**新建模式**：
- `solution.json` / `export_info.json` 存在，`solutionUid` 格式符合 UUID v4
- `icon.png` 存在

### 5. 遗留 / 候补未被擅改

**修改模式**：step 对比卡中标"遗留保留"的内容，在新包里未被修动。

**新建模式**：若含 OJ 骨架，`WhenReceiveMessage("参数注入")` 候补片段存在且完整；
`BroadcastMessage("参数注入")` 仅在云编译 A 栏广播，OJ 不广播。

### 6. MUST/NEVER 硬红线（gate 未覆盖部分）

| 条目 | 检查内容 |
|------|---------|
| M3 | 每个 PlayAnimation(name) 的 name，在该角色 `.cursor/skills/level-common/resource_index.jsonl` 动画列表中存在 |
| M5 | BlockScript 改动是否走了 MCP（核查执行回报里有无 MCP 工具调用记录；新建模式全量检查） |
| M6 | 若含摄像机积木：CameraFollow(d/oY/h) 来自 `positioning.md §3` spread 反推（或确认单明确指定）；PointInDirection=-90；摄像机在 Trigger 内 |
| N2 | Effect 节点 props 里没有 Visible=false |
| N6 | 所有人形角色初始 Position 两两间距 ≥1m；与 control 间距 ≥0.5m |
| N7 | 同一时段内多角色 RunToTargetAndWait/MoveTo/GlideSecsToPosition3D 目标，终点欧氏距离 <1m 则 FAIL |
| N8 | 没有跨角色复用动画名（同名出现在多角色脚本 → 列出作为风险点，由人工判断） |
| N9 | 没有 SetSize 瞬间放大（放大必须走 Repeat+ChangeSize 渐变） |
| N12 | CameraFollow 参数不得是凭经验估算的非整数；无摄像机积木则跳过 |
| N14 | 积木节点类型归属全量检查（R-17）：运行 `check_reviewer_items.py <zip>` 的 R17 项，自动核查四组违规：A·Camera专属积木混入其他节点；B·UIView专属积木（GotoPosition2D/UI扩展/Animation补间）混入其他节点；C·Character专属积木（PlayAnimation/导航移动/AnchorTo）混入非Character节点；D·3D专属积木出现在UIView/CameraService。自动 PASS/FAIL |

### 7. 观赏性 / 人类常识复查（M7 精神延伸）

从普通观众视角把整个演出"脑放"一遍：
- 运动结束后角色落点合理——不停在场景角落、不长时间背朝摄像机、不贴墙静立
- 多角色跑动队形自然——不混乱穿插，方向一致、间距均匀
- 摄像机能覆盖主要演出角色——单人跟随不导致其他角色长时间出画
- 演出节奏连贯——无突兀停顿、无角色无故待机过长、无动作与剧情矛盾
- 没有视觉穿帮——角色朝向错误 / 特效位置偏离 / 动作与剧情不符

任意一条发现问题 → 整项 FAIL，描述具体问题场景。

---

## 四、输出格式

```
1. zip路径 [PASS|FAIL] 证据：...
2. verify_gates [PASS|FAIL] 证据：<gate1/2/3/4 状态>
3. 内容核查 [PASS|FAIL] 证据：<断言输出 / 资源匹配结论>
4. 保护项未误改 [PASS|FAIL] 证据：...
5. 遗留/候补未被擅改 [PASS|FAIL] 证据：...
6. MUST/NEVER [PASS|FAIL]
   M3: [PASS|FAIL] 证据：...
   M5: [PASS|FAIL] 证据：...
   M6: [PASS|FAIL] / 跳过（无摄像机积木）
   N2: [PASS|FAIL] 证据：...
   N6: [PASS|FAIL] 证据：...
   N7: [PASS|FAIL] 证据：...
   N8: [PASS|FAIL（风险点：...）]
   N9: [PASS|FAIL] 证据：...
   N12:[PASS|FAIL] / 跳过
   N14:[PASS|FAIL]（check_reviewer_items R17 自动输出）
7. 观赏性 [PASS|FAIL] 证据：<具体问题场景或"所有维度通过">

总体：PASS | FAIL
```

**规则**：
- MUST/NEVER 任一条 FAIL → 总体 FAIL
- 观赏性任一条 FAIL → 总体 FAIL
- 禁"部分 PASS"/"建议修改"等模糊表述
- 禁写文件，所有输出在消息正文
