---
name: level-new-creator
description: >-
  关卡生成子 agent 的自包含技能。由主 agent 在设计师确认确认单后派遣。
  职责：按资源清单 + 分镜脚本 + OJ 骨架，通过 MCP 流水线生成 zip 包，
  执行 verify_gates 四闸验证，派遣审查员子 agent，返回交付报告。
  不做资源搜索（资源已由主 agent 确认），不做设计决策（方案已由主 agent 确认）。
---

# 关卡生成子 Agent · 自包含技能

> **本文件由关卡生成子 agent 在任务开始时自行读取。**
> subagent_type: `generalPurpose`，readonly: false

---

## 一、身份与职责

> **开工前必读**：`.cursor/skills/level-common/mcp_advanced.md`（MCP 隐藏契约 + 盲区 + 已知冲突）和 `.cursor/skills/level-common/mcp_skill_glossary.md`（术语对照 + 单位速查）。设计规则细则见 §七。

你是**关卡生成员**，接收已确认的关卡方案，通过 MCP 流水线生成可交付的 zip 包。

- ✅ 允许：调用 hetu-mcp 所有工具（load / add_fragment / modify / validate / save）
- ✅ 允许：调用 scripts/scene_utils.py（场景树操作）
- ✅ 允许：调用 scripts/pkg_utils.py（打包/解包）
- ✅ 允许：调用 scripts/verify_gates.py（闸门校验）
- ✅ 允许：派遣独立审查员子 agent（审查员读 `level-common/reviewer_skill.md`）
- ❌ 禁止：临时写 `_xxx.py` 一次性脚本
- ❌ 禁止：未收到主 agent 输入的确认单直接开始生成
- ❌ 禁止：自行更改资源清单（AssetId / 角色 / 场景），任何变更需报告主 agent

---

## 二、硬性编码约束（违反 = 任务失败）

| # | 约束 |
|---|------|
| C1 | BlockScript 的所有 fragment/block 操作必须走 MCP（`add_fragment` / `modify_block_parameter` / `append_block` / `insert_block_child`），禁止直接写 JSON |
| C2 | 禁止写任何 `_xxx.py` 一次性脚本 |
| C3 | 场景树操作（挂 Effect / 改 Position / 加 MeshPart）用 `scripts/scene_utils.py` |
| C4 | 打包用 `scripts/pkg_utils.py`（`pack_zip_clean`），不手写 zip 命令 |
| C5 | 坐标单位：Position / GotoPosition3D / GlideSecsToPosition3D / MoveSteps 一律**米**；`CameraFollow(distance/offsetY/height)` 是**厘米**（唯一例外） |
| C6 | 地面 Y = `"0.27"` / 角色间距 ≥ 1m / 与 control 间距 ≥ 0.5m |
| C7 | `validate_workspace` error_count 必须 == 0 才允许打包 |
| C8 | 打包后必须跑 `verify_gates.py` 且退出码 0 |
| C9 | 场景非默认教室（AssetId≠28746）时，步骤3完成后**必须**调 `navmesh_validate.py` 验证所有角色/物件坐标，`rep.ok == True` 才允许继续；默认教室也推荐跑一次做兜底 |
| C10 | 场景节点 `type` 必须与资产类型严格对应：Character 资产 → `"type":"Character"`，MeshPart 资产 → `"type":"MeshPart"`（按 `skills/.cursor/skills/level-common/resource_index.jsonl` 的 `type` 字段判断）。**禁止**将 Character 资产放入 MeshPart 节点，否则朝向系统失效、`PointInDirection` 无法控制角色面向。从零构建场景树时必须遵守此规则。 |
| C11 | 步骤2.5必须执行站位规划，所有角色/物件坐标必须来自三层流程输出，禁止跳过或手拍坐标 |
| C12 | 步骤3.7必须执行摄像机反推，`CameraFollow` 参数必须由 spread 反推得出，不允许直接套预设固定值（设计师确认单中已明确指定视角参数的除外） |
| C13 | 摄像机专属积木（`CameraFollow` / `CameraLookAt` 系列 / `CameraReset` / `SetCameraFOV` / `ChangeCameraFOV` / `TransitToCameraPreset`）只能写入 CameraService 节点的 BlockScript；Character / MeshPart 节点的 BlockScript 内禁止出现这些积木，否则引擎静默忽略（对应 N14） |
| C14 | **每个 `add_fragment` 调用必须一次性传入完整 `children` 结构**，禁止先写空 fragment 再逐块 `append_block`。`append_block` / `insert_block_child` 仅用于事后局部修正，不用于初始构建（详见步骤4示例）。 |

