# 盘古3D平台 — 积木块完整参考手册

> 来源：Hetu_Blocks_Documentation v3.1 + Hetu_Block_Serialization_Analysis（基于实际 .ws 文件和源代码双重验证）  
> 覆盖：178+ Block 类型（核心 150+ + 扩展 28）
>
> **与 SKILL.md 的关系**：本文件是"积木参数槽"的权威来源。  
> SKILL.md §"代码块参数槽规则"的完整内容已迁入本文件 §0 节。  
> `scripts/params_registry.json`（实证扫描 27 个上线关卡自动生成）是机器校验的权威源，本文件是人工查询的权威源。

---

## §0 · 参数槽核心规则（从 SKILL.md 迁入）

### 积木 JSON 核心结构

```json
{
  "define": "积木名",
  "sections": [
    { "params": [...], "children": [...] }
  ]
}
```

- **顺序执行**的后续块 → 作为父 `sections[0].children` 数组的下一个元素**平铺**（禁用 `next`）
- **分支里**的子块（`If` / `Repeat` / `Forever` / `Trigger` 的 body）→ 放 `sections[i].children`
- **嵌入运算**的子块 → 放 `sections[0].params[i]`，且必须包装成 `{"type":"block","val":{...}}`

### ⚠️ 硬规则：children 平铺，禁用 `next`

**事故教训（2026-04，15-2 关卡3）**：用 `next` 串联积木，`verify_blocks.py` 通过，但**编辑器打开后只渲染链头，其余全部消失**。

所有顺序执行的积木必须作为父 `sections[*].children` 的数组元素平铺：

```json
// ✅ 正确
"children": [
  {"define": "SetVar", ...},
  {"define": "ListAdd", ...},
  {"define": "If", "sections": [{"params": [...], "children": [...]}]}
]

// ❌ 错误（next 链）
"children": [{"define": "SetVar", "next": {"define": "ListAdd", ...}}]
```

交付前必跑：`python scripts/verify_no_new_next.py <zip> --baseline <母本zip>`

### 三大参数槽模式

| 模式 | 占位 `{}` 位置 | 典型积木 |
|------|---------------|---------|
| **[S] self 占位** | 第 1 个是 `{}` | `Show`, `Hide`, `SetSize`, `PointInDirection`, `PointInPitch`, `MoveSteps`, `AnchorTo` |
| **[O] 运算符占位** | 中间 1 个 `{}` | `Add`, `Subtract`, `Multiply`, `Divide`, `IsEqual`, `IsLess`, `IsGreator`, `And`, `Or` |
| **[N] 无占位** | 无 `{}` | `SetVar`, `ListGetItemAt`, `Mod`, `StrJoin`, `BroadcastMessage`, `PlayAnimation`, `CameraFollow`, `GotoPosition3D` 等 |

### 常错陷阱

| 积木 | ✅ 正确 | ❌ 常犯错 | 后果 |
|------|---------|----------|------|
| `ListGetItemAt` | **2 个 params** `[index, list]` | 误加中间 `{}` 变 3 个 | 循环不执行 |
| `Mod` | **2 个 params** `[a, b]` | 误加 `{}` | 取模失效 |
| `StrJoin` | **2 个 params** `[a, b]` | 误加 `{}` | 拼接失效 |
| `Variable` | **1 个 param**，无 `name` 字段 | 误加空占位 | 引擎识别不出 |
| 嵌套 Operator | `{"type":"block","val":{...}}` 包装 | 直接塞裸 `{"define":...}` | 渲染为字面值 |
| `LogicalOperator` 进 `[逻]` 槽 | 只能 `{"type":"block","val":{...}}` | 用 `{"type":"var","val":"true"}` | 布尔条件永远为假 |
| 多参积木（`GotoPosition3D` 等） | **每个参数独立写** `{"type":"var","val":"..."}` | 把 `[x,y,z]` 合并成一个数组参数 | 引擎静默忽略，坐标全部失效 |

### 常用积木参数槽速查表（n = sections[0].params 长度）

**Events / Control**

| 积木 | n | 模式 | 备注 |
|------|---|------|------|
| `WhenGameStarts` / `WhenStartup` | 0 | — | body 在 children |
| `WhenReceiveMessage` | 1 | [N] | `[固] message` |
| `Repeat` | 1 | [N] | `[值] times` |
| `Forever` | 0 | — | body 在 children |
| `If` | 1 | [N] | `[逻] condition`，必须 block 包装 |
| `IfElse` | 1 | [N] | **2 个 sections**：[0] 条件+then，[1] 空params+else |
| `WaitSeconds` | 1 | [N] | `[值] sec` |
| `StopScript` | 1 | [N] | `all / this script / other scripts in sprite` |

**Sprite 动作**

| 积木 | n | 模式 | 备注 |
|------|---|------|------|
| `Show` / `Hide` | 1 | [S] | `[{}]` |
| `SetSize` | 2 | [S] | `[{}, size]` |
| `PointInDirection` / `PointInPitch` | 2 | [S] | `[{}, degrees]` |
| `RunToTargetAndWait` | 1 | [N] | `[固] target`（无 self 占位）|
| `GotoPosition3D` | 3 | [N] | `[x, y, z]`；**单位：米** |
| `GlideSecsToPosition3D` | 4 | [N] | `[sec, x, y, z]`；**单位：米** |
| `PlayAnimation` / `PlayAnimationUntil` | 1 | [N] | `[固] name` |
| `SetAnimationSpeed` / `SetSpeedMul` | 1 | [N] | `[值]` |

**摄像机 / 音频**

| 积木 | n | 模式 | 备注 |
|------|---|------|------|
| `SetCameraFOV` | 1 | [N] | `[值] fov` |
| `CameraFollow` | 4 | [N] | `[固] target, distance, offsetY, height`；**distance/offsetY/height 单位厘米** |
| `PlaySound` | 1 | [N] | `[固] name` |
| `PlayBGM` | 2 | [N] | `[固] name, [值] volume` |
| `StopAllSound` | 0 | — | `sections=[{}]` |

**变量 / 列表**

| 积木 | n | 模式 | 备注 |
|------|---|------|------|
| `Variable` | 1 | [N] | `[固] name`（无中间占位） |
| `SetVar` / `IncVar` | 2 | [N] | `[固] name, [值] value` |
| `ListAdd` | 2 | [N] | `[值] item, [固] listname` |
| `ListDeleteAll` | 1 | [N] | `[固] listname` |
| `ListGetItemAt` | **2** | [N] | `[值] index, [固] listname`（**无中间 `{}`**）|
| `ListGetLength` | 1 | [N] | `[固] listname` |

**运算**

| 积木 | n | 模式 | 备注 |
|------|---|------|------|
| `Add` / `Subtract` / `Multiply` / `Divide` | 3 | [O] | `[a, {}, b]` |
| `Mod` | **2** | [N] | `[a, b]`（**无中间 `{}`**）|
| `StrJoin` | **2** | [N] | `[a, b]`（**无中间 `{}`**）|
| `IsEqual` / `IsLess` / `IsGreator` | 3 | [O] | `[a, {}, b]`；⚠️ 拼写是 `Greator` |
| `And` / `Or` | 3 | [O] | 两端必须 LogicalOperator |
| `Not` | 1 | [N] | 只接 1 个 LogicalOperator |

**UI / 通信**

| 积木 | n | 模式 | 备注 |
|------|---|------|------|
| `SetTitle` | 1 | [N] | `[值] text` |
| `BroadcastMessage` / `BroadcastMessageAndWait` | 1 | [N] | `[固] message` |
| `EndRun` | 2 | [N] | `[值] text, [值] extra` |

### 消息注册（`#EVENT`）

所有自定义广播消息名必须注册到 `scene.props2["#EVENT"].value` 数组里，否则编辑器无法识别。

### 变量注册（`props2`）

所有 `SetVar/IncVar/Variable/ListAdd` 用到的变量名，必须在 `scene.props2` 里先声明：

```json
"i": {"type": "Simple", "value": "0"},
"cin_cut": {"type": "SimpleList", "value": []}
```

