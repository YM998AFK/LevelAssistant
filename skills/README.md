# PanGu Level Tools（盘古 3D 关卡生成工具）

面向盘古 3D 教育平台的编程关卡生成工作区。包含：

- `.cursor/skills/level-generator/`：Cursor Skill，按 10 步结构化流程生成关卡 zip 包。
- `.cursor/rules/`：项目级 Cursor 规则。
- `.cursor/hooks/` + `hooks.json`：交付前自检 hook。
- `scripts/`：批处理 / 分析脚本（生成素材目录、积木清单、角色用途、升级模板等）。

## 目录约定

| 目录 | 是否入库 | 说明 |
| --- | --- | --- |
| `.cursor/` | ✅ | Skills / rules / hooks，所有 AI 编排配置 |
| `scripts/` | ✅ | 源码脚本（临时文件 `_tmp_*` 会被忽略） |
| `input/`, `输入/` | ❌ | 原始素材输入，体积大不入库 |
| `output/`, `输出/`, `关卡输出/` | ❌ | 关卡产物 zip |
| `backup/` | ❌ | 旧版本备份 |
| `参考/`, `*-extracted/` | ❌ | 参考解包文件 |

## 开发流程

1. 在 Cursor 里说"创建一个关卡"触发 `level-generator` skill。
2. Skill 通过 10 步结构化提问收集关卡配置。
3. 生成前输出确认单，等待审核。
4. 生成完整的关卡 zip，落在 `output/`。
5. `hooks.json` 会在交付前运行 `pre_delivery_check.py` 做校验。

## 开发约定

- 所有脚本以 UTF-8 保存，Windows 下 git 已设置 `core.quotepath=false`。
- commit 一律走 main 分支，push 到 `origin`（Bitbucket 私有仓库）。