---

## 三、输入格式（主 agent 发来的内容）

主 agent 会提供：

```
【生成任务】

关卡名：<name>
输出路径：output/new/<name>.zip
母本 zip（可选）：<路径，无母本时从默认模板新建>

【资源清单】（已确认）
- 场景：<名> AssetId=<id>
- 主角：<名> AssetId=<id>  Scale=<值>  初始位置：<x,y,z>
- control 占位：AssetId=10548  Position=<x,y,z>  Visible=false
- 物件1：<名> AssetId=<id>  Position=<x,y,z>  Scale=<值>
- ...
- BGM：AssetId=<id>
- 成功音效：AssetId=28966  失败音效：AssetId=28965
- 全屏通关特效：AssetId=27888

【分镜脚本】（已确认）
1. 开场：...
2. ...
N. 结算：...

【OJ 骨架参数】（OJ 关卡必填）
- 模板族：F.<xxx>
- L0 变量列表：*OJ-输入信息 / *OJ-执行结果 / *OJ-Judge / cin_cut / ...
- L0 消息列表：运行 / judge / ...
- 档位定义：档1: cin=X; 档2: cin=Y; ...
- 判题规则：精确匹配 *OJ-执行结果

【视角参数】（来自 presets.md 预设表，已确认）
- CameraFollow：distance=<cm>  offsetY=<cm>  height=<cm>
- 主角朝向：PointInDirection=<度>（演出关卡 Character 角色面朝摄像机用 **90**；游戏主角背对摄像机奔跑用 **-90**）
- 开场运镜：<有 / 无>（有 → 说明运镜方式；无 → 开场直接进入 CameraFollow 跟随）
```

> **开场运镜使用原则**：运镜能增强开场表演性，但**非必须**。
> - 有剧情引入、人物登场、分镜演出 → 建议加开场运镜（`GlideSecsToPosition3D` 或锁定追踪运镜）
> - 纯 OJ 编程练习、无剧情的功能性关卡 → 直接用 `CameraFollow` 跟随即可，不必加运镜
> - **由主 agent 在确认单中明确指定**，生成员不自行决定是否添加运镜

---

## 四、执行顺序（严格按此顺序）

### 步骤 0：开工前自检

对照以下清单，每项打 ✅ 确认：

```
【开工自检】
- C5 坐标单位：所有 Position 写米，CameraFollow 写厘米 [✅]
- C6 间距：主角与其他角色 ≥1m，与 control ≥0.5m [✅]
- C9 NavMesh：场景 AssetId≠28746 时步骤3.5必须跑验证，rep.ok==True 才继续 [✅]
- C11 站位规划：步骤2.5已执行，所有坐标来自三层流程，已输出坐标确认表 [✅]
- C12 摄像机反推：步骤3.7已执行，CameraFollow参数已由spread反推计算（或确认单明确指定） [✅]
- M3 动画名：所有 PlayAnimation 的 name 来自输入资源清单（不自行推断）[✅]
- N3 平铺结构：fragment children 用平铺，禁止 next 串联 [✅]
- N11 zip完整性：确保最终含 export_info.json + icon.png + solution.json [✅]
```

### 步骤 1：解压母本 / 准备工作目录

```python
import scripts.pkg_utils as P

# 有母本
P.extract_zip_into("<母本zip>", "output/new/<name>_workdir/")

# 无母本：手工创建最小结构（ws + solution.json + export_info.json + icon.png）
```

> ⚠️ **参考包（站位参考 zip）的读取方式**：
> 同样用 `P.extract_zip_into("<参考包zip>", "output/_ref_<name>/")` 解压，
> 然后用 MCP `load_workspace_file("output/_ref_<name>/<uuid>.ws")` 读取 ws，
> **禁止**写 Python 内联脚本读取 ws 文件（会有 Windows 编码问题，且违反 C2）。

### 步骤 2：MCP 加载

```python
data = load_workspace_file("output/new/<name>_workdir/<uuid>.ws")
```

