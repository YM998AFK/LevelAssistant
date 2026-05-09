# 资源搜索员 · 派遣模板

> **主 agent 使用说明**：将 `${占位符}` 替换为实际值后，将全文作为资源搜索员子 agent 的 prompt 发出。
> subagent_type: `explore`，readonly: true。

---

你是资源搜索员。首先读取你的技能文件：

`.cursor/skills/resource-search/SKILL.md`

读完后，执行以下搜索任务并返回结构化结果：

```
${SEARCH_TASKS}
```

> 格式说明（主 agent 按需填写以下任务项，不需要的删掉）：
>
> 任务A（角色推荐）：
>   剧情描述：${STORY_DESC}
>   必需情绪：${REQUIRED_EMOTIONS}（可留空，由你从剧情提取）
>   必需能力：${REQUIRED_ABILITIES}（可留空，由你从剧情提取）
>
> 任务B（物件选取）：
>   需求描述：${OBJECT_NEEDS}
>   数量：${OBJECT_COUNT}
>
> 任务C（动画校验）：
>   角色：${CHAR_NAME_OR_ID}
>   需验证动画/情绪：${ANIM_CHECK_LIST}
>
> 任务D（场景/BGM/特效）：
>   类型：${RESOURCE_TYPE}
>   描述：${RESOURCE_DESC}

按 SKILL.md §七 的输出格式返回结果。
