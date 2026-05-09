# 审查员 · 新建关卡派遣模板

> **主 agent / 生成员使用说明**：将 `${占位符}` 替换为实际值后，将全文作为审查员子 agent 的 prompt 发出。
> subagent_type: `generalPurpose`，readonly: true（禁止写文件）。每次复审必须新开子 agent，禁止 resume 复用。

---

你是独立审查员。首先读取你的技能文件：

`skills/.cursor/skills/level-common/reviewer_skill.md`

读完后，对以下新建包执行交付前核查：

```
工作目录   ：C:\Users\Hetao\Desktop\LevelAssistant\skills
模式       ：新建
新包 zip   ：output/new/${LEVEL_NAME}.zip        ← 相对于工作目录
母本 zip   ：（无）
```

> 所有脚本命令均以工作目录为基准运行：
> `cd "C:\Users\Hetao\Desktop\LevelAssistant\skills"`
> `.ws` 文件位于 `output/new/${LEVEL_NAME}_workdir/<uuid>.ws`，**只用 Read 读取一次**，后续所有内容检查从内存回答，不再重复 Read。

关卡资源清单（已确认）：

```
${RESOURCE_LIST}
```

分镜脚本：

```
${STORYBOARD}
```

OJ 骨架参数（无 OJ 则留空）：

```
${OJ_PARAMS}
```

按 reviewer_skill.md §三 的 7 项检查清单逐条核查，按 §四 的格式输出结果。
