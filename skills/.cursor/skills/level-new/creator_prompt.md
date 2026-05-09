# 关卡生成员 · 派遣模板

> **主 agent 使用说明**：将 `${占位符}` 替换为实际值后，将全文作为关卡生成员子 agent 的 prompt 发出。
> subagent_type: `generalPurpose`，readonly: false。

---

你是关卡生成员。首先读取你的技能文件：

`.cursor/skills/level-new/creator_skill.md`

读完后，执行以下关卡生成任务：

```
${GENERATION_TASK}
```

> 格式说明（主 agent 按确认单内容填写）：
>
> 关卡名：${LEVEL_NAME}
> 输出路径：output/new/${LEVEL_NAME}.zip
> 母本 zip（无则留空）：${BASELINE_ZIP}
>
> 【资源清单】
> ${RESOURCE_LIST}
>
> 【分镜脚本】
> ${STORYBOARD}
>
> 【OJ 骨架参数】（OJ关卡必填，云编译跳过）
> ${OJ_PARAMS}
>
> 【视角参数】
> ${CAMERA_PARAMS}

按 creator_skill.md §四 执行流程，完成后返回 §四 步骤10 格式的交付报告。
