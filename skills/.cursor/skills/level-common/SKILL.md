---
name: level-common
description: >-
  盘古3D关卡制作主 agent 编排手册。包含：第零章 MUST/NEVER 硬红线（M1-8 + N1-12）、
  子 agent 派遣路由、路径规范、坐标系统、OJ骨架约定、编码禁忌、多 Agent 协作规范。
  主 agent 动手前必读本文件（尤其第零章）。
  资源搜索由 level-resource 子 agent 完成；关卡生成由 creator 子 agent 完成；
  扫描由主 agent 直接调用 scripts/_scan_level.py；改造/审查由专属子 agent 完成。主 agent 只做决策与编排。
---

# 盘古3D关卡制作 · 主 Agent 编排手册

## ⛔ 第零章：MUST / NEVER 硬红线（最高优先级）

> **优先级高于所有业务规则**。动手前逐条自检，交付前必须证明每条已校验。违反 = 关卡报废。

### MUST（违反即返工）

| # | 规则 | 校验方式 |
|---|------|---------|
| M1 | 打包前跑 `scripts/verify_gates.py`，退出码 0 才允许交付 | 🤖 自动 |
| M2 | 按 `blocks_reference.md §0` 给 params 数量，禁止凭经验猜 | 🤖 gate1 |
| M3 | `PlayAnimation(name)` 前查该角色有此动画（资源搜索员负责预校验） | 👀 人工 + 🔍 审查员 |
| M4 | 有歧义 / 资源缺口 / 不确定时主动向设计师提问，不擅自假设 | 👀 人工 |
| M5 | BlockScript 的所有 fragment/block 操作必须走 MCP（`add_fragment` / `modify_block_parameter` / `append_block` 等），禁止直接手写 fragment/block JSON | 👀 人工 |
| M6 | 含摄像机积木时，`CameraFollow(DISTANCE, OFFSET_Y, HEIGHT)` 必须按 `positioning.md §3` spread 反推计算（或来自设计师确认单明确指定），禁止凭印象推算 | 👀 人工 + 🔍 审查员 |
| M7 | 修改或生成关卡前，必须向人类明确确认「改后/生成后效果」，获明确 OK 后才允许动手；**未获确认 = 强制停止** | 👀 人工 |
| M8 | 打包前必须用 `validate_workspace`（MCP）验证，`error_count == 0` 才允许打包 | 🤖 MCP |

### NEVER（违反即关卡报废）

| # | 规则 | 校验方式 |
|---|------|---------|
| N1 | 把未通过 `verify_gates.py` 的包交给设计师 | 🤖 自动 |
| N2 | 给 Effect props 设 `Visible=false` | 🔍 审查员 |
| N3 | 在积木 JSON 里用 `next` 串联（一律平铺 children） | 🤖 gate2 |
| N4 | 对嵌套 Operator 省略 `{"type":"block","val":{...}}` 包装 | 🤖 gate1 |
| N5 | 对 `ListGetItemAt / Mod / StrJoin` 等多参积木加中间 `{}` 占位 | 🤖 gate1 |
| N6 | 让人形角色初始间距 <1m，或人形与 control 间距 <0.5m | 🔍 审查员 |
| N7 | 让两个角色在同一时段内移动到同一位置（终点欧氏距离 <1m） | 🔍 审查员 |
| N8 | 凭记忆/跨角色抄动画名（每个 AssetId 动画池独立） | 👀 人工 + 🔍 审查员 |
| N9 | 对角色做瞬间放大（必须 ChangeSize 渐变） | 🔍 审查员 |
| N10 | 擅自假设剧情 / 单位 / 资源 | 👀 人工 |
| N11 | 交付 zip 缺少 `export_info.json`、icon png，或 `solutionUid` 格式不符 | 🤖 自动 |
| N12 | 自行估算 `CameraFollow` 参数（不按 `positioning.md §3` 计算，凭印象写） | 👀 人工 + 🔍 审查员 |
| N13 | 把数组（`[...]`）写入积木 `params` 的任意一项；每项只允许 `{"type":"var","val":"..."}` / `{"type":"block","val":{...}}` / `{}` 三种形式；多参积木（如 `GotoPosition3D`）必须每个坐标独立写一项，**不得合并为数组** | 🤖 gate1 |
| N14 | 积木节点类型归属强制规则（详见 design_rules.md R-17）：A·Camera专属积木只能在CameraService内；B·UIView专属积木（GotoPosition2D/UI扩展/Animation补间）只能在UIView内；C·Character专属积木（PlayAnimation系列/导航移动/AnchorTo）只能在Character内；D·3D专属积木（TurnUp/TurnDown/PointInPitch/GotoPosition3D等）禁止出现在UIView/CameraService | 🤖 check_reviewer_items R17（A/B/C/D四组自动检查） |

