# 已知坑库 pitfalls v0

> **生成日期**：2026-04-23
> **语料**：61 包跨包分析 + 历史对话沉淀
> **用途**：新建/修改关卡前的"排雷清单"。每个坑有"现象 → 诊断 → 规避"三段式。
> **维护**：遇到新坑，加到 §99 临时坑区；三次复现后转正式条目。

---

## 使用方式

1. **开工前**：按"模式匹配"找相关坑（比如要用 F.tree 循环演出，先看 §2.1）。
2. **踩坑后**：优先查本文件，有则按"规避"去做；无则先解决再登记。
3. **登记新坑**：严格三段式，并标注至少 1 个复现的参考包路径。

---

## §1 · 骨架层坑（F.core 相关）

### P-1.1 ⚠️ cmd 三连广播少一个 → 判题完全静默

**现象**：关卡启动后 UI 正常进场，但输入代码后完全没反应，既不判对也不判错。

**诊断**：C-1 的 "init / cintest / couttest" 三连广播缺了任一一个。`judge` / `cin判断` / `cout判断` 没被触发。

**规避**：严格按 `cinematics.md` C-1：
```
SetVar(cmd, "init")     → Broadcast("运行")
SetVar(cmd, "cintest")  → Broadcast("运行")
SetVar(cmd, "couttest") → Broadcast("运行")
```
三条一个都不能省。即使没 cin（如无输入题），也要先 SetVar `*OJ-输入信息="0"`（见 L14-2-低-练习16 的写法）再走 cin 判断。

**来源**：跨 37 包共有模式，缺一即哑火。

---

### P-1.2 ⚠️ err_msg / state 未预置 → 失败分支显示为空

**现象**：触发失败时弹窗空白，没有错误文案。

**诊断**：v0 把 `err_msg` / `state` 当 L1 可选，实际 93% 共现，前端失败对话框依赖这两个变量。

**规避**：在 `WhenStartup` 里显式 SetVar：
```
SetVar(err_msg, "")
SetVar(state, "进行中")
```
写失败分支时**必须先 SetVar(err_msg, "<具体原因>")再 Broadcast(传递失败)**，不要直接 Broadcast。

---

### P-1.3 ⚠️ "*OJ-" 前缀变量被改名/赋值

**现象**：关卡挂载后云端判题永远 Judge=0，或学生 cin 永远为空。

**诊断**：`*OJ-输入信息 / *OJ-执行结果 / *OJ-Judge` 是**云端-关卡契约变量**，任何一处 SetVar 这三个会破坏契约。

**规避**：
- **只读不写**：关卡代码里**只读取**这三个变量，**只有 `WhenStartup` 的"清零"可以 SetVar** 成 `""`。
- 改名绝对禁止。

---

## §2 · F.tree 成长树族坑

### P-2.1 ⚠️ 挑战3 循环演出：n>10 完全哑火

**现象**：学生输入 `n=15` 这样的正常数字，关卡卡死，既不成功也不失败。

**诊断**：挑战3 的 T-4 循环演出有硬编码的 `if 0 < cin_cut[1] < 11` 外层保护，超出则**没有任何分支**处理，连失败都不走。

**规避**：
- **做新 F.tree 循环题**：去掉 `<11` 上限，或改成 `if cin_cut[1] > 0`（只下限），让大数值也走演出。
- 或者**显式处理越界**：额外分支 `else: SetVar(err_msg, "n 超出范围"); Broadcast(传递失败)`。
- **改老 F.tree 关卡**：优先查该 if 的上下界，若与题意不符必须调整。

**来源**：挑战3 的 control 节点 `WhenReceiveMessage("cout判断")`。

---

### P-2.2 ⚠️ 成长树展示缺"收起成长树"

**现象**：第一轮判题正确后成长树出现，但第二轮的成长树叠加在老的上面，屏幕越来越挤。

**诊断**：T-2 的 4 步 `收起 → 机器人右转 → 生成成长树 → 收起成长树` 是一个完整周期，缺 `收起成长树` 就没有回落。

**规避**：T-2 四步不能拆，不能省；判题每轮结束都要完整走一次。

---

## §3 · F.sundial 日晷族坑

### P-3.1 ⚠️ 一包多练 cid 只改一处 → 运行错题

