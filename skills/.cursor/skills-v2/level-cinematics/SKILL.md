---
name: level-cinematics
mode: create_cinematic
description: >-
  剧情演出制作主 Agent 编排手册。
  触发词：写剧情/生成剧情/做剧情关卡/基于剧本制作/制作剧情演出。
  四步流程：接收剧本 → 解析+扫包+资源搜索 → 分镜确认单 → 派生成员。
  输出 output/new/{NAME}.zip（无母本）或 output/modify/{NAME}-vN.zip（有母本）。
---

# 剧情员主 Agent · 入口

> 你只做编排决策：收剧本、派解析员、等资源、出确认单、等 OK、派生成员。
> 不亲自解析剧本、不亲自搜索资源、不亲自写 BlockScript。

---

## 触发判断

- **本模式**：写剧情 / 生成剧情 / 做剧情关卡 / 基于剧本制作 / 制作剧情演出
- **跳转**：涉及 OJ 判题逻辑 → 读 `level-new/SKILL.md`；仅改参数/值/角色 → 读 `level-modify/SKILL.md`
- **判断不了**：向设计师确认，不擅自假设

---

## 执行步骤索引

> 每步开始前才读对应文件，不要一次全部读入

| 步骤 | 内容 | 需要读的文件 |
|------|------|------------|
| Step 1 | 接收剧本 + 询问 ws 包路径和关卡名 | `steps/workflow.md §1` |
| Step 2 | 【并行】扫包(可选) + 派分镜解析员 + 派资源搜索员 | `steps/workflow.md §2`；派 `agents/storyboard_agent.md`；派 `../_shared/resource_agent.md` |
| Step 3 | 汇总两员返回 → 输出分镜确认单 → M7 等 OK | `steps/workflow.md §3` |
| Step 4 | 派生成员（有 ws → modifier；无 ws → creator） | `steps/workflow.md §4` |

> **Step 1 完成条件 → 立即切换**：同时满足 ① 剧本原文 ② ws 包路径（或确认"无"） ③ 关卡名，则读 `steps/workflow.md §2` 执行 Step 2，**禁止重读 §1 或已读过的文件**。

---

## 三条核心禁令

| # | 禁令 |
|---|------|
| C1 | 有 ws 包且当前 session 未扫过 → **扫包（A）与派分镜解析员（B）必须同批次并行触发**，禁止等扫包完成后再派 B |
| C2 | **M7 卡点**：未获设计师明确 OK（"确认/可以/OK"）→ 强制停止，不得派生成员 |
| C3 | 禁止擅自假设 AssetId / 动画名 / 场景（N10）；所有资源缺口必须在确认单中标注并等待设计师决定 |

其余执行规则（BlockScript 构建、validate、verify_gates 等）已内嵌到各 `agents/` 文件对应步骤中。

---

## 子 Agent 速查

| 需要做什么 | 读哪个文件 | subagent_type | readonly |
|-----------|-----------|--------------|---------|
| 剧本→分镜解析 | `agents/storyboard_agent.md` | generalPurpose | true |
| 角色/动画/场景/特效/音效搜索 | `../_shared/resource_agent.md` | generalPurpose | true |
| 生成剧情关卡（无母本） | `../level-new/agents/creator_agent.md` | generalPurpose | false |
| 改造剧情关卡（有 ws 包） | `../level-modify/agents/modifier_agent.md` | generalPurpose | false |
| 交付前审查（由生成员内部派） | `../_shared/reviewer_agent.md` | generalPurpose | true |

> 审查员每次复审必须**新开子 Agent**，禁止 resume 复用。

---

## 路径规范

| 路径 | 说明 |
|------|------|
| `input/` | 设计师输入文件（ws 包等） |
| `output/new/{NAME}.zip` | 无母本时的输出 |
| `output/modify/{ORIG_NAME}-v{N}.zip` | 有母本时的输出（v 递增，不覆盖旧版） |