OJ 模板必备：`variable`, `#EVENT`, `err_msg`, `*OJ-输入信息`, `*OJ-执行结果`, `cmd`, `state`, `*OJ-Judge`, `输入元素`, `n`, `cin_cut`, `输出元素`, `n1`, `space-flag`, `cout_cut`。

> ⚠️ 表里没列的积木先 Grep 本文件找说明，再在 `参考-extracted/` 找至少 1 个实证 JSON 样本对照，**禁止凭猜**。

---

## ⚠️ 必读：关键拼写陷阱与规则

| 文档/直觉写法 | 引擎实际 define 名 | 说明 |
|---|---|---|
| `IsGreater` | **`IsGreator`** | 引擎源码拼写错误，必须原样用 |
| `SayForSeconds` | **`SaySeconds`** | 引擎实际定义名 |
| `ThinkForSeconds` | **`ThinkSeconds`** | 引擎实际定义名 |
| `PlayInstrument` | **`PlayIntrument`** | 引擎源码缺字母，必须原样用 |
| `ShowSprite` | **`Show`** | 实际 define |
| `HideSprite` | **`Hide`** | 实际 define |
| `ListDeleteAll` | **`ListDeleteAll`** | 旧代码里可能出现 `ListDeleteALl`（AaL）拼写错误 |

### Block 类型系统

| BlockType | 能否有返回值 | 能否嵌入参数槽 | 典型例子 |
|---|---|---|---|
| **Trigger** | 无 | 不可嵌入 | WhenGameStarts、WhenKeyPressed |
| **Statement** | 无 | 不可嵌入 | MoveSteps、WaitSeconds |
| **BranchStatement** | 无 | 不可嵌入 | Forever、If、IfElse |
| **Operator** | 有（数值/文本/混合） | 可嵌入 `[值]` 槽 | Add、GetPosX、Variable |
| **LogicalOperator** | 有（布尔值） | 可嵌入 `[逻]` 槽 | IsGreator、IsTouching、And |

### 参数嵌入规则符号约定

本文档参数列使用以下简写标注：
- `[固]` = 固定值，只能选下拉列表，**不可**嵌入其他 Block
- `[值]` = 可嵌入返回数值/文本的 Operator Block
- `[逻]` = 只能嵌入返回布尔值的 LogicalOperator Block

---

## Events（事件）

**BlockType：Trigger**（事件头不使用 `next`，后续块放在 `sections[0].children` 中）

| define | 说明 | 返回值 | 参数 | 使用次数 |
|--------|------|--------|------|---------|
| `WhenGameStarts` | 游戏开始（点击开始按钮）时触发 | - | 无 | 51 |
| `WhenStartup` | 场景初始化时触发，早于 WhenGameStarts | - | 无 | 23 |
| `WhenGameStopped` | 游戏停止时触发 | - | 无 | — |
| `WhenIStartAsAClone` | 作为克隆体启动时触发 | - | 无 | 21 |
| `WhenThisSpriteClicked` | 角色/场景被点击时触发 | - | **target** `[固]`：被点击的对象（this sprite / scene / anywhere / 角色名） | — |
| `WhenKeyPressed` | 按键按下时触发 | - | **key** `[固]`：space / ← / → / ↓ / ↑ / any / enter / a-z / 0-9 | — |
| `WhenCollisionDetected` | 碰到指定对象时触发 | - | **target** `[固]`：碰撞检测目标（动态角色列表） | — |
| `WhenLoudnessOrTimer` | 音量或计时器超过阈值时触发 | - | **type** `[固]`：timer / loudness；**value** `[值]`：阈值，默认10 | — |
| `WhenReceiveMessage` | 收到广播消息时触发 | - | **message** `[固]`：消息名（动态列表） | 442 |

**序列化示例：**
```json
{
  "define": "WhenGameStarts",
  "sections": [{"params": [], "children": [
    {
      "define": "MoveSteps",
      "sections": [{"params": [{"type": "var", "val": "10"}]}],
      "next": {
        "define": "WaitSeconds",
        "sections": [{"params": [{"type": "var", "val": "1"}]}]
      }
    }
  ]}]
}
```

---

## Events-Broadcast（广播消息）

**BlockType：Statement**

| define | 说明 | 返回值 | 参数 | 使用次数 |
|--------|------|--------|------|---------|
| `BroadcastMessage` | 广播消息（不等待） | - | **message** `[固]`：消息名（动态列表） | 75 |
| `BroadcastMessageAndWait` | 广播消息并等待所有脚本执行完毕 | - | **message** `[固]`：消息名（动态列表） | 343 |

**序列化示例：**
```json
{"define": "BroadcastMessage", "sections": [{"params": [{"type": "var", "val": "初始化"}]}]}
```

---

## Motion（运动）

**BlockType：Statement / Operator**

| define | 说明 | 返回值 | 参数 | 使用次数 |
|--------|------|--------|------|---------|
| `MoveSteps` | 向前移动 N 步 | - | **steps** `[值]`：步数，默认10 | — |
| `TurnRight` | 顺时针旋转 N 度 | - | **degrees** `[值]`：角度，默认15 | — |
| `TurnLeft` | 逆时针旋转 N 度 | - | **degrees** `[值]`：角度，默认15 | — |
| `TurnUp` | 向上旋转（仅3D） | - | **degrees** `[值]`：角度，默认15 | — |
| `TurnDown` | 向下旋转（仅3D） | - | **degrees** `[值]`：角度，默认15 | — |
| `GotoPosition3D` | 瞬移到3D坐标 ⚠️ 仅用于初始化，运行中移动用 RunToTargetAndWait | - | **x** `[值]` **y** `[值]` **z** `[值]`：坐标，默认0 | 64 |
| `GotoPosition2D` | 瞬移到2D坐标（UI元素） | - | **x** `[值]` **y** `[值]`：坐标，默认0 | 74 |
| `GotoTarget` | 瞬移到目标位置 | - | **target** `[固]`：random position / mouse pointer / 角色名 | 11 |
| `GotoFrontBack` | 瞬移到物件前/后方 | - | **direction** `[固]`：front / back | 17 |
| `GlideSecsToTarget` | N 秒内滑动到目标 | - | **time** `[值]`：秒；**target** `[固]`：目标名 | — |
| `GlideSecsToPosition2D` | N 秒内滑动到2D坐标 | - | **time** `[值]`；**x** `[值]`；**y** `[值]` | 6 |
| `GlideSecsToPosition3D` | N 秒内滑动到3D坐标 | - | **time** `[值]`；**x** `[值]`；**y** `[值]`；**z** `[值]` | 16 |
| `GlideStepsInSecs` | N 秒内滑动 N 步 | - | **steps** `[值]`；**time** `[值]` | — |
| `GlideSecsToPosition3DAndSetRotation` | 滑动到3D坐标并设置旋转 | - | time/x/y/z/yaw/pitch/rotType（7个参数） | 1 |
| `PointInDirection` | 设置水平朝向角度（0=Y+, 90=X+, -90=X-, 180=Y-） | - | 空占位 `{}`；**degrees** `[值]`：角度，默认90 | 13 |
| `PointInPitch` | 设置俯仰角度 | - | 空占位 `{}`；**degrees** `[值]`：俯仰角 | 10 |
| `PointTowards` | 面向指定目标 | - | **target** `[固]`：mouse pointer / 角色名 | — |
| `BounceOnEdge` | 碰到边缘就反弹 | - | 无 | — |
| `SetRotationStyle` | 设置旋转样式 | - | **style** `[固]`：left-right / horizontal / don't rotate / all around | — |
| `AnchorTo` | 锁定到对象骨骼节点 | - | **target** `[固]`；**coordinateType** `[固]`：local/world；**orientation** `[固]`：with/without；**bone** `[固]`：骨骼节点名 | — |
| `ChangePosX` | 改变 X 坐标（增量） | - | 空占位 `{}`；**delta** `[值]`：增量 | 52 |
| `ChangePosY` | 改变 Y 坐标（增量） | - | 空占位 `{}`；**delta** `[值]`：增量 | 61 |
| `ChangePosZ` | 改变 Z 坐标（增量） | - | 空占位 `{}`；**delta** `[值]`：增量 | 7 |
| `SetPosX` | 设置 X 坐标 | - | 空占位 `{}`；**x** `[值]` | 3 |
| `SetPosY` | 设置 Y 坐标 | - | 空占位 `{}`；**y** `[值]` | 4 |
| `SetPosZ` | 设置 Z 坐标 | - | 空占位 `{}`；**z** `[值]` | 1 |
| `GetPosX` | 获取 X 坐标 | 浮点数 | 无 | 22 |
| `GetPosY` | 获取 Y 坐标 | 浮点数 | 无 | 9 |
| `GetPosZ` | 获取 Z 坐标 | 浮点数 | 无 | 3 |
| `GetDirection` | 获取水平朝向角度 | 浮点数 | 无 | — |
| `GetPitch` | 获取俯仰角度 | 浮点数 | 无 | — |
| `WalkToTarget` | 走向目标（不等待） | - | **target** `[固]`：目标名 / random position | — |
| `WalkToTargetAndWait` | 走向目标并等待到达（行走动画） | - | **target** `[固]`：目标名 | — |
| `RunToTarget` | 跑向目标（不等待） | - | **target** `[固]`：目标名 / random position | — |
| `RunToTargetAndWait` | ⭐ 跑向目标并等待到达（跑步动画）**角色移动首选** | - | **target** `[固]`：目标名 | 4 |
| `FollowAndKeepDistance` | 跟随目标并保持距离 | - | **target** `[固]`：目标名；**distance** `[值]`：距离 | — |
| `StartWalk` | 开始行走/跑步动画 | - | **mode** `[固]`：walk / run | — |
| `StopWalk` | 停止行走 | - | **target** `[固]`：self / 角色名 | — |
| `SetSpeedMul` | 设置移动速度倍率 | - | **multiplier** `[值]`：倍率 | 2 |
| `TurnToTargetInSecs` | N 秒内朝向目标 | - | **time** `[值]`：秒；**target** `[固]`：目标名 | — |
| `TurnToAngleInSecs` | N 秒内转到指定角度 | - | **angle** `[值]`：角度；**time** `[值]`：秒 | — |