**现象**：把练习5 母本 copy 成新关卡，改了一处 cid=2，但真跑起来仍然是练习5 的剧本。

**诊断**：`cid` 在**两处**被 SetVar：
- `WhenGameStarts` 里 1 次
- `WhenReceiveMessage("展示关卡效果")` 里 1 次

只改第一处，第二处会在结算时把 cid "回滚"，下一轮又回到老题。

**规避**：见 `modify_playbook.md` M-1。改 cid 的脚本或 MCP 操作**强制同步两处**。

**来源**：练习5 (`cid=1`) vs 练习7 (`cid=2`) vs 练习9 (`cid=3`) 三包仅差这两处。

---

### P-3.2 ⚠️ S-1 的 9 步顺序不能改

**现象**：日晷演出看起来对但最后没给出正确结果，或给出结果时位置错误。

**诊断**：S-1 的 `打开日晷 → 开启测算 → ... → 正确效果` 是 3 包字面量完全一致的 L9 序列，各 handler 依赖前一步的状态（如"凸显图标"依赖"测算分析"已经设好了指示哪个图标）。

**规避**：不要重排序，不要省略任何一步。即便觉得某步"多余"，也先看该包的 handler 内部是否在做副作用赋值。

---

## §4 · F.beast 机械兽族坑

### P-4.1 ⚠️ 分镜1 ↔ 分镜2 切换不同步 → 黑屏

**现象**：战斗演出中摄像机黑屏或卡在单侧。

**诊断**：B-1/B-3 里 `分镜1` 和 `分镜2` 是两个独立摄像机状态的切换 handler；handler 里若缺 camera reset 会留下前一镜头的尾巴。

**规避**：新建 F.beast 关卡时，把 ym / 挑战10 / 挑战12 对应的 `分镜1` / `分镜2` handler 原封不动抄过来（它们已经处理了 camera reset）。

---

### P-4.2 ⚠️ B-2 血量消息顺序错乱 → HP 算不对

**现象**：攻击回合 HP 展示跳跃（"满血 → 0 → 半血"乱跳）。

**诊断**：B-2 六步 `机械狗加血 → 机械狗格档 → 加血 → 机械狗被伤 → 机械狗被伤 → 减血` 是**加血先、格档后、被伤两次、减血最后** 的严格顺序，因为每个 handler 都在读上一步 SetVar 过的 `血量` 变量。

**规避**：严格按序列抄。血量变化全靠 handler 内部做，关卡外层只给 Broadcast 不要自己 SetVar `血量`。

---

## §5 · F.supplies 物资族坑

### P-5.1 ⚠️ 该族 L0 骨架不完整 → 云端判题路径断裂

**现象**：14-3-6/7/9 的 L0 变量覆盖只有 6/12，缺 `*OJ-Judge / cout_cut / n / space-flag / 输入元素 / 输出元素`。

**诊断**：该族使用了自研的 state 管道做判题，没走标准 `*OJ-Judge` 分岔。如以它为母本做"标准 OJ"题，会漏掉 cout 判断入口。

**规避**：
- **若题目真是简单清点（只需 cin 判断）**：可以继续用该族，不要强行塞 `cout判断` handler。
- **若题目需要 cout 判断**：**不要用该族做母本**，改用 F.tree / F.sundial 等标准族。

---

## §6 · F.fire 无人机灭火族坑

### P-6.1 ⚠️ 变长坐标记录硬编码 20 次 → N≠20 时卡住

**现象**：学生输入 `N=5` 只有 5 个火堆，但演出仍广播 `记录火堆6坐标 ~ 记录火堆20坐标`，屏幕上出现空挂点闪烁。

**诊断**：练习13/14/15 把 `for i=1..20: Broadcast("记录火堆"+i+"坐标")` 线性展开成 20 个独立 Broadcast，没有循环守卫。

**规避**：做新 F.fire 题用 `Repeat(N)` + `字符串拼接 Broadcast`（或用 `Variable("火堆索引")` 驱动的泛化 handler）。**不要**抄线性展开。

---

## §7 · F.forge 铸造族坑

### P-7.1 ⚠️ 14-4 挑战/练习 hat 数量爆炸（100+ fragments）