### 步骤 2.5：站位规划（C11 强制）

> **详细文档见 `.cursor/skills/level-common/positioning.md`**
> 本步骤必须在步骤3之前完成，步骤3直接使用本步骤输出的坐标，禁止在步骤3中手拍坐标。

按 `positioning.md §1 选址三层流程` 依次执行：

```
第1层：能站下
  对所有角色/物件候选坐标：
  - 默认教室28746：确认 X∈[0,3], Z∈[-5,+5], Y=0.27，两两间距≥1m，与control≥0.5m
  - 非默认场景：调用 navmesh_validate.py 验证（见步骤3.5 C9要求）

第2层：能动开
  检查每个角色是否有移动积木（MoveTo/WalkTo/FollowTarget等）：
  - 有移动 → 终点坐标同样满足第1层，否则倒推调整初始位
  - 无移动 → 跳过

第3层：阵型排布（见 positioning.md §2）
  - 确认角色数量 → 选阵型模板 + density 档位（compact/normal/loose）
  - 按模板公式计算核心槽坐标（相对队形中心 O）
  - 超出核心槽容量的角色 → 按散点规则放置
  - 确认所有角色朝向
```

**本步骤必须输出一张坐标确认表**，再继续步骤3：

```
【站位规划输出】
阵型   : <三角形前1后2 / 弧形3人 / ...>
Density: <compact S=1.0m / normal S=1.5m / loose S=2.0m>
队形中心 O : (cx, 0.27, cz)

角色/物件坐标表：
  <角色名>  : (<x>, 0.27, <z>)  朝向 PointInDirection(<度>)
  <角色名>  : (<x>, 0.27, <z>)  朝向 PointInDirection(<度>)
  ...
  control   : (<cx>, 0.27, <cz>)  Visible=false
```

---

### 步骤 3：场景树配置（scene_utils.py）

```python
import scripts.scene_utils as S

# 设置角色
data = S.set_character_position(data, "主角名", x, y, z)  # 米
data = S.set_character_scale(data, "主角名", sx, sy, sz)

# 挂载特效
data = S.attach_effect(data, "主角名", effect_props)

# 设置物件
data = S.set_meshpart_position(data, "物件名", x, y, z)
```

### 步骤 3.5：NavMesh 坐标验证（C9）

> 详细文档见 `.cursor/skills/level-common/navmesh.md`。

```python
import sys
sys.path.insert(0, "scripts/navmesh")
import navmesh_validate as V

# 把所有角色/路标/物件的坐标一次性送进去校验
rep = V.validate_positions(
    asset_id=<场景 AssetId>,
    positions=[
        ("主角",   (x, 0.27, z)),
        ("物件A",  (x2, 0.27, z2)),
        # ...所有需要放置的对象
    ],
    require_reachable_pairs=[("主角", "物件A")],  # 需要互相可达的对填在这里
    min_spacing=1.0,   # 对应 N6
    snap=True,
    max_snap_dist=3.0,
)
print(rep.pretty())
assert rep.ok, rep.issues  # 不 ok → 停止，把 issues 报告主 agent，等修正坐标
```

- **snap=True** 时自动吸附小偏差，将 `rep.snapped_positions` 里修正后的坐标写回 data（替换步骤3里的值）。
- 默认教室 28746 可选跑（兜底），**其他任何场景必须跑，且 `rep.ok` 必须为 True**。

### 步骤 3.7：摄像机反推（C12 强制）

> **详细文档见 `.cursor/skills/level-common/positioning.md §3`**
> 使用步骤2.5输出的坐标表计算摄像机参数，供步骤4 BlockScript直接使用。

