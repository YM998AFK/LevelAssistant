---
name: level-modify
mode: modify
description: >-
  修改已有盘古3D关卡的主 Agent 编排手册。
  触发词：修改/调整/改动/基于XX包改/把XX改成YY/改挑战X/练习X改成YY。
  四步流程：策划输入 → 扫包+对比卡 → 派改造员 → 派审查员。
  输出 output/modify/{ORIG_NAME}-v{N}.zip。
---

# 改关主 Agent · 入口

> 你只做编排决策，不亲自改 JSON、不亲自跑改造逻辑、不亲自审查。

---

## 触发判断

- **本模式**：修改/调整/改动/基于 XX 改/把 XX 改成 YY/改挑战 X/练习 X 改成 YY
- **跳转**：全新制作（没有母本）→ 读 `level-new/SKILL.md`
- **判断不了**：向设计师确认，不擅自假设

---

## 执行步骤索引

> 每步开始前才读对应文件，不要一次全部读入

| 步骤 | 内容 | 需要读的文件 |
|------|------|------------|
| Step 1 | 收集策划输入（包路径 + 需求描述） | 无需额外读文件 |
| Step 2 | 扫包 + 输出状态对比卡 | `steps/workflow.md §2`（扫包流程）<br>`../_knowledge/modify_playbook.md`（匹配模式，扫包完成后） |
| Step 3 | 派改造员 | 读 `agents/modifier_agent.md`，将全文（填入变量后）作为子 Agent prompt |
| Step 4 | 派审查员 + 交付 | 读 `../_shared/reviewer_agent.md`，将全文（填入变量后）作为子 Agent prompt，`${MODE}` 填 "修改" |

> **同 session 轻量修复**（当前 session 刚完成该包的生成/修改，设计师指出具体问题）：  
> 免除 Step 2 的扫包三步（S1/S2/S3），但 M7 卡点、派改造员、派审查员**不可免除**。  
> 详见 `steps/workflow.md §1`。

---

## 三条核心禁令

| # | 禁令 |
|---|------|
| C1 | 有包体输入（zip/.ws）且当前 session 未扫过 → **必须立即扫包**，未扫不得出对比卡 |
| C2 | **M7 卡点**：未获设计师明确 OK（"确认/可以/OK"）→ 强制停止，不得动手 |
| C3 | 审查员返回**总体：PASS** 才允许交付，任一 FAIL → 重新派改造员+审查员 |

其余执行规则（block构建、validate、verify_gates等）已内嵌到各 `agents/` 文件对应步骤中。

---

## 子 Agent 速查

| 需要做什么 | 读哪个文件 | subagent_type | readonly |
|-----------|-----------|--------------|---------|
| 资源搜索（角色/物件/场景/动画） | `../_shared/resource_agent.md` | generalPurpose | true |
| 改造关卡 | `agents/modifier_agent.md` | generalPurpose | false |
| 交付前审查 | `../_shared/reviewer_agent.md` | generalPurpose | true |

> 审查员每次复审必须**新开子 Agent**，禁止 resume 复用。

---

## 路径规范

| 路径 | 说明 |
|------|------|
| `input/` | 设计师输入文件 |
| `参考/` | 已上线关卡 zip（只读） |
| `output/modify/{ORIG_NAME}-v{N}.zip` | 本模式输出（v 递增，不覆盖旧版） |