**坐标系说明：** Position[2]（Z轴）= 水平"一排"，Position[0]（X轴）= 深度

**序列化示例（GotoPosition3D）：**
```json
{"define": "GotoPosition3D", "sections": [{"params": [{"type":"var","val":"0"},{"type":"var","val":"0"},{"type":"var","val":"0"}]}]}
```

**序列化示例（PointInDirection，注意有空占位）：**
```json
{"define": "PointInDirection", "sections": [{"params": [{}, {"type":"var","val":"-90"}]}]}
```

**序列化示例（CameraFollow）：**
```json
{"define": "CameraFollow", "sections": [{"params": [{"type":"var","val":"队长"},{"type":"var","val":"640"},{"type":"var","val":"0"},{"type":"var","val":"500"}]}]}
```

---

## Camera（摄像机）

**BlockType：Statement**

| define | 说明 | 返回值 | 参数 | 使用次数 |
|--------|------|--------|------|---------|
| `CameraFollow` | 摄像机跟随目标 | - | **target** `[固]`；**offsetX** `[值]`；**offsetY** `[值]`，默认30；**offsetZ** `[值]`，默认0 | 10 |
| `CameraLookAt` | 相机看向目标 | - | **target** `[固]`：目标对象 | — |
| `CameraLookAtWithOffset` | 相机看向目标（带偏移） | - | **target** `[固]`；**offsetX** `[值]`；**offsetY** `[值]`；**offsetZ** `[值]` | — |
| `CameraLookAtPos` | 相机看向指定坐标 | - | **x** `[值]`；**y** `[值]`；**z** `[值]` | — |
| `CameraLookAt2` | 相机同时看向两个目标 | - | **target1** `[固]`；**target2** `[固]` | — |
| `CameraReset` | 重置相机 | - | 无 | — |
| `SetCameraFOV` | 设置摄像机视野角度 | - | **fov** `[值]`：视野角度 | 10 |
| `ChangeCameraFOV` | 改变摄像机 FOV（增量） | - | **delta** `[值]`：增量，默认10 | — |
| `TransitToCameraPreset` | 切换到摄像机预设视角 | - | **preset** `[固]`：预设名；**outEffect** `[固]`：退出效果；**inEffect** `[固]`：进入效果 | 17 |

---

## Looks（外观）

**BlockType：Statement / Operator**

| define | 说明 | 返回值 | 参数 | 使用次数 |
|--------|------|--------|------|---------|
| `Say` | 说话气泡（持续显示） | - | **message** `[值]`：内容，默认"Hello!" | — |
| `SaySeconds` | 说话气泡持续 N 秒 ⚠️ 非SayForSeconds | - | **message** `[值]`；**duration** `[值]`：秒，默认2 | 24 |
| `Think` | 思考气泡（持续显示） | - | **message** `[值]`：内容，默认"Hmm..." | — |
| `ThinkSeconds` | 思考气泡持续 N 秒 ⚠️ 非ThinkForSeconds | - | **message** `[值]`；**duration** `[值]`：秒，默认2 | — |
| `ShowLabel` | 显示标签 | - | **text** `[值]`：标签文本，默认"Hello!" | 4 |
| `HideLabel` | 隐藏标签 | - | 无 | 1 |
| `ChangeLabel` | 修改标签样式 | - | **text** `[值]`；**tips** `[值]`；**bgColor** `[固]`，默认#ffffff；**textColor** `[固]`，默认#000000；**tipsColor** `[固]`，默认#000000 | — |
| `XPosOfSubLabel` | 获取子标签 X 坐标 | 浮点数 | **target** `[固]`：self / 角色名 | — |
| `YPosOfSubLabel` | 获取子标签 Y 坐标 | 浮点数 | **target** `[固]`：self / 角色名 | — |
| `ChangeSize` | 改变角色大小（增量百分比） | - | **delta** `[值]`：增量，默认10 | 33 |
| `SetSize` | 设置角色大小（百分比） | - | **size** `[值]`：大小，默认100 | 59 |
| `SetBrightness` | 设置亮度（0-100） | - | **brightness** `[值]`：亮度，默认0 | — |
| `SetTransparency` | 设置透明度（0-100，0为不透明） | - | **transparency** `[值]`：透明度，默认0 | — |
| `Show` | 显示角色 ⚠️ define是Show非ShowSprite | - | 无 | 115 |
| `Hide` | 隐藏角色 ⚠️ define是Hide非HideSprite | - | 无 | 177 |
| `SwitchCostume` | 切换造型 | - | **costume** `[固]`：造型名（动态列表） | 75 |
| `NextCostume` | 切换到下一个造型 | - | 无 | — |
| `GetCostumeIndexOrName` | 获取造型编号或名称 | 混合 | **type** `[固]`：number（返回整数）/ name（返回字符串） | — |
| `SizeOp` | 获取当前大小百分比 | 浮点数 | 无 | — |
| `SetSaySkin` | 设置说话气泡皮肤 | - | **skin** `[固]`：皮肤名 | 1 |
| `SetThinkSkin` | 设置思考气泡皮肤 | - | **skin** `[固]`：皮肤名 | — |
| `PlayAnimation` | 播放动画（循环，不等待结束） | - | **animation** `[固]`：动画名（含循环动画的动态列表） | 30 |
| `PlayAnimationAndWait` | 播放动画并等待指定时间 | - | **animation** `[固]`：动画名；**duration** `[值]`：等待秒数，默认1 | — |
| `PlayAnimationUntil` | 播放动画直到结束（阻塞） | - | **animation** `[固]`：动画名（不含循环动画的列表） | 32 |
| `PlayAnimationUntilAndWait` | 播放动画直到结束后再等待 N 秒 | - | **animation** `[固]`：动画名；**duration** `[值]`：额外等待秒数 | — |
| `PlayEmotionAnimation` | 播放表情动画 | - | **emotion** `[固]`：表情名；**loop** `[固]`：true / false | — |
| `StopAnimation` | 停止指定动画（Patches扩展） | - | **animation** `[固]`：动画名 | 8 |
| `SetAnimationSpeed` | 设置动画播放速度 | - | **speed** `[值]`：速度 | 8 |
| `SetAnimationSpeedRatio` | 设置角色动画播放速率（Patches扩展） | - | **ratio** `[值]`：速率 | — |
| `FollowNode` | UI锚定到3D对象骨骼节点（UI扩展） | - | **bone** `[固]`：骨骼节点名；**offset** `[固]`：偏移（none等） | 1 |