**现象**：新建 F.forge 包后打开工程卡死，加载缓慢。

**诊断**：14-4挑战16/练习14/15 有 100+ fragments，主要原因是字符串逐字符的 hat 展开。

**规避**：
- **优先用循环化的 FG-1 + FG-2 模板**，字符索引用 Variable 驱动。
- 若必须拆 hat（如不同字符有完全不同的演出），**用 UIView 归类管理**，不要全塞在 control 下。

---

## §8 · 场景结构坑

### P-8.1 ⚠️ Visible=False 的 UI 节点不可以挂 WhenGameStarts handler

**现象**：关卡首次进场时某些 UI 初始化没生效。

**诊断**：Visible=False 的节点在 WhenGameStarts 不被遍历调度；需要用 WhenStartup（场景总开场）或等待其他节点 Broadcast。

**规避**：
- UI 节点的初始化放在 `WhenReceiveMessage("初始化")` 里，由 control 节点的 WhenStartup 末尾 Broadcast("初始化") 触发。
- 不要在 UI 节点上直接写 WhenGameStarts。

---

### P-8.2 ⚠️ BlockScript 顶层节点 fragments 数一旦>100，保存会变慢

**现象**：导出 zip 慢，zip 压缩后 >200KB。

**诊断**：BlockScript 节点是顶层脚本容器，fragments 超过 100 后内部搜索变 O(N²)。

**规避**：
- 把逻辑拆到各 UI/MeshPart 节点自己的 BlockScript 下（就近原则）。
- control 节点只负责骨架（C-1~C-5）和族桥段调用。

---

## §9 · 编辑/工具链坑

### P-9.1 ⚠️ PowerShell 重定向 Python 输出 → 中文乱码

**现象**：`python foo.py > out.txt` 产生 UTF-16 BOM 文件或乱码。

**规避**：
- Python 脚本内直接 `open(path, "w", encoding="utf-8")` 写文件，**不要**靠 PowerShell 重定向。
- 必须控制台看：先 `chcp 65001 > $null; $env:PYTHONIOENCODING='utf-8'`。

---

### P-9.2 ⚠️ zip 双重命名嵌套 → extract 后多一层目录

**现象**：`参考-extracted/14-4练习14/14-4练习14/` 这种套娃结构。

**诊断**：zip 包内部含一个同名顶层目录。`ref_ingest.py` 已做兼容，但 `ref_scan.py` 会在最外层找 .ws 失败（.ws 在嵌套子目录）。

**规避**：
- `ref_scan.py` 目前查找 `pack_dir.iterdir()` 顶层，不会递归。如果漏掉，手工把嵌套层 move 到上一级，或在 ref_scan 内 `pack_dir.rglob("*.ws").next()`。
- 下次升级 ref_ingest 时自动拉平嵌套层。

---

### P-9.3 ⚠️ 修改 .ws 后未重跑 ref_scan → _analysis.md 陈旧

**现象**：改完关卡内容，`_analysis.md` 还是旧数据。

**规避**：改完后跑 `python scripts/ref_scan.py <dir>` 刷新。批量刷新：`python scripts/ref_ingest.py --rescan-only --json`。

---

## §10 · 多 Agent 协作坑（来自 SKILL.md §0.9 延伸）

### P-10.1 ⚠️ 并行 agent 同时 ref_ingest → 生成 _analysis.md 冲突

**现象**：多个 agent 同时解压/扫描，`_analysis.md` 被覆盖不一致。

**规避**：
- ref_ingest 不应并行运行。若需多 agent 协作：主 agent 跑 ingest，子 agent 只读 `_analysis.md` 和 `suggestions.md`。
- 若必须并行写，改用 `--pack-dir` 单包模式，各自只写自己的 dir。

---

## §11 · 场景摆放 / MeshPart 可见性坑

### P-11.1 ⚠️ MeshPart Visible=False 且无 Size → 编辑器里完全隐形

**现象**：路标 / 巡逻点等纯逻辑 MeshPart 设置了 `Visible=False`，
在编辑器中连线框都找不到，和"不存在"没有区别。

**诊断**：编辑器的线框 gizmo 依赖 `Size` 属性来绘制碰撞体轮廓。
`Visible=False` 只关掉网格渲染；如果同时缺少 `Size`，
碰撞体轮廓也没有可绘制的尺寸，gizmo 完全消失。