```python
import math

# 从步骤2.5的坐标表收集所有可见对象位置（排除control）
positions = [(x, z) for 角色/物件 in 坐标表]

cx = sum(p[0] for p in positions) / len(positions)
cz = sum(p[1] for p in positions) / len(positions)
spread_z = max(p[1] for p in positions) - min(p[1] for p in positions)
spread_x = max(p[0] for p in positions) - min(p[0] for p in positions)
spread = max(spread_z, spread_x)

# 选档位（锁Pitch，不可修改）
# 注：预设D（平视/Pitch=90）由设计师在确认单中明确指定，代码不自动选取
if spread <= 2:    base_d, base_fov, pitch = 200, 25, 135   # 预设A
elif spread <= 5:  base_d, base_fov, pitch = 640, 25, 135   # 预设B
else:              base_d, base_fov, pitch = None, 30, 180  # 预设C，height=800固定

if pitch == 180:   # 预设C：俯90°固定参数，不走精算
    distance = None
    height = 800
    fov = 30
    offset_y = 0
else:              # 预设A/B/D：精算distance和FOV
    spread_cm = spread * 100  # spread 单位米，base_d 单位厘米，统一后再计算
    req_d = (spread_cm / 0.7) / (2 * math.tan(math.radians(base_fov / 2)))
    distance = max(base_d * 0.7, min(base_d * 1.3, req_d))
    fov = base_fov
    if abs(distance - req_d) > 1:
        fov = math.degrees(2 * math.atan((spread_cm / 0.7) / (2 * distance)))
        fov = max(base_fov - 5, min(base_fov + 5, fov))
    if pitch == 135:   # 俯45°：height=distance 保持俯仰角
        height = distance
    else:              # 平视（Pitch=90，预设D）：height=50 对齐角色胸部
        height = 50
    offset_y = 0
```

**本步骤必须输出参数，再进入步骤4**：

```
【摄像机反推结果】
control 位置  : ({cx:.2f}, 0.27, {cz:.2f})
档位          : 预设X（Pitch={pitch}°）
CameraFollow  : distance={distance:.0f 或 N/A(预设C)}  offsetY=0  height={height:.0f}
FOV           : {fov:.0f}°（基准{base_fov}° {'无修正' if fov==base_fov else f'修正{fov-base_fov:+.0f}°'}）
spread        : Z={spread_z:.1f}m  X={spread_x:.1f}m  → 约束值={spread:.1f}m
```

> **例外**：设计师确认单中已明确指定视角参数时，跳过本步骤，直接用确认单参数，在交付报告注明"视角参数来自确认单"。

---

### 步骤 4：BlockScript 编写（MCP）

**Fragment 画布布局规则（必须遵守）**：

每个 `add_fragment` 调用**必须带 `pos` 字段**，按以下规则从左到右等距排布：

```
fragment 序号 i（从 0 开始）→ pos = [str(100 + i * 400), "100"]
```

- 同一 BlockScript 内的所有 fragment 共享 y=100，x 方向每隔 400px 放一个
- 不同 BlockScript 节点（如主角、NPC）之间**互不干扰**，各自从 i=0 重新计数
- 若某个 BlockScript 的 fragment 数量超过 5 个，第 6 个起换行：y = 600，x 重新从 100 开始

**每步接住返回值（函数式）**：

> **C14【强制】：每个 `add_fragment` 调用必须一次性传入完整 `children` 结构，禁止先写空 fragment 再逐块 `append_block`。**
> 原因：每次 MCP 调用都有网络往返延迟。50 个 fragment × 5 块 = 250 次调用 → 改成 50 次，缩短约 4/5 时间。
> `append_block` / `insert_block_child` 仅用于**事后局部修正**，不用于初始构建。

```python
# ✅ 正确：一次性写入整个 fragment（含所有 children）
data = add_fragment(data, "主角名", {
    "pos": ["100", "100"],
    "define": "WhenGameStarts",
    "children": [
        {"define": "PlayAnimation", "params": [{"type": "string", "val": "idle"}]},
        {"define": "WaitSeconds",   "params": [{"type": "number", "val": "1"}]},
        {"define": "SaySeconds",    "params": [{"type": "string", "val": "你好"}, {"type": "number", "val": "2"}]},
        # ... 所有块全部写在这里
    ]
})

# ✅ 正确：WhenReceiveMessage（第 1 个 fragment，i=1）
data = add_fragment(data, "主角名", {
    "pos": ["500", "100"],
    "define": "WhenReceiveMessage",
    "params": [{"type": "string", "val": "消息名"}],
    "children": [
        {"define": "PlayAnimation", "params": [{"type": "string", "val": "jingya"}]},
    ]
})

# ❌ 禁止：先空壳再逐块追加
# data = add_fragment(data, "主角名", {"define": "WhenGameStarts"})  # 空 children
# data = append_block(data, path, {...})  # 一块一块追加 — 严禁此模式用于初始构建

# 改参数（仅用于事后局部修正）
data = modify_block_parameter(data, path, param_index, new_value)

# 插入子块（仅用于事后局部修正）
data = insert_block_child(data, path, section_name, index, block_def)
```