> ⚠️ `PlayAnimation`（非阻塞/循环）vs `PlayAnimationUntil`（阻塞）：先判断是否需要并行，选错会导致逻辑错乱。

**序列化示例（PlayAnimation）：**
```json
{"define": "PlayAnimation", "sections": [{"params": [{"type":"var","val":"直播框"}]}]}
```

**序列化示例（SaySeconds 嵌套 StrJoin）：**
```json
{
  "define": "SaySeconds",
  "sections": [{"params": [
    {"type":"block","val":{"define":"StrJoin","sections":[{"params":[
      {"type":"block","val":{"define":"GetSpriteName","sections":[{}]}},
      {"type":"var","val":"被点击"}
    ]}]}},
    {"type":"var","val":"2"}
  ]}]
}
```

---

## Sound（声音）

**BlockType：Statement / Operator**

| define | 说明 | 返回值 | 参数 | 使用次数 |
|--------|------|--------|------|---------|
| `PlaySound` | 播放音效（异步） | - | **sound** `[固]`：声音名（动态列表） | 75 |
| `PlaySoundUntil` | 播放音效并等待结束 | - | **sound** `[固]`：声音名（动态列表） | 30 |
| `PlayBGM` | 播放背景音乐 | - | **sound** `[固]`：音乐名；**volume** `[值]`：音量百分比，默认100 | 2 |
| `StopAllSound` | 停止所有声音 | - | 无 | 4 |
| `ChangeVolumeBy` | 改变音量（增量百分比） | - | **delta** `[值]`：增量，默认10 | — |
| `SetVolumeTo` | 设置音量（0-100） | - | **volume** `[值]`：音量，默认100 | 3 |
| `GetVolume` | 获取当前音量 | 浮点数 | 无 | — |
| `Set3DSettings` | 设置3D音效参数 | - | **dopplerFactor** `[值]`，默认1；**distanceScale** `[值]`，默认1；**rolloffFactor** `[值]`，默认1 | — |

**序列化示例（PlayBGM）：**
```json
{"define": "PlayBGM", "sections": [{"params": [{"type":"var","val":"轻松休闲1"},{"type":"var","val":"100"}]}]}
```

---

## Control�����ƣ�

**BlockType��Statement / BranchStatement**

| define | ˵�� | ����ֵ | ���� | ʹ�ô��� |
|--------|------|--------|------|---------|
| `Forever` | ��Զѭ��ִ�� | - | �ޣ�children ���ӿ飩 | 12 |
| `Repeat` | �ظ�ִ�� N �� | - | **times** `[ֵ]`��������Ĭ��10 | 86 |
| `RepeatUntil` | �ظ�ֱ���������� | - | **condition** `[��]`����������ʽ | �� |
| `Break` | ������ǰѭ�� | - | �� | �� |
| `If` | �������������ִ�� | - | **condition** `[��]`����������ʽ | 291 |
| `IfElse` | ���...����...��˫ Section�� | - | **condition** `[��]`����������ʽ | 134 |
| `WaitSeconds` | �ȴ�ָ������ | - | **duration** `[ֵ]`���룬Ĭ��1 | 131 |
| `WaitUntil` | �ȴ�ֱ���������� | - | **condition** `[��]`����������ʽ | 11 |
| `StopScript` | ֹͣ�ű� | - | **type** `[��]`��all / this script / other scripts in sprite | 35 |
| `WhenIStartAsAClone` | ��Ϊ��¡������ʱ������Trigger�� | - | �� | 21 |
| `CreateCloneOf` | ������¡�� | - | **target** `[��]`��myself / ��ɫ�� | 20 |
| `DeleteThisClone` | ɾ����ǰ��¡�� | - | �� | 9 |
| `GotoProject` | ��ת����Ŀ | - | **project** `[��]`����Ŀ������̬�б��� | �� |
| `TransitProject` | �л�������������Ч���� | - | **project** `[��]`����������**outEffect** `[��]`���˳�Ч����**inEffect** `[��]`������Ч�� | �� |
| `ShowSpriteName` | ��ʾ/���ؽ�ɫ���� | - | **action** `[��]`��show / hide | �� |
| `PlayTransitEffect` | ����ת��Ч�� | - | **outEffect** `[��]`���˳�Ч����**inEffect** `[��]`������Ч�� | �� |
| `SetQuestText` | ���������ı� | - | **mainTitle** `[ֵ]`��������������**subTitle** `[ֵ]`���������� | �� |
| `SetQuestStyle` | ����������ʽ | - | **style** `[��]`����ʽ������̬�б��� | �� |
| `ShowQuest` | ��ʾ������� | - | **animation** `[��]`��none / animation | �� |
| `HideQuest` | ����������� | - | **animation** `[��]`��none / animation | �� |
| `CompleteQuest` | ���������� | - | �� | �� |

**���л�ʾ����Forever ѭ������**
```json
{
  "define": "Forever",
  "sections": [{"params": [], "children": [
    {"define": "MoveSteps", "sections": [{"params": [{"type":"var","val":"10"}]}],
     "next": {"define": "WaitSeconds", "sections": [{"params": [{"type":"var","val":"1"}]}]}}
  ]}]
}
```

**���л�ʾ����IfElse ˫ Section����**
```json
{
  "define": "IfElse",
  "sections": [
    {"params": [{"type":"block","val":{"define":"IsGreator","sections":[{"params":[{"type":"var","val":""},{"type":"var","val":"50"}]}]}}],
     "children": [{"define":"Say","sections":[{"params":[{"type":"var","val":"Greater"}]}]}]},
    {"params": [], "children": [{"define":"Say","sections":[{"params":[{"type":"var","val":"Less or Equal"}]}]}]}
  ]
}
```

---

## Sensing����⣩

**BlockType��Operator / LogicalOperator / Statement**

| define | ˵�� | ����ֵ | ���� | ʹ�ô��� |
|--------|------|--------|------|---------|
| `GetMouseX` | ��ȡ��� X ���� | ������ | �� | �� |
| `GetMouseY` | ��ȡ��� Y ���� | ������ | �� | �� |
| `IsMouseDown` | ����Ƿ��� | ����ֵ | �� | �� |
| `GetDistanceTo` | ��ĳ����ľ��� | ������ | **target** `[��]`��mouse pointer / ��ɫ�� | �� |
| `IsTouching` | �Ƿ�����ĳ���� | ����ֵ | **target** `[��]`����̬��ɫ�б� | �� |
| `IsKeyPressed` | �����Ƿ񱻰��� | ����ֵ | **key** `[��]`��space / �� / �� / �� / �� / any / enter / a-z / 0-9 | �� |
| `GetTimer` | ��ȡ��ʱ��ֵ���룩 | ������ | �� | �� |
| `ResetTimer` | ���ü�ʱ��Ϊ0 | - | �� | �� |
| `GetCurrentDate` | ��ȡ��ǰ����/ʱ�� | ���� | **type** `[��]`��year / month / day / day of week / hour / minute / second | �� |
| `GetDaysSince2000` | ��ȡ��2000��1��1������������ | ���� | �� | �� |
| `GetUserName` | ��ȡ�û��� | �ַ��� | �� | �� |
| `GetSpriteName` | ��ȡ��ǰ��ɫ���� | �ַ��� | �� | �� |
| `GetPropertyOf` | ��ȡ���������ֵ | ��� | **property** `[��]`������������̬����**target** `[��]`��Ŀ����� | �� |
| `AskAndWait` | ѯ�ʲ��ȴ��û����� | - | **question** `[ֵ]`���������ݣ�Ĭ��"what's your name?" | �� |
| `Answer` | ��ȡ�û��ش����� | �ַ��� | �� | �� |
| `GetLoudness` | ��ȡ��˷�������С | ������ | �� | �� |