---

## 场景路由（先判断任务类型）

| 用户意图 | 触发词 | 走哪个入口 |
|---------|--------|----------|
| 🆕 新建关卡 | 创建/生成/做一个/新建 OJ/制作教师端 | 读 `level-new/SKILL.md` |
| 🔧 修改已有关卡 | 修改/调整/改动/基于 XX 改/把 XX 改成 YY | 读 `level-modify/SKILL.md` |

> 判断不了 → 先向设计师确认，不擅自假设。

---

## 子 Agent 派遣路由（主 agent 只负责编排）

主 agent 永远不亲自执行以下工作，全部派遣专属子 agent：

| 工作 | 执行方式 | 参考文件 |
|------|---------|---------|
| 资源搜索（角色/物件/场景/BGM 查询、Top3推荐、动画校验） | 派遣资源搜索员子 agent | `level-resource/SKILL.md` |
| 新建关卡生成（MCP流水线 + 打包 + 验证） | 派遣关卡生成员子 agent | `level-new/creator_skill.md` |
| **修改关卡扫描** | **主 agent 直接 `run_python`**，脚本：`scripts/_scan_level.py`，参数：`[WORKDIR_PATH, WS_FILE_PATH]` | ~~`level-modify/scanner_skill.md`~~（已删除） |
| 修改关卡改造 | 派遣改造员子 agent | `level-modify/modifier_skill.md` |
| 交付前审查 | 派遣审查员子 agent | `level-common/reviewer_skill.md` |

**派遣规则**：
- 需要资源信息时 → **强制**先派遣资源搜索员，获取结果后再继续流程
- 资源搜索员：`subagent_type: generalPurpose, readonly: true`
- 关卡生成员：`subagent_type: generalPurpose, readonly: false`
- 改造员：`subagent_type: generalPurpose, readonly: false`
- 审查员：`subagent_type: generalPurpose, readonly: true`，**每次复审新开，禁止 resume**

⛔ **有包体必扫规则**：只要用户提供了 zip / `.ws` 文件，且当前 session 尚未对该包运行过 `_scan_level.py`，**必须立即调用 `run_python`** 执行扫描，获得 §1~§8 + 表A + 表B 报告后再继续。唯一豁免：当前 session 中该包的完整扫描结果已在上下文中。

---

## 平台架构基础认知

**zip 包 = 3D 动画可视化层**，不是代码存储层。

| zip 包里有什么 | 在哪里 |
|--------------|--------|
| 3D 场景树（角色/道具/特效） | `.ws` → `scene.children` |
| BlockScript 动画逻辑 | `.ws` → `scene.children[*].BlockScript.fragments` |
| OJ 框架变量 | `.ws` → `scene.props2` |
| 演示示例值 | `.ws` → `WhenGameStarts` 的 SetVar |

zip 包里**永远没有**：C++ 源代码。

---

## Path Conventions（路径规范）

| 路径 | 说明 |
|------|------|
| `input/` | 设计师输入文件（代码、待修改 zip 等） |
| `参考/` | 已上线关卡 zip（只读参考） |
| `参考-extracted/` | 参考包解压缓存 |
| `output/new/{LEVEL_NAME}.zip` | 🆕 新建关卡输出 |
| `output/modify/{ORIG_NAME}-v{N}.zip` | 🔧 修改关卡输出（v 递增，不覆盖旧文件） |

---

## 坐标系统（关键）

**结论（2026-04-27 实证 25 包 + 编辑器实测）**：