**规避**：凡是"空盒子"型 MeshPart（不需要渲染、仅作位置标记）：
```json
"Size": ["1", "1", "1"],
"Visible": false
```
加了 `Size` 后编辑器会显示白色线框，便于调试定位；对游戏运行无影响。

**参考包**：`output/modify/抗寒跑操-小核桃队长展喵-v6.zip`（P1-P4 vs L1-L3 对比）

---

### P-11.2 ⚠️ 以 navmesh 边界点作为 waypoint → 坐标贴墙/跑出房间

**现象**：路径顶点落在场景墙根 / 家具背面，角色跑操时贴墙或穿模。

**诊断**：NavMesh 边界点 = 可行走面的最外缘；BoundsCenter 未必等于可行走区域质心，按比例外推的顶点可能在障碍物内。

**规避（MCP v0.0.4+）**：

场景元素位置直接用 `ws_update_scene_element_position` + navmesh 贴地：

```json
{
  "element_name": "P1",
  "position": [10, 99, -6],
  "navmesh": { "enabled": true, "max_sample_distance": 2, "strict": true }
}
```

贴地后 Y 自动更新为 NavMesh 高度；`strict=true` 时采样失败会报错，不会静默写入越界坐标。

需要精细脚本生成多点时，用 `navigation.scene_navmesh` API：

```python
from navigation.scene_navmesh import sample_scene_position, find_scene_closest_edge
result = sample_scene_position(scene_id, [x, y, z], max_dist=2).to_dict()
edge = find_scene_closest_edge(scene_id, [x, y, z]).to_dict()
# edge["distance"] < 1.0 时换点
```

另：`validate_workspace` 会自动检测 `WalkToTarget` / `RunToTarget` 积木的目标落点合法性（scene_resource_id 存在时），无需手写校验脚本。`GotoPosition3D` 等直接坐标移动积木不参与 NavMesh 检测。

**参考包**：`output/modify/抗寒跑操-小核桃队长展喵-v6.zip`

---

### P-11.3 💡 navmesh 坐标与 ws.Position 单位关系（2026-04-28 实测）

**结论**：`navmesh_loader` 输出的 XZ 坐标与 `.ws` 文件 `Position[0]` / `Position[2]` 
**数值上 1:1 直接对应**（同为 Unity 世界坐标 ws 单位）。
- `Position[1]`（高度）直接取 navmesh 对应顶点的 Y 值即可，不需乘以 30。
- "×30 = 编辑器 cm" 是给人看编辑器时用的换算，不影响 `.ws` 写值本身。

| 换算方向 | 公式 |
|---|---|
| ws → 编辑器显示 | `editor_X(cm) = Position[0] × 30`（前后）；`editor_Y(cm) = Position[2] × 30`（左右）；`editor_Z(cm) = Position[1] × 30`（高度）|
| navmesh vert → ws | `Position[0] = vert[0]`；`Position[2] = vert[2]`；`Position[1]` 取 navmesh Y 或场景常用地面高度 |

---

## §99 · 临时坑区（未满 3 次复现）

| 坑 | 现象 | 复现次数 | 备注 |
|---|---|---|---|
| （占位）| | 0 | |

> 任何一行积累到 3 次复现，转正式 §1~§10。

---

## 相关文档

- `cinematics.md` —— 演出桥段库 v1
- `oj_standard_vars.md` —— 变量/消息 checklist v1
- `modify_playbook.md` —— 改关卡模式库
- `SKILL.md` §0.9 —— 多 Agent 协作规则

---

## 修订记录

- **v0（2026-04-23）**：首版，合并历史对话里明确踩过的坑 + 跨 61 包新挖掘的坑。10 条正式条目。
- **v1（2026-04-28）**：新增 §11 场景摆放 / MeshPart 可见性三条（P-11.1 空盒子无 Size 隐形、P-11.2 navmesh 边界贴墙、P-11.3 坐标单位实测说明）。来源：抗寒跑操 v6 开发对话。
- **v2（2026-05-09）**：§11.2 手写 navmesh 脚本替换为 MCP v0.0.4 `ws_update_scene_element_position` + `navigation.scene_navmesh` API。