**���л�ʾ����IsTouching����**
```json
{"define": "IsTouching", "sections": [{"params": [{"type":"var","val":"_edge_"}]}]}
```

**���л�ʾ����GetPropertyOf����**
```json
{"define": "GetPropertyOf", "sections": [{"params": [{"type":"var","val":"x position"},{"type":"var","val":"Sprite1"}]}]}
```

---

## Operators�����㣩

**BlockType��Operator / LogicalOperator**

### �������㣨���ظ�������

| define | ˵�� | ����ֵ | ���� | ʹ�ô��� |
|--------|------|--------|------|---------|
| `Add` | �ӷ� | ������ | **operand1** `[ֵ]`��**operand2** `[ֵ]` | 56 |
| `Subtract` | ���� | ������ | **operand1** `[ֵ]`��**operand2** `[ֵ]` | 26 |
| `Multiply` | �˷� | ������ | **operand1** `[ֵ]`��**operand2** `[ֵ]` | 30 |
| `Divide` | ���� | ������ | **operand1** `[ֵ]`��**operand2** `[ֵ]` | 10 |
| `Mod` | ȡģ�����ࣩ | ������ | **dividend** `[ֵ]`��**divisor** `[ֵ]` | 11 |
| `PickRandom` | ��Χ��ȡ����� | ������ | **min** `[ֵ]`��Ĭ��1��**max** `[ֵ]`��Ĭ��10 | 30 |
| `Round` | �������� | ������ | **value** `[ֵ]` | 2 |
| `MathFunc` | ��ѧ���� | ������ | **function** `[��]`��abs/floor/ceiling/sqrt/sin/cos/tan/asin/acos/atan/ln/log/e^/10^��**value** `[ֵ]` | 5 |
| `KeepNDecimalPlaces` | ���� N λС����Patches��չ�� | ������ | **n** `[ֵ]`��λ����**value** `[ֵ]`����ֵ | �� |

### �Ƚ����㣨���ز���ֵ��

| define | ˵�� | ����ֵ | ���� | ʹ�ô��� |
|--------|------|--------|------|---------|
| `IsGreator` | ���ڱȽ� ?? ע��ƴд�� Greator | ����ֵ | **operand1** `[ֵ]`��**operand2** `[ֵ]`��Ĭ��50 | 19 |
| `IsLess` | С�ڱȽ� | ����ֵ | **operand1** `[ֵ]`��**operand2** `[ֵ]`��Ĭ��50 | 39 |
| `IsEqual` | ���ڱȽ� | ����ֵ | **operand1** `[ֵ]`��**operand2** `[ֵ]`��Ĭ��50 | 437 |

### �߼����㣨���ز���ֵ��

| define | ˵�� | ����ֵ | ���� | ʹ�ô��� |
|--------|------|--------|------|---------|
| `And` | �߼��� | ����ֵ | **condition1** `[��]`��**condition2** `[��]` | 28 |
| `Or` | �߼��� | ����ֵ | **condition1** `[��]`��**condition2** `[��]` | 42 |
| `Not` | �߼��� | ����ֵ | **condition** `[��]` | 52 |
| `ReturnBool` | ���ع̶�����ֵ | ����ֵ | **value** `[��]`��true / false | �� |

### �ַ�������

| define | ˵�� | ����ֵ | ���� | ʹ�ô��� |
|--------|------|--------|------|---------|
| `StrJoin` | ���������ַ��� | �ַ��� | **str1** `[ֵ]`��Ĭ��"apple"��**str2** `[ֵ]`��Ĭ��"banana" | 132 |
| `StrLetterOf` | ��ȡ�ַ����� N ���ַ� | �ַ��� | **index** `[ֵ]`��Ĭ��1��**string** `[ֵ]`��Ĭ��"apple" | 94 |
| `StrLength` | ��ȡ�ַ������� | ���� | **string** `[ֵ]`��Ĭ��"apple" | 52 |
| `StrContains` | �ж��ַ����Ƿ�����Ӵ� | ����ֵ | **string** `[ֵ]`��Ĭ��"apple"��**substring** `[ֵ]`��Ĭ��"apple" | 11 |

**���л�ʾ����Ƕ������ Add ��Ƕ Multiply����**
```json
{
  "define": "Add",
  "sections": [{"params": [
    {"type":"block","val":{"define":"Multiply","sections":[{"params":[{"type":"var","val":"5"},{"type":"var","val":"3"}]}]}},
    {"type":"var","val":"10"}
  ]}]
}
```

**���л�ʾ����And Ƕ�������Ƚϣ���**
```json
{
  "define": "And",
  "sections": [{"params": [
    {"type":"block","val":{"define":"IsGreator","sections":[{"params":[{"type":"var","val":""},{"type":"var","val":"10"}]}]}},
    {"type":"block","val":{"define":"IsLess","sections":[{"params":[{"type":"var","val":""},{"type":"var","val":"100"}]}]}}
  ]}]
}
```

---

## Variables��������

**BlockType��Operator / Statement**

| define | ˵�� | ����ֵ | ���� | ʹ�ô��� |
|--------|------|--------|------|---------|
| `Variable` | ��ȡ����ֵ��?? ������� `name` �ֶΣ� | ��� | **variableName** `[��]`�������� | 1049 |
| `SetVar` | ���ñ���ֵ | - | **variable** `[��]`����name����**value** `[ֵ]`��Ĭ��1 | 872 |
| `IncVar` | ����ֵ���� | - | **variable** `[��]`����name����**delta** `[ֵ]`��Ĭ��1 | 95 |
| `ShowVar` | ��ʾ���������� | - | **variable** `[��]` | �� |
| `HideVar` | ���ر��������� | - | **variable** `[��]` | �� |
| `ListVariable` | ��ȡ�б���?? ������� `name` �ֶΣ� | ���� | **listName** `[��]`���б��� | �� |
| `ListAdd` | ���б�ĩβ����Ԫ�� | - | **item** `[ֵ]`��Ĭ��"thing"��**list** `[��]`����name�� | 86 |
| `ListDelete` | ɾ��ָ��λ�õ��б��� | - | **index** `[ֵ]`��Ĭ��1��**list** `[��]`����name�� | �� |
| `ListDeleteAll` | ����б������� ?? �ɴ�������� ListDeleteALl ƴд���� | - | **list** `[��]`����name�� | 32 |
| `ListInsertAt` | ��ָ��λ�ò�����Ŀ | - | **item** `[ֵ]`��**index** `[ֵ]`��Ĭ��1��**list** `[��]`����name�� | �� |
| `ListReplaceItemAt` | �滻ָ��λ�õ��б��� | - | **index** `[ֵ]`��Ĭ��1��**list** `[��]`����name����**item** `[ֵ]` | �� |
| `ListGetItemAt` | ��ȡָ��λ�õ��б��� | ��� | **index** `[ֵ]`��Ĭ��1��**list** `[��]`����name�� | 113 |
| `ListGetItemIndex` | ��ȡ��Ŀ���б��е����� | ���� | **item** `[ֵ]`��**list** `[��]`����name�� | �� |
| `ListGetLength` | ��ȡ�б����� | ���� | **list** `[��]`����name�� | 20 |
| `ListContainsItem` | �ж��б��Ƿ����ĳ�� | ����ֵ | **list** `[��]`����name����**item** `[ֵ]` | �� |
| `ListShow` | ��ʾ�б������� | - | **list** `[��]` | �� |
| `ListHide` | �����б������� | - | **list** `[��]` | �� |

**?? ����/�б�������Я�� `name` �ֶΣ�**
```json
{"type":"var","val":"myVar","name":"myVar"}
```

**���л�ʾ����SetVar����**
```json
{"define":"SetVar","sections":[{"params":[{"type":"var","val":"score","name":"score"},{"type":"var","val":"100"}]}]}
```