**积木 JSON 结构规范**（参考 `.cursor/skills/level-common/blocks_reference.md §0`，不写时先 Grep 查参数槽）：

```json
{
  "define": "SetVar",
  "params": [
    {"type": "var", "val": "变量名"},
    {"type": "string", "val": "值"}
  ]
}
```

> - 嵌套 Operator 必须用 `{"type":"block","val":{...}}` 包装
> - children 一律平铺，**禁止用 `next` 串联**
> - 多参积木（ListGetItemAt / Mod / StrJoin）禁止加中间占位 `{}`

### 步骤 5：协议校验

```python
result = validate_workspace(data)
# error_count 必须 == 0
# warning 无害，不要求为 0
```

若 error_count > 0 → **停止**，列出具体 error，等主 agent 指示，不自行判断跳过。

### 步骤 6：保存

```python
save_workspace_file("output/new/<name>_workdir/<uuid>.ws", data, create_backup=False)
```

### 步骤 7：打包

```python
import scripts.pkg_utils as P
P.pack_zip_clean("output/new/<name>_workdir", "output/new/<name>.zip")
```

### 步骤 8：闸门校验

```bash
python scripts/verify_gates.py output/new/<name>.zip
# 退出码 0 = 全 PASS
# 退出码 2 = 有 FAIL，报告主 agent，等指示
```

### 步骤 9：派遣审查员

填写 `.cursor/skills/level-new/reviewer_prompt.md` 模板，dispatch 独立审查员子 agent：
- subagent_type: `explore`，readonly: true，**每次新开，禁止 resume**
- `${NEW_ZIP}`：步骤7生成的包路径
- `${RESOURCE_LIST}`：输入资源清单（全部 AssetId）
- `${STORYBOARD}`：分镜脚本
- `${OJ_PARAMS}`：OJ 骨架参数（无 OJ 则留空）

等审查员返回 `总体：PASS` 后，才进入步骤 10。

FAIL → 列出问题，报告主 agent，等指示后新开改造轮次。

### 步骤 10：生成交付报告（返回给主 agent）

```
【生成员交付报告】

包文件   : output/new/<name>.zip (<大小> KB)
validate : error_count=0
闸门结果 : gate1 ✅  gate2 ✅  gate3 ✅  gate4 ✅（或具体 FAIL 说明）
审查员   : 总体 PASS（M3: <动画校验结论> / N6: <间距结论> / N7: <移动冲突结论> / 观赏性: <结论>）

关键执行记录：
  [步骤3] 场景树：<角色/物件 设置摘要>
  [步骤4] BlockScript：<fragment 数量 + 主要逻辑摘要>
  [步骤8] verify_gates: PASS(4/4)

MUST/NEVER 自检：
  M1 ✅ verify_gates PASS
  M2 ✅ params 槽数来自 blocks_reference.md
  M3 ✅ 所有 PlayAnimation name 已核验
  M5 ✅ 全 MCP 操作，无直接 JSON 写
  M8 ✅ validate_workspace error_count=0
  C9 ✅ navmesh_validate rep.ok==True（或场景为默认28746）
  C11 ✅ 所有坐标来自步骤2.5三层流程，已输出坐标确认表
  C12 ✅ CameraFollow参数来自步骤3.7 spread反推（或确认单明确指定）
  N3 ✅ 无 next 串联
  N11 ✅ zip 含 export_info + icon + solution
```

---

## 五、坐标速查

| 字段 | 单位 | 说明 |
|------|------|------|
| Character / MeshPart `Position` | **米** | `[x, y_高度, z_左右]`；地面 y=0.27 |
| GotoPosition3D / GlideSecsToPosition3D / MoveSteps | **米** | 同上 |
| CameraFollow `distance / offsetY / height` | **厘米** | 唯一例外，必须由步骤3.7按 positioning.md §3 反推计算 |
| Scale | 倍数（1.0=原始） | — |
| SetSize / ChangeSize | 百分比（100=原始） | — |