- `.ws` JSON 里所有长度字段（Position / Size / GotoPosition3D / GlideSecsToPosition3D / MoveSteps）存**米**。
- 编辑器换算：`ws值 × 30 = 编辑器显示的厘米`（不是 × 100）。
- ⚠️ 轴互换：ws `Position[1]` 对应编辑器 Z（高度），ws `Position[2]` 对应编辑器 Y（左右）。
- 唯一例外：`CameraFollow` 的 distance/offsetY/height 是**厘米**（历史遗留）。

| 字段 | JSON 存储单位 |
|------|------------|
| Character/MeshPart `Position` | **米**（地面 y=0.27） |
| GotoPosition3D / GlideSecsToPosition3D / MoveSteps | **米** |
| CameraFollow `distance / height / offsetY` | **厘米** |
| Scale | 倍数（1.0=原始） |
| SetSize / ChangeSize | 百分比（100=原始） |

```
editor_X(cm) = ws.Position[0] × 30
editor_Y(cm) = ws.Position[2] × 30   ← ws[2]，非[1]
editor_Z(cm) = ws.Position[1] × 30   ← ws[1]，非[2]
```

---

## 角色移动方式

| 方式 | 积木 | 坐标单位 |
|------|------|---------|
| 瞬移 | `GotoPosition3D` | **米** |
| 跑步移动（有动画） | `RunToTargetAndWait` | 目标物件名，无坐标 |
| 滑动移动 | `GlideSecsToPosition3D` | **米** |
| 速度倍率 | `SetSpeedMul` | 倍率 |

- 演出中角色移动必须用 `RunToTargetAndWait`，不能用 `GotoPosition3D`
- 停在物件"前方"时，用隐形路标（AssetId:10548, Visible:false）

---

## 摆放规则

1. 不重叠，无关联物件间隔 >0.5m
2. 人形角色两两间距 ≥1m，与 control ≥0.5m（N6）
3. 物件占场景面积 30%~80%
4. 轴心偏移（地面物件必须）：轴心在底部 → `Position[1]=0.27`；轴心居中 → `Position[1]=0.27+size.y/2×Scale`
5. 非默认教室场景（28746）：摆完后用 `navmesh_validate` 验证所有坐标

---

## OJ 骨架约定（候补模块 + 云编译切换）

| 对象 | 字面量 | 作用 |
|------|-------|------|
| 候补 hat | `WhenReceiveMessage("参数注入")` | 固定输入注入（受保护，扫描员必须归 B1） |
| 候补激活 | `BroadcastMessage("参数注入")` | 只有云编译 A 栏广播；OJ 不广播 → 候补静默 |
| 收尾 | `样例成功` | OJ 超档 + 云编译结束统一收尾 |

**`参数注入` 是受保护的消息名**：主 agent 或改造员看到 `WhenReceiveMessage("参数注入")` 必须归 B1 候补，不能归 B2 遗留，不能删除。

---

## 代码整洁规则

| 规则 | 说明 |
|------|------|
| 无孤立片段 | 每个 fragment 必须有 hat block（WhenGameStarts / WhenReceiveMessage 等） |
| 无未调用块 | hat 事件名从未被广播 → 删除；**豁免**：`参数注入` hat 是候补，保留 |
| 无空脚本 | 无逻辑的物件 BlockScript.fragments = [] |
| 无冗余变量 | props2 只声明实际被引用的变量 |
| 最小修改原则 | 只改明确要求的内容，以下字段一律不动：物件 id/UUID/Name/AssetId/位置/旋转/缩放/solution.json/export_info.json |

---

## 0.8 编码禁忌（必须遵守）

**不可违反的规则**：

1. **禁止**用 PowerShell `Get-Content` / `Set-Content` / `-replace` 管道改含非 ASCII 字符的文件
2. **禁止**用 `sed` / `awk` 改中文文件
3. **禁止**用 shell 重定向 `>` / `>>` 写中文到文件
4. **唯一允许**修改含中文文本文件的工具：Cursor 的 `StrReplace` / `Write` / `EditNotebook` 工具；或显式 `python -X utf8` 脚本用 `Path.read_bytes().decode("utf-8")`
5. 若必须 shell 操作：先 `chcp 65001` + `$env:PYTHONIOENCODING='utf-8'` 且走 Python 脚本

---