**���л�ʾ����ListAdd����**
```json
{"define":"ListAdd","sections":[{"params":[{"type":"var","val":"apple"},{"type":"var","val":"myList","name":"myList"}]}]}
```

---

## Music�����֣�

**BlockType��Statement / Operator**

| define | ˵�� | ����ֵ | ���� | ʹ�ô��� |
|--------|------|--------|------|---------|
| `PlayDrum` | ������� | - | **drum** `[��]`�������ͣ���̬�б�����**beats** `[ֵ]`����������Ĭ��1 | �� |
| `RestMusic` | ������ֹ����Ĭ�� | - | **beats** `[ֵ]`����������Ĭ��1 | �� |
| `PlayIntrument` | �������� ?? ������ȱ��ĸn����PlayInstrument | - | **note** `[ֵ]`������ֵ0-127��Ĭ��60��**beats** `[ֵ]`����������Ĭ��1 | �� |
| `SetInstrument` | ���õ�ǰ���� | - | **instrument** `[��]`������������̬�б��� | �� |
| `SetInstrumentPitch` | ���������ٶȣ�BPM�� | - | **tempo** `[ֵ]`���ٶȣ�Ĭ��60 | �� |
| `ChangeInstrumentPitch` | �ı������ٶȣ������� | - | **delta** `[ֵ]`��������Ĭ��20 | �� |
| `GetInstrumentPitch` | ��ȡ��ǰ�����ٶ� | ������ | �� | �� |

**���л�ʾ����PlayIntrument����**
```json
{"define":"PlayIntrument","sections":[{"params":[{"type":"var","val":"60"},{"type":"var","val":"0.5"}]}]}
```

---

## Physics��������

**BlockType��Statement**

| define | ˵�� | ����ֵ | ���� | ʹ�ô��� |
|--------|------|--------|------|---------|
| `FallSetting` | �����Ƿ�������Ӱ�� | - | **can** `[��]`��can�������䣩/ can't���������䣩 | �� |
| `CollideSetting` | �����Ƿ������ײ | - | **can** `[��]`��can / can't | �� |
| `BeFixedSetting` | �����Ƿ�̶����������ƶ��� | - | **be** `[��]`��be���̶���/ be not�����̶��� | �� |

---

## Stage����̨��

**BlockType��Statement / Operator**

| define | ˵�� | ����ֵ | ���� | ʹ�ô��� |
|--------|------|--------|------|---------|
| `PlayDialogueGroup` | ���ŶԻ��� | - | **group** `[��]`���Ի���������̬�б��� | �� |
| `SetDialogueTypingSpeed` | ���öԻ������ٶȣ���/�ַ��� | - | **speed** `[ֵ]`��Ĭ��0.1 | �� |
| `SetDialogueStyle` | ���öԻ���ʽ | - | **style** `[��]`����ʽ������̬�б��� | �� |
| `SetDialoguePlayMode` | ���öԻ�����ģʽ | - | **mode** `[��]`��auto���Զ���/ manual���ֶ��� | �� |
| `SetDialogueCamera` | ���öԻ�ʱ�����Ŀ�� | - | **target** `[��]`��Ŀ����� | �� |
| `SelectedMenuItem` | ��ȡѡ�еĲ˵����ı� | �ַ��� | �� | �� |
| `SelectedMenuItemIndex` | ��ȡѡ�в˵�������� | ���� | �� | �� |
| `PlayVideo` | ������Ƶ | - | **video** `[��]`����Ƶ����**mode** `[��]`��fullscreen / centered / cg | �� |
| `PlayWindowedVideo` | ����С����Ƶ | - | **video** `[��]`��**position** `[��]`��top left/top/top right/left/center/right/bottom left/bottom/bottom right��**offsetX** `[ֵ]`��**offsetY** `[ֵ]` | �� |

---

## Magic�����⹦�ܣ�

**BlockType��Statement / Operator / Trigger / LogicalOperator**

| define | ˵�� | ����ֵ | ���� | ʹ�ô��� |
|--------|------|--------|------|---------|
| `NextLesson` | ������һ�� | - | �� | �� |
| `FailLesson` | ��Ǳ���ʧ�� | - | �� | �� |
| `EndRun` | �������У�OJ�ύ����� | - | **result** `[ֵ]`��Ĭ��"success"��**message** `[ֵ]` | 22 |
| `HideUs` | �������ǣ����ض��� | - | �� | �� |
| `WhenGameStopped` | ��Ϸֹͣʱ������Trigger�� | - | �� | �� |
| `GetCloneId` | ��ȡ��¡�� ID | ���� | �ޣ�sections��[{}]�� | �� |
| `RaycastTest` | ���߼�� | ����ֵ | **dx** `[ֵ]`��**dy** `[ֵ]`��**dz** `[ֵ]` | �� |
| `MoveToAFreePosition` | ������ײ���Ƶ�����λ�ã� | - | �� | �� |
| `IsAvailablePath` | ·�������Ƿ���� | ����ֵ | **dx** `[ֵ]`��**dy** `[ֵ]`��**dz** `[ֵ]` | �� |
| `SpriteClickedSenderName` | ��ȡ����¼����������ƣ�Patches��չ�� | �ַ��� | �� | �� |

---

## My Blocks���Զ����ľ��

**BlockType��Statement / Operator��ȡ���ڶ��壩**

| define ��ʽ | defineMethod | ˵�� |
|------------|-------------|------|
| `{uuid}/myblockdefine` | `"defineMethod"` | �Զ��巽���Ķ���ͷ��sections �� children �����ݣ� |
| `{uuid}/myblockdefine` | `"callMethod"` | �����Զ��巽����sections �Ŵ�������� |
| `{uuid}/myblockdefine` | `"callParam"` + `paramIndex:N` | ��ȡ�Զ��巽���ĵ� N ������ |

**�����Զ���Blockʾ��������ʵ���ļ�����**
```json
{
  "name": "6377b110e62644a28570625c30d5c6ad/myblockdefine",
  "displayName": "�⾰��45����",
  "wrapBlockName": "",
  "fragment": {
    "pos": ["615.9999","216"],
    "head": {
      "define": "6377b110e62644a28570625c30d5c6ad/myblockdefine",
      "sections": [{"children": [
        {"define":"SetCameraFOV","sections":[{"params":[{"type":"var","val":"25"}]}]},
        {"define":"PointInDirection","sections":[{"params":[{},{"type":"var","val":"-90"}]}]},
        {"define":"CameraFollow","sections":[{"params":[{"type":"var","val":"�ӳ�"},{"type":"var","val":"640"},{"type":"var","val":"0"},{"type":"var","val":"500"}]}]}
      ]}]
    }
  }
}
```

**�����Զ���Block��**
```json
{"define":"6377b110e62644a28570625c30d5c6ad/myblockdefine","defineMethod":"callMethod","sections":[{"params":[{"type":"var","val":"����ֵ"}]}]}
```

---

## ��չBlock �� UI��չ

������ `Scripts/Hotfix/HetuExtensions/UI/UIBlockDefines.cs`  
**BlockType��Statement / Operator**

| define | ˵�� | ����ֵ | ���� | ʹ�ô��� |
|--------|------|--------|------|---------|
| `SetTitle` | ���� UI �������� | - | **text** `[ֵ]` | 30 |
| `SetIcon` | ���� UI ͼ�� | - | **icon** `[��]`��ͼ���� | �� |
| `SetChildStringProperty` | ������UI�����ַ������� | - | **child** `[��]`��**property** `[��]`��**value** `[ֵ]` | �� |
| `SetChildListProperty` | ������UI�����б����� | - | **child** `[��]`��**property** `[��]`��**list** `[��]` | �� |
| `SetControllerState` | ���� UI ������״̬ | - | **controller** `[��]`��**state** `[��]` | 16 |
| `PlayTransition` | ���� UI ת������ | - | **animation** `[��]`�������� | �� |
| `StopTransition` | ֹͣ UI ת������ | - | **animation** `[��]`�������� | �� |
| `SetProgressBarValue` | ���ý�����ֵ | - | **value** `[ֵ]`������ֵ | �� |
| `AddProgressBarValue` | ���ӽ�����ֵ | - | **delta** `[ֵ]`������ | �� |
| `SetTransparencyUI` | ���� UI Ԫ��͸���� | - | **transparency** `[ֵ]` | �� |
| `GotoFrontBack` | �Ƶ���ǰ/���� | - | **direction** `[��]`��front / back | 17 |
| `GoForwardBackwardLayers` | ǰ��/����ָ������ | - | **layers** `[ֵ]`��������������ǰ��������� | �� |
| `FollowNode` | UI ê����3D��������ڵ� | - | **bone** `[��]`�������ڵ�����**offset** `[��]` | 1 |