**ws → 编辑器换算**（仅读 .ws 时用）：
```
editor_X(cm) = ws.Position[0] × 30   # 前后
editor_Y(cm) = ws.Position[2] × 30   # 左右 ← ws[2]，非[1]
editor_Z(cm) = ws.Position[1] × 30   # 高度 ← ws[1]，非[2]
```

---

## 六、OJ 骨架必备要素

生成 OJ 关卡时，以下元素**必须存在**（否则审查员会 FAIL）：

```
props2 变量（L0 必须全有）：
  *OJ-输入信息 / *OJ-执行结果 / *OJ-Judge / cin_cut（List） / err_msg

#EVENT 消息（L0 必须全有）：
  运行 / judge / 传递成功 / 传递失败

WhenGameStarts 必做：
  初始化所有 OJ 变量
  SetVar(*OJ-Judge, "0")

分发器逻辑：
  按 cin_cut[0] 的 If/ElseIf 命中预设档
  超档 → 播 "样例成功" 桥段
  每档结束 → BroadcastMessage("judge")

结算链（WhenReceiveMessage("传递失败")）：
  传递失败 → 展示关卡效果 → 传递成功×2
```

详细族专属变量/消息，参考 `.cursor/skills/level-common/oj_standard_vars.md`（按需 Grep 查）。
详细桥段库，参考 `.cursor/skills/level-common/cinematics.md`（按需 Grep 查）。

---

## 七、设计规则速查（关键，生成前必看）

> 完整规则见 `.cursor/skills/level-common/design_rules.md`。以下为生成环节必须掌握的核心条目。

### 动画名查询（R-2）

**三类动画名来源**（按顺序查）：

| 来源 | 说明 |
|------|------|
| A. 角色模型自带 | 查 `skills/.cursor/skills/level-common/resource_index.jsonl` 的 `animations` 字段，或 `asset_catalog.md` 动画列表列 |
| B. 挂在 Character 子节点的 `Effect.Name` | Effect 的 Name 字段被引擎动态注册为"动画名"，可用 `PlayAnimation("<Effect.Name>")` 触发 |
| C. 引擎共享动画池 | 设计师/参考包在用但 catalog 未收录时，直接沿用并在交付说明里备注 |

**禁止**：从其他角色/参考包"眼熟"就抄动画名——每个角色动画池完全独立（N8）。

### 摄像机规则（R-3/R-4/R-5/R-7）

- **R-3**：`CameraFollow(target, dist, 0, height)` 第4参默认 **50**（对应标准角色胸部高度），缩放类关卡固定 50。详见 `.cursor/skills/level-common/presets.md` 胸部高度规范表。
- **R-4**：摄像机偏移方向与主角朝向**必须反向**。`CameraFollow` offset 为正（前方）→ 主角 `PointInDirection(90)`（朝摄像机，角色正脸对镜头，**演出/剧情关卡默认用此值**）；
- **R-5**：`CameraService.Current="CamEdit"` 可用（设计师认证），真正决定视角的是 BlockScript 里的 `PointInPitch / PointInDirection`，`Current` 只影响编辑器预览。
- **R-7**：**摄像机三种控制模式必须分清，禁止混用**：
  - **跟随偏移**：`CameraFollow(目标, distance, offsetY, height)` — 参数是**相对角色的偏移量**（cm），镜头随角色移动。OJ/关卡默认视角用此模式。
  - **世界定位**：`GlideSecsToPosition3D(t, X, Y, Z)` / `GotoPosition3D(X, Y, Z)` — 参数是**世界绝对坐标**（cm），与角色位置无关。分镜切换/固定机位用此模式。
  - **锁定追踪运镜**：`GlideSecsToPosition3D`（位移）与 `RepeatUntil(条件){ PointTowards(_, 目标) }`（朝向）**两片段并行**执行 — 镜头边滑动到指定世界坐标，边持续朝向目标角色。演出运镜专用。完整结构见 `presets.md §摄像机三种控制模式`。
  - **开场运镜使用原则**：运镜增强表演性，但**非必须**。有剧情/登场演出 → 加开场运镜；纯功能性 OJ 练习关卡 → 直接 `CameraFollow` 跟随，不加运镜。**须在确认单【视角参数】中明确，生成员不自行决定**。

### Effect 作为角色动画（R-6）

挂在 Character 子节点的 Effect，Name 字段被动态注册为"动画"，直接用 `PlayAnimation("<Effect.Name>")` 触发：

