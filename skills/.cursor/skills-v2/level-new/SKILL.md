---
name: level-new
mode: create_level
description: >-
  新建盘古3D编程关卡的主 Agent 编排手册。
  触发词：创建/生成/做一个XX练习/新建OJ关卡/制作教师端关卡。
  三步流程：发收集单 → 并行资源搜索+制作确认单 → 派生成员。
  输出 output/new/{LEVEL_NAME}.zip。
---

# 新建关卡主 Agent · 入口

> 你只做编排决策：收集需求、制确认单、等设计师 OK、派子 Agent。
> 不亲自搜索资源、不亲自写 BlockScript、不亲自打包。

---

## 触发判断

- **本模式**：创建/生成/做一个 XX 练习/新建 OJ 关卡/制作教师端关卡
- **跳转**：基于已有包改造 → 读 `level-modify/SKILL.md`
- **判断不了**：向设计师确认，不擅自假设

---

## 执行步骤索引

> 每步开始前才读对应文件，不要一次全部读入

| 步骤 | 内容 | 需要读的文件 |
|------|------|------------|
| Step 1 | 发一次性收集单，等设计师填完 | 读 `steps/workflow.md §1`（收集单模板在里面） |
| Step 2 | 【并行】派资源搜索员 + 主 Agent 推导方案 → 制确认单 → 等设计师 OK | 读 `steps/workflow.md §2`<br>派搜索员：读 `../_shared/resource_agent.md` |
| Step 3 | 派生成员 → 质检返回报告 → 交付 | 读 `agents/creator_agent.md`，将全文（填入变量后）作为子 Agent prompt |

> 审查员由**生成员**在其内部流程中派遣，主 Agent 无需另行操作。  
> 生成交付后，若设计师指出问题 → 切换到 `level-modify/SKILL.md` 同 session 轻量修复路径。

---

## 全局约束（编排开始前必读）

> **读 `../_shared/constraints.md`**，其中 M4（有歧义必问）/ M7（禁未 OK 派生成员）/ N10（禁止脑补剧情/资源）是硬性红线。

## 三条核心禁令

| # | 禁令 |
|---|------|
| C1 | 未收到设计师填完的收集单，不得进入 Step 2 |
| C2 | **M7 卡点**：未获设计师明确 OK（"确认/可以/OK"）→ 强制停止，不得派生成员 |
| C3 | 不亲自搜索资源、不亲自写 BlockScript——这两件事必须派专属子 Agent 执行 |

---

## 子 Agent 速查

| 需要做什么 | 读哪个文件 | subagent_type | readonly |
|-----------|-----------|--------------|---------|
| 资源搜索（角色/物件/场景/动画） | `../_shared/resource_agent.md` | generalPurpose | true |
| 新建关卡生成（含审查） | `agents/creator_agent.md` | generalPurpose | false |
| 交付前审查（由生成员派） | `../_shared/reviewer_agent.md` | generalPurpose | true |

---

## AI 自动填充（不问设计师）

| 项目 | 默认值 |
|------|-------|
| 成功/失败音效 | 28966 / 28965 |
| 全屏特效 | 通过 27888 / 不通过 27887 |
| UI 组件包 | Basic(27561) + Icons(27562) |
| UUID | 自动 v4 生成 |
| 产出路径 | `output/new/{LEVEL_NAME}.zip` |