**���л�ʾ����SetProgressBarValue����**
```json
{"define":"SetProgressBarValue","sections":[{"params":[{"type":"var","val":"0"}]}]}
```

---

## ��չBlock �� Animation ���䶯����չ

������ `Scripts/Hotfix/HetuExtensions/Animation/AnimationBlockDefine.cs`  
**BlockType��Statement / LogicalOperator**

| define | ˵�� | ����ֵ | ���� |
|--------|------|--------|------|
| `AnimationMotionTo2DSeconds` | N���ڶ����ƶ���2D���� | - | **x** `[ֵ]`��**y** `[ֵ]`��**time** `[ֵ]`��**easing** `[��]`��Linear�ȣ� |
| `AnimationMotionTo3DSeconds` | N���ڶ����ƶ���3D���� | - | **x** `[ֵ]`��**y** `[ֵ]`��**z** `[ֵ]`��**time** `[ֵ]`��**easing** `[��]` |
| `AnimationMotionDelta2DSeconds` | N��������ƶ�2D | - | **dx** `[ֵ]`��**dy** `[ֵ]`��**time** `[ֵ]`��**easing** `[��]` |
| `AnimationMotionDelta3DSeconds` | N��������ƶ�3D | - | **dx** `[ֵ]`��**dy** `[ֵ]`��**dz** `[ֵ]`��**time** `[ֵ]`��**easing** `[��]` |
| `AnimationTransparencyToSeconds` | N���ڸı�͸���� | - | **target** `[ֵ]`��**time** `[ֵ]`��**easing** `[��]` |
| `AnimationScaleToSeconds` | N���ڸı��С | - | **target** `[ֵ]`��**time** `[ֵ]`��**easing** `[��]` |
| `AnimationDirectionSeconds` | N������ת��ָ���Ƕ� | - | **angle** `[ֵ]`��**time** `[ֵ]`��**easing** `[��]` |
| `StopAllAnimationMotions` | ֹͣ���䶯�� | - | **scope** `[��]`��all / others / self |
| `IsAnimationMotion` | �Ƿ�����ִ�в��䶯�� | ����ֵ | �� |

**���л�ʾ����AnimationMotionTo2DSeconds����**
```json
{"define":"AnimationMotionTo2DSeconds","sections":[{"params":[{"type":"var","val":"0"},{"type":"var","val":"0"},{"type":"var","val":"1"},{"type":"var","val":"Linear"}]}]}
```

---

## ��չBlock �� Patches ������չ

������ `Scripts/Hotfix/HetuExtensions/Patches/PatchesBlockDefine.cs`  
**BlockType��Statement / Operator**

| define | ˵�� | ����ֵ | ���� | ʹ�ô��� |
|--------|------|--------|------|---------|
| `KeepNDecimalPlaces` | ���� N λС�� | ������ | **n** `[ֵ]`��λ����**value** `[ֵ]`����ֵ | �� |
| `StopAnimation` | ָֹͣ����ɫ���� | - | **animation** `[��]`�������� | 8 |
| `SetSaySkin` | ����˵������Ƥ�� | - | **skin** `[��]`��Ƥ���� | 1 |
| `SetThinkSkin` | ����˼������Ƥ�� | - | **skin** `[��]`��Ƥ���� | �� |
| `SpriteClickedSenderName` | ��ȡ����¼����������� | �ַ��� | �� | �� |
| `SetAnimationSpeedRatio` | ���ý�ɫ������������ | - | **ratio** `[ֵ]`�����ʣ�1.0Ϊ������ | �� |

---

## ���л���ʽ�����ٲ�

> ���й��������ʵ�� .ws �ļ���֤������ϸ����ء�

### ���Ĺ���Υ���ᵼ�¹ؿ�����ʧ�ܣ�

1. **������ֵ�������ַ���**��д `"10"` ���� `10`
2. **λ���������ַ�������**��`["100", "150"]`��**����** `{"x":100,"y":150}`
3. **Trigger ���Ͳ��� `next`**��������ȫ������ `sections[0].children` ��
4. **�޲�Block �� section �� `[{}]`**���� `GetCloneId`��`GetSpriteName` �� `"sections": [{}]`
5. **����/�б���������� `name` �ֶ�**��`{"type":"var","val":"x","name":"x"}`
6. **�Զ���Block name �� UUID + "/myblockdefine"**

### �������ͻ���

| ���� type �ֶ� | ���� |
|---|---|
| `"var"` | �ַ���ֵ��������ã����̶�����ֵ�� |
| `"block"` | Ƕ����һ�� Block��val ������ Block JSON�� |
| `{}` | ��ռλ��ĳЩBlock��Ҫ�� |

### BlockFragment �ṹ������Ƭ�Σ�

```json
{
  "pos": ["100", "150"],
  "head": { /* ������ Block JSON���� Trigger �� Statement ��ʼ */ }
}
```

### BlockScript �ṹ���ű��ļ���

```json
{
  "myblocks": [ /* �Զ���Block�����б� */ ],
  "fragments": [ /* BlockFragment �б� */ ],
  "uiState": {"pos": ["0","0"], "scroll": ["0","0"], "scale": "1"}
}
```

### �����ۺ�ʾ����WhenGameStarts �� Forever �� If/Else �� ����������

```json
{
  "pos": ["0", "0"],
  "head": {
    "define": "WhenGameStarts",
    "sections": [{"params": [], "children": [{
      "define": "Forever",
      "sections": [{"params": [], "children": [{
        "define": "IfElse",
        "sections": [
          {
            "params": [{"type":"block","val":{
              "define": "IsTouching",
              "sections": [{"params": [{"type":"var","val":"����"}]}]
            }}],
            "children": [{"define":"IncVar","sections":[{"params":[{"type":"var","val":"score","name":"score"},{"type":"var","val":"1"}]}]}]
          },
          {"params": [], "children": [{"define":"WaitSeconds","sections":[{"params":[{"type":"var","val":"0.1"}]}]}]}
        ]
      }]}]
    }]}]
  }
}
```

### ����ֵ�����ٲ�

| �������� | ��Ƕ������� | ���� Block |
|---|---|---|
| ���� | `[ֵ]` �� | GetCurrentDate, StrLength, ListGetLength |
| ������ | `[ֵ]` �� | Add, GetPosX, GetTimer, GetVolume |
| �ַ��� | `[ֵ]` �� | StrJoin, GetUserName, Answer |
| ����ֵ | `[��]` �� | IsGreator, IsTouching, And, Not |
| ��� | `[ֵ]` �� | Variable, ListGetItemAt, GetPropertyOf |
| - | ����Ƕ�� | ���� Statement / Trigger / BranchStatement |

### ����ö��ֵ�����б�

**������key����**
```
space, ��, ��, ��, ��, any, enter, a-z��26����, 0-9��10����
```

**��ѧ������MathFunc function����**
```
abs, floor, ceiling, sqrt, sin, cos, tan, asin, acos, atan, ln, log, e^, 10^
```

**�������ͣ�GetCurrentDate type����**
```
year, month, day, day of week, hour, minute, second
```

**��ת��ʽ��SetRotationStyle style����**
```
left-right, horizontal, don't rotate, all around
```

**ֹͣ�ű����ͣ�StopScript type����**
```
all, this script, other scripts in sprite
```