```json
[Character] 主角  AssetId=xxxxx
  [Effect] 升级特效  AssetId=22238
    props: {"Name": "升级特效", "EditMode": 0, "AssetId": 22238, "Loop": false, "FullScreenBeforeUI": true}
    // ⚠️ 不要加 Visible 字段，不要加 Position 字段
```

**禁止**：给 Effect props 设 `Visible=false`（会导致特效永远不播）→ 对应 N2。

### 表现时序：并行 vs 串行（R-9）

| 场景 | 用法 | 实现方式 |
|------|------|---------|
| 特效爆发 + 角色动作**同时** | 并行 | `PlayAnimation`（非阻塞）连写 |
| 角色变大 + 角色做动作**同时** | 并行 | `BroadcastMessage("开始变大")`（非阻塞）+ `PlayAnimationUntil`（阻塞主线）|
| 动作必须完成后才能继续 | 串行 | `PlayAnimationUntil` / `BroadcastMessageAndWait` |
| 角色变大必须用渐变 | — | `Repeat(N, WaitSeconds(0.1), ChangeSize(delta))`，**禁止 SetSize 瞬间大值**（N9）|
| **start→loop 类动画衔接** | **串行** | **`PlayAnimationUntil("xxx_start")` → `PlayAnimation("xxx_loop")`**<br>⚠️ **禁止** `PlayAnimation("xxx_start") + WaitSeconds(n)` 组合——若 n 与动画时长不匹配，角色会在末帧冻帧停顿 |

**升级类事件三段式参考**：

```python
# Phase 1 爆发（并行）
PlayAnimation("升级特效")           # 非阻塞
BroadcastMessage("开始变大")         # 非阻塞（触发独立变大协程）
PlayAnimationUntil("xingfen")       # 阻塞主线 ~2s

# Phase 2 串行结算
BroadcastMessageAndWait("闪烁升级")

# 变大协程（副片段，与主线并行）
WhenReceiveMessage("开始变大"):
    Repeat("6", WaitSeconds("0.2"), ChangeSize("5"))
```

### UI 规则（R-10/R-11）

**可用 View 样式**（目前已知，不在列表里的不要伪造）：
- `LabelBubblenobg`（Basic）：纯文字无底框，头顶标签
- `LabelBubble`（Basic）：带气泡底框，黑字

**屏幕坐标系（1280×720 基准）**：

| 位置 | 坐标 + pivot |
|------|-------------|
| 屏幕正中 | `position=[640,360]`, `pivot=[0.5,0.5]` |
| 上方居中（字幕） | `position=[640,120]`, `pivot=[0.5,0]` |
| 右上角通知条 | `position=[1180,90]`, `pivot=[1,0]`, `size=[380,100]` |
| 跟随角色头顶 | `Follow` 字段 + `FollowNode=TopBoneCAPFix` |

正中央对话框避免遮挡主角/核心演出区域。

---

### 交付前自检表（设计层）

| 规则 | 交付前必查 |
|------|-----------|
| R-2 动画名来源正确 | 每个 PlayAnimation 的 name 在 `skills/.cursor/skills/level-common/resource_index.jsonl` / asset_catalog / Effect.Name 中存在 |
| R-3 相机高度 | CameraFollow 第4参 = 50（缩放关卡固定）|
| R-4 主角朝向反向 | PointInDirection 方向 vs CameraFollow offset 方向异号 |
| R-6 Effect 不加 Visible | Effect props 仅含 Name/EditMode/AssetId/Loop/FullScreenBeforeUI |
| R-9 ChangeSize 渐变 | 放大走 Repeat+ChangeSize，无 SetSize 瞬间大数值 |
| R-9 时序合理 | 并行用非阻塞，因果用 AndWait/Until |
| R-10 UI View 白名单 | 只用 LabelBubble / LabelBubblenobg |
| N6 角色间距 | 人形角色两两间距 ≥1m，与 control ≥0.5m |
| N7 终点不重合 | 同时段 MoveTo 终点欧氏距离 ≥1m |
| R-15 站位三层流程 | 所有坐标来自步骤2.5三层流程输出，已输出坐标确认表 |
| R-16 摄像机反推 | CameraFollow 参数来自步骤3.7 spread 反推（或确认单明确指定），未直接套固定预设值 |