## 0.9 多 Agent 协作规范

### 子 agent 职责

| 类型 | subagent_type | readonly | 禁止 |
|------|--------------|---------|------|
| **资源搜索员** | `generalPurpose` | true | 编造 AssetId、做决策、写文件 |
| **关卡生成员** | `generalPurpose` | false | 越界改资源清单、跳过 validate、写 `_xxx.py` |
| **改造员** | `generalPurpose` | false | 越界改其他关卡、跳过 verify、自行 Python 降级 |
| **审查员** | `generalPurpose` | true | 写"建议"、给中间态、改文件 |

**类型不许混用**：所有子 agent 均为 `generalPurpose`；资源搜索员和审查员通过 `readonly: true` 约束禁止写文件。

### 单关卡标准流程

```
[新建] 收集信息 → 派资源搜索员 → 制确认单 → 设计师 OK（M7卡点）→ 派生成员 → 派审查员 → 交付
[修改] 策划输入 → 并行触发（run_python _scan_level.py）→ 三项原子前置（A.扫包完整性S1/S2/S3 + B.读modify_playbook.md匹配模式M-X + C.最小diff清单）→ 制对比卡 → 设计师 OK（M7卡点）→ 派改造员 → 派审查员 → 交付
```

**并行规则**：`run_python _scan_level.py` 和主 agent 读 skill **必须同一消息批次触发**，不允许串行等待。

### 主 agent 收到子 agent 返回后的质检

- **资源搜索员**：每项资源都有 AssetId 证据？未找到的需求已明确标注？
- **扫描报告**（`run_python _scan_level.py` 返回结果）：§1~§8 全有内容？表 A 每 fragment 都有分类？表 B 覆盖所有 SetVar？
- **改造员**：改造前确认表存在？每改动有执行回报？validate error_count==0？verify_gates gate1/2/3 PASS？
- **审查员**：`总体：PASS` 字面存在？第6项（MUST/NEVER）和第7项（观赏性）所有子条目 PASS？

---

## 0.10 hetu-mcp 工具对照表

| 我要做什么 | 走 MCP（首选） | 辅助脚本 |
|-----------|--------------|---------|
| 读工作区 JSON | `load_workspace_file` | — |
| 扫某类积木 | `find_blocks_by_type` | — |
| 加 fragment | `add_fragment` | — |
| 改积木参数 | `modify_block_parameter` | — |
| 追加积木 | `append_block` | — |
| 插入子积木 | `insert_block_child` | — |
| 协议校验 | `validate_workspace` | — |
| 保存 | `save_workspace_file(create_backup=False)` | — |
| 场景树操作（Position / Effect / MeshPart） | ✗ MCP 不管 | `scripts/scene_utils.py` |
| zip 打包/解包 | ✗ MCP 不管 | `scripts/pkg_utils.py` |

**给子 agent 的指令必须包含**：

> "本仓库已配置 `hetu-mcp`。读写 `.ws` 必须优先调用 MCP 工具。场景树用 `scripts/scene_utils.py`。禁止临时写 `_xxx.py` 一次性脚本。交付前必须跑 `validate_workspace` 且 `error_count == 0`。MCP 使用前读 `.cursor/skills/level-common/mcp_advanced.md` + `mcp_skill_glossary.md`。"

**主 agent 质检子 agent 返回时**，参照 `.cursor/skills/level-common/reviewer.md §4` 质检问执行验收。平台导入失败时，指引改造员读 `reviewer.md §5`。

---

## 0.0.2 输出精简硬上限

1. **确认单 ≤ 10 行**
2. **交付摘要 ≤ 15 行**
3. **每条 AskQuestion 之前说明 ≤ 3 行**

禁止"复述理解"段 / 过程独白 / 重复列示例 / 在红线清单后复述红线。

---

## 0.7 会话卫生

| 场景 | 推荐做法 |
|------|---------|
| 对话很长，开始出现"忘记规则" | 人类主动要求**开新会话**，新 agent 从零读最新 SKILL |
| 单次任务涉及 ≥2 个关卡 | 读 `level-common/multi_agent_protocol.md` 完整协作规范 |
| 任何交付前 | 强制走**独立审查员 agent**（explore+readonly，不 resume） |