**�Ի�����ģʽ��** `auto, manual`  
**��Ƶ����ģʽ��** `fullscreen, centered, cg`  
**��������/��ײ��** `can, can't`  
**�����̶���** `be, be not`  
**����ϵ���ͣ�** `local, world`  
**����ʽ��** `with, without`  
**С��λ�ã�** `top left, top, top right, left, center, right, bottom left, bottom, bottom right`

---

## Block ���ӹ�������˵��

> �������ɺϷ� .ws �ļ��ĺ����߼������й��������Դ���ʵ���ļ���֤��

### ����һ��BlockType ���� Block �ܳ��ֵ�λ��

| BlockType | ����Ϊ fragment head | �ܳ����� `children` �� | ���� `next` ���� | ��Ƕ�� `params`��type="block"�� |
|---|:---:|:---:|:---:|:---:|
| **Trigger** | ? ֻ��������Ϊ head | ? | ? | ? |
| **Statement** | ?������Ƭ�Σ� | ? | ? | ? |
| **BranchStatement** | ?������Ƭ�Σ� | ? | ? | ? |
| **Operator** | ? | ? | ? | ? Ƕ�� `[ֵ]` �� |
| **LogicalOperator** | ? | ? | ? | ? ��Ƕ�� `[��]` �� |

**���Ľ��ۣ�**
- ��˳��ִ�еĿ� �� �� `next` ����
- ��Ž���֧����Ŀ� �� �Ž� `children`
- ����Ϊ����/�����õĿ� �� Ƕ�� `params` �� `type:"block"` ����
- Trigger ��Զ����㣬���ܱ�����

---

### �������`next` ���ӹ���

`next` ��һ����ѡ�ֶΣ�ֵ����һ���ֵ� Block ������ JSON��

```
Block_A
  ���� "next": Block_B
                ���� "next": Block_C   �� ��βû�� next �ֶ�
```

- **������ next ��**��Statement��BranchStatement
- **������ next ��**��Trigger������ children����Operator��LogicalOperator
- BranchStatement �� `next` ��ʾ������֧�ṹ**ִ����֮��**����ִ�еĿ�

---

### ��������`children` �ӿ����

`children` �����飬��**ʵ����ֻ�ŵ�һ�� Block**������ͨ�� `next` ���ӡ�

```json
"children": [
  {
    "define": "Block_A",
    ...
    "next": {
      "define": "Block_B",
      ...
      "next": { "define": "Block_C", ... }
    }
  }
]
```

- children ������ֻ�� **1 ��Ԫ��**����һ���飩
- ��һ����֮������п�ͨ�� `next` �γ�����
- �շ�֧��д `"children": []`

---

### �����ģ�Trigger ���͵�����ṹ

**Trigger ��� body ���� `next`�����Ƿ��� `sections[0].children` �**

```json
{
  "define": "WhenGameStarts",        �� Trigger
  "sections": [{
    "params": [],
    "children": [                    �� body �ĵ�һ����
      {
        "define": "SetVar", ...
        "next": { ... }              �� body �ڲ��� next ����
      }
    ]
  }]
  �� ע�⣺Trigger û�� next �ֶΣ�
}
```

���� Trigger ���ͣ�WhenGameStarts / WhenStartup / WhenReceiveMessage / WhenKeyPressed �ȣ�����ѭ�˹���

---

### �����壺sections �ṹ���

ÿ�� Block ������һ�� Section��Section ���� `params`���������� `children`���ӿ��壩��

| Block | sections ���� | �ṹ˵�� |
|---|:---:|---|
| ��ͨ Statement | 1 | `[{ "params": [...] }]`���� children |
| `Forever` | 1 | `[{ "params": [], "children": [...] }]` |
| `Repeat` | 1 | `[{ "params": [����], "children": [...] }]` |
| `RepeatUntil` | 1 | `[{ "params": [����block], "children": [...] }]` |
| `If` | 1 | `[{ "params": [����block], "children": [...then...] }]` |
| `IfElse` | **2** | section[0]������+then�壻section[1]����params+else�� |
| Trigger | 1 | `[{ "params": [], "children": [...body...] }]` |
| �޲� Operator | 1 | `[{}]`��һ���ն��󣬷ǿ����飩 |

**IfElse ˫ Section ģʽ��������д������**
```json
{
  "define": "IfElse",
  "sections": [
    {
      "params": [{"type":"block","val": {������}}],
      "children": [{...then ��һ��, "next": {...}}]
    },
    {
      "params": [],
      "children": [{...else ��һ��, "next": {...}}]
    }
  ]
}
```

---

### �������������ۣ�Column��������Ƕ�����

| ������ | ���л��еı��� | �ɽ��ܵ����� |
|---|---|---|
| **Variable ��**��`[ֵ]`�� | `{"type":"var","val":"..."}` �� `{"type":"block","val":{Operator}}` | �ַ���/��ֵ �� Operator Block |
| **Logical ��**��`[��]`�� | `{"type":"block","val":{LogicalOperator}}` | **ֻ��**�� LogicalOperator Block |
| **FixedDroplist ��**��`[��]`�� | `{"type":"var","val":"ѡ��ֵ"}` | �̶��ַ�����**����**Ƕ�� Block |
| **Label ��** | **�����л�**���������� params �� | ֻ����ʾ���� |
| **��ռλ** | `{}` | ĳЩ Block���� PointInDirection����һ��������ռλ |

---

### �����ߣ���̬�б� vs �̶�ö�٣�`[��]` �����������ͣ�

���Ϊ `[��]` �Ĳ��������֣�

**�� �̶�ö��**�����ĵ��������г�����
- ��ת��ʽ��`left-right / horizontal / don't rotate / all around`
- ֹͣ���ͣ�`all / this script / other scripts in sprite`
- �������ͣ�`year / month / day / day of week / hour / minute / second`
- ��ѧ������`abs / floor / ceiling / sqrt / sin / cos / tan / asin / acos / atan / ln / log / e^ / 10^`
- ������`space / �� / �� / �� / �� / any / enter / a-z / 0-9`
- �������أ�`can / can't`��`be / be not`
- ����ϵ��`local / world`������`with / without`
- ����ģʽ��`auto / manual`����Ƶģʽ��`fullscreen / centered / cg`
- �������ͣ�`timer / loudness`

**�� ��̬�б�**������ʱ���ݾ��峡����Դ��д���޷�Ԥ��ö�٣���
- ��ɫ/������������ target ������
- ��������PlayAnimation �ȣ�
- ��������SwitchCostume��
- ��������PlaySound / PlayBGM��
- ��Ϣ����BroadcastMessage / WhenReceiveMessage��
- �Ի�������PlayDialogueGroup��
- �Ի���ʽ����SetDialogueStyle��
- �����Ԥ������TransitToCameraPreset��
- ��������SetInstrument���������ͣ�PlayDrum��
- �����ڵ�����AnchorTo��
- ��������GetPropertyOf��

---

### ����ˣ�Variable/List ��������� name �ֶ�

��ȡ�������б�ʱ������ `val` �������� `name` �ֶΣ�����ֵ��ͬ����

```json
? ��ȷ��{"type":"var","val":"score","name":"score"}
? ����{"type":"var","val":"score"}      �� ȱ name�������޷�ʶ��Ϊ��������
```

SetVar / IncVar �ĵ�һ����������������ͬ����Ҫ name �ֶΡ�
ListAdd / ListGetItemAt ���е��б�������ͬ����

---

### �������ӽṹͼʾ

```
BlockScript
������ fragments[]                 �� ����Ƭ���б�
��   ������ BlockFragment
��       ������ pos: ["x","y"]      �� Ƭ���ڻ����ϵ�λ��
��       ������ head                �� Ƭ��ͷ��Trigger ����� Statement��
��           ������ define
��           ������ sections[]
��           ��   ������ params[]    �� ������varֵ �� Ƕ��Operator/LogicalOperator��
��           ��   ������ children[]  �� ��֧���һ���飨������next���ӣ�
��           ������ next            �� ��һ���ֵܿ飨Triggerû�д��ֶΣ�
��               ������ define
��               ������ sections[]
��               ������ next �� ...  �� �ݹ�����
������ myblocks[]                  �� �Զ���Block����
    ������ { name, displayName, columns[], fragment }
```
