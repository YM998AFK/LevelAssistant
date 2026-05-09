# 盘古3D关卡制作 · 13 条硬性设计规则

> 从编排规范剥离的**设计层面**硬规则汇总。每条都是踩坑立规的血泪实证。
> **开工前必读**，交付前对照自检。MUST/NEVER 是元级红线（见 `_shared/constraints.md`），
> 本文件是元级红线之外的"涉及具体子系统怎么做"的细则。
>
> **校验图例**：
> - 🤖 自动 = `verify_gates.py` 脚本能机器拦截
> - 🔍 审查员 = 独立审查员（`explore` + readonly）必检
> - 👀 人工 = agent 自觉 + 设计师确认

---

## §1 · 资源与提问

### R-1 · 遇到疑问必须主动向人类确认 [👀]

完成提问流程、准备生成之前，若出现以下任何一种情况，**必须停下来向设计师提问，不得擅自假设或跳过**：

1. **资源缺口**：需要某个物件/角色/场景，但在 `asset_catalog.md` 中找不到合适的 AssetId，或找到的资源不确定是否匹配
2. **流程歧义**：设计师描述的关卡流程中有步骤顺序不清、条件分支不明确、或需要特殊技术实现但不确定方案
3. **代码推导失败**：无法从提供的代码/伪代码中确定 cin/cout 格式、数据类型、测试值
4. **BGM / 音效不确定**：设计师要求某种风格，但知识库中没有对应 AssetId
5. **任何其他让你感到不确定的地方**：宁可多问一次，也不要生成出错的关卡

> 提问时应具体说明"我不确定 XXX，请问您希望用哪种方案？"，并提供若干可选项。

### R-2 · 调用 PlayAnimation 前必须查该角色的动画清单 [👀 + 🔍]

**绝对禁止从其他角色/参考包"眼熟"就抄动画名** —— 每个角色的动画池完全独立。

**强制流程**：

1. 角色确定后（AssetId 已知），**第一件事**打开 `asset_catalog.md`，搜该 AssetId 行，读"动画列表"列；
2. `PlayAnimation(name)` / `PlayAnimationUntil(name)` 里的 `name` **必须**严格来自该角色清单；
3. 若关卡涉及多角色形态切换（如升级形态、受伤形态），**每个形态单独查**，不能假设"同系列角色有相同动画";
4. 若清单为空 / 只含 idle，**不能使用该角色做动作表演**，要么换资源、要么跟设计师明确"该角色无此动作"。

**三类"动画名"来源**（按实证扩充）：

| 来源 | 示例 | 说明 |
|------|------|------|
| A. 角色模型自带 | `idle, run, jingyataitou` | 来自 `asset_catalog.md` 动画列表 |
| B. 挂在 Character 子节点的 Effect.Name | `队长升级特效` | **运行时动态注册为动画**，详见 §R-6 |
| C. 引擎共享动画池 | `xingfen`（实证存在但不在 catalog 里）| catalog 可能不完整；若设计师示范包已使用，直接采用不用质疑 |

**遇到 catalog 里找不到的动画名，但设计师/参考包在用**：直接沿用，同时在 commit message / 交付说明里备注 "catalog 未收录但实证可用 的 `xxx` 动画"，供下次更新 catalog。

**历史教训（实证）**：

- 小法师升级01/02/03（21360/21361/21362）**只有 `yan_shd / yifu_shd / zui_shd` 三个发光动画**，没有 idle/run/jingya 等肢体动作。曾误调用 `PlayAnimation("jingyataitou")` 导致运行时无响应。
- 同为"队长"系列：20760（法师袍）有 `jingyataitou/qitiao_start` 等 24 个动画；而 21339（抱龙宝宝版）只有 `idle/run` 和 3 个 shd —— **不能共用动画名**。

**标准查询命令**（在对话中执行）：

```
grep "^\| {AssetId} \|" _knowledge/asset_catalog.md
```

查不到就改用 SemanticSearch，或向设计师确认该角色的可用动作。

---

## §2 · 摄像机

### R-3 · 摄像机跟随胸部高度默认 50 [🔍]

**`CameraFollow(target, dist, 0, height)` 第 4 参默认 50**（对 1.2 ~ 1.5m 的标准 Character 即胸部中心）。实证教训：

- 120 对 1.2m 角色**太高**（相机抬头过多，视线在头顶而非胸口）
- 详表见 `presets.md` 中"NPC 胸部高度规范"

缩放类关卡（角色运行时变大）**固定 50**，相机跟随 control 节点而非主角，主角缩放不影响相对高度。

### R-4 · 主角朝向 vs 摄像机朝向 —— 必须反向 [🔍]

**`CameraFollow(target, +X, 0, h)` + `PointInDirection(-90)` 时**：

- 摄像机在 target 的 **X+** 方向（偏移量为正即前方）
- 摄像机朝向 **-90** = 朝 **X-** 方向看回 target
- **主角必须 `PointInDirection(90)`**（朝 X+）才能面对摄像机

**错误写法**：主角也 `PointInDirection(-90)` → 和摄像机**同向** → 看到的是主角**背面** ❌

### R-5 · CameraService.Current 可用 "CamEdit"（设计师示范认证）[👀]

**之前规则**：`Current="CamEdit"` 是正俯视，必须改 `"Camera45"`。
**实证更正**：设计师示范包使用 `Current="CamEdit"`，仍能达到水平视角。**真正决定视角的是 `WhenGameStarts` Trigger 里的 `PointInPitch(90) / PointInDirection(-90)` 积木**，`Current` 字段仅影响编辑器预览。

**建议**：新关卡统一用 `"CamEdit"` 作为 `Current`（编辑器打开是编辑模式，运行时由 BlockScript 接管）。

---

### R-17 · 积木节点类型归属 —— 禁止跨类型使用 [🔍]

> **来源**：`blocks_reference.md` 各节标注 + 引擎实证（跨类型调用静默失效）。  
> 下表按节点类型列出"专属积木"。写入错误节点时引擎**静默忽略**，既不报错也不执行。

---

#### A · CameraService 专属（不能出现在其他任何节点）

| 积木 | 作用 |
|------|------|
| `CameraFollow` | 跟随目标 |
| `CameraLookAt` | 看向目标 |
| `CameraLookAtWithOffset` | 带偏移看向目标 |
| `CameraLookAtPos` | 看向世界坐标 |
| `CameraLookAt2` | 同时看向两目标 |
| `CameraReset` | 重置相机 |
| `SetCameraFOV` | 设置 FOV |
| `ChangeCameraFOV` | 增量调整 FOV |
| `TransitToCameraPreset` | 切换预设视角 |

**反向**：CameraService 节点内禁止出现 `PlayAnimation` / `PlayAnimationUntil` / `ChangeSize` / `SetSize` / `Hide` / `Show`（无骨骼/无可见性逻辑，调用无效）。

---

#### B · UIView 专属（只能在 UIView 节点的 BlockScript 内使用）

**2D 坐标移动**（明确标注"UI元素"）：

| 积木 | 说明 |
|------|------|
| `GotoPosition2D` | 瞬移到 2D 坐标（UI元素） |
| `GlideSecsToPosition2D` | N 秒滑动到 2D 坐标 |
| `GotoFrontBack` | 移到物件前/后层级（UI层序） |
| `GoForwardBackwardLayers` | 前进/后退指定层数 |

**UI 扩展积木**（来自 `UIBlockDefines.cs`）：

| 积木 | 说明 |
|------|------|
| `SetTitle` | 设置 UI 标题文本 |
| `SetIcon` | 设置 UI 图标 |
| `SetChildStringProperty` | 设置子UI字符串属性 |
| `SetChildListProperty` | 设置子UI列表属性 |
| `SetControllerState` | 设置 UI 控制器状态 |
| `PlayTransition` | 播放 UI 转场动画 |
| `StopTransition` | 停止 UI 转场动画 |
| `SetProgressBarValue` | 设置进度条值 |
| `AddProgressBarValue` | 增加进度条值 |
| `SetTransparencyUI` | 设置 UI 透明度 |
| `FollowNode` | UI 锚定到 3D 骨骼节点 |

**Animation 补间扩展**（来自 `AnimationBlockDefine.cs`，UIView 2D 动画）：

| 积木 | 说明 |
|------|------|
| `AnimationMotionTo2DSeconds` | N 秒移动到 2D 坐标 |
| `AnimationMotionDelta2DSeconds` | N 秒增量移动 2D |
| `AnimationTransparencyToSeconds` | N 秒改变透明度 |
| `AnimationScaleToSeconds` | N 秒改变大小 |
| `AnimationDirectionSeconds` | N 秒旋转到角度 |
| `StopAllAnimationMotions` | 停止补间动画 |
| `IsAnimationMotion` | 是否在执行补间动画 |

**反向**：UIView 节点内禁止出现以下 3D 专属积木（见 D 组）：  
`TurnUp` / `TurnDown` / `PointInPitch` / `GotoPosition3D` / `GlideSecsToPosition3D` / `GlideSecsToPosition3DAndSetRotation` / `FallSetting` / `CollideSetting` / `BeFixedSetting`

---

#### C · Character 专属（需要骨骼系统 / NavMesh，写入 MeshPart/UIView/CameraService 静默失效）

**角色动画**（需要动画骨骼）：

| 积木 | 说明 |
|------|------|
| `PlayAnimation` | 播放动画（非阻塞） |
| `PlayAnimationUntil` | 播放动画直到结束（阻塞） |
| `PlayAnimationAndWait` | 播放动画并等待指定时长 |
| `PlayAnimationUntilAndWait` | 播放动画结束后再等待 |
| `PlayEmotionAnimation` | 播放表情动画 |
| `StopAnimation` | 停止指定动画 |
| `SetAnimationSpeed` | 设置动画速度 |
| `SetAnimationSpeedRatio` | 设置动画速率 |

**导航移动**（需要 NavMesh Agent）：

| 积木 | 说明 |
|------|------|
| `RunToTargetAndWait` | 跑向目标并等待到达 |
| `WalkToTargetAndWait` | 走向目标并等待到达 |
| `RunToTarget` | 跑向目标（不等待） |
| `WalkToTarget` | 走向目标（不等待） |
| `FollowAndKeepDistance` | 跟随并保持距离 |
| `StartWalk` | 开始行走/跑步动画 |
| `StopWalk` | 停止行走 |
| `TurnToTargetInSecs` | N 秒内朝向目标 |
| `TurnToAngleInSecs` | N 秒内转到指定角度 |

**骨骼绑定**：

| 积木 | 说明 |
|------|------|
| `AnchorTo` | 锁定到角色骨骼节点 |

---

#### D · 3D 节点专属（Character + MeshPart，UIView 禁止使用）

明确标注"仅3D"或需要 3D 空间语义：

| 积木 | 说明 |
|------|------|
| `TurnUp` | 向上旋转（**仅3D**） |
| `TurnDown` | 向下旋转（**仅3D**） |
| `PointInPitch` | 设置俯仰角（3D） |
| `GotoPosition3D` | 瞬移到 3D 坐标 |
| `GlideSecsToPosition3D` | N 秒滑动到 3D 坐标 |
| `GlideSecsToPosition3DAndSetRotation` | 滑动到 3D 坐标并设置旋转 |
| `FallSetting` | 设置是否受重力 |
| `CollideSetting` | 设置是否开启碰撞 |
| `BeFixedSetting` | 设置是否固定（不可移动） |

**同时**，D 组积木中的 3D 坐标积木（`GotoPosition3D` / `GlideSecsToPosition3D`）  
**禁止出现在 UIView / CameraService 节点**（节点无 3D 变换语义，调用静默失效）。

---

#### E · 通用积木（所有节点类型均可使用）

以下积木不受节点类型限制（Events、广播、变量、运算符、Control 等全部类别）。  
代表性通用积木：`BroadcastMessage` / `WhenReceiveMessage` / `SetVar` / `WaitSeconds` / `If` / `Repeat` / `Forever` / `Show` / `Hide` / `SetSize` / `ChangeSize` / `PointInDirection` / `PlaySound` / `PlayBGM` / `SaySeconds` / `ThinkSeconds`

---

**脚本自动拦截**：`check_reviewer_items.py` 的 R17 检查覆盖 A/B/C/D 四组违规（自动 PASS/FAIL）。

**历史教训**：CameraService 内误写 `PlayAnimation("idle")` → 相机静止不动，排查耗时 1 小时。


---

### R-14 · 摄像机三种控制模式 —— 禁止混用 [🔍]

> **核心区别**：`CameraFollow` 的参数是**相对角色偏移**；`GlideSecsToPosition3D` / `GotoPosition3D` 的参数是**世界绝对坐标**。两者单位相同（cm），但语义完全不同。

| 模式 | 积木 | 参数语义 | 适用场景 |
|------|------|---------|---------|
| **跟随偏移** | `CameraFollow(目标, D, oY, H)` | 相对目标角色的偏移量 | OJ/关卡全程跟随主角 |
| **世界定位** | `GlideSecsToPosition3D(t,X,Y,Z)` / `GotoPosition3D(X,Y,Z)` | 摄像机世界绝对坐标 | 分镜固定机位、切镜头 |
| **锁定追踪运镜** | `GlideSecsToPosition3D` ＋ `RepeatUntil{PointTowards}` 并行 | 位置=世界坐标；朝向=持续指向角色 | 演出运镜（镜头边移动边盯目标）|

**锁定追踪运镜结构**（两片段并行，来自视角参考包实证）：
```
[片段A - WhenGameStarts]          ← 控制位移
  GlideSecsToPosition3D(t, X, Y, Z)    ← 滑到世界坐标，可连续多段

[片段B - WhenGameStarts]          ← 控制朝向，与片段A并行
  RepeatUntil(<结束条件>)
    PointTowards(_, 目标角色)     ← 每帧更新，持续盯着目标
```

---

## §3 · Effect 特效

### R-6 · Effect 作为 Character 子节点时，用 PlayAnimation(特效名) 播放（关键机制）[🔍]

**设计师示范实证**：挂在 Character 下的 Effect 节点，其 `Name` 字段会被**动态注册为一个"动画"**，可直接通过 `PlayAnimation("<Effect.Name>")` 触发播放。这是 `blocks_reference.md` 说的 "动画名（含循环动画的动态列表）" 的完整含义。

**标准结构**：

```json
[Character] 小法师队长  AssetId=20760
  [BlockScript]   ← 角色脚本
  [Effect] 队长升级特效  AssetId=22238
      props: {"Name": "队长升级特效", "EditMode": 0, "AssetId": 22238,
              "Loop": false, "FullScreenBeforeUI": true}
      # 不要 Visible 字段、不要 Position 字段
```

**脚本调用**：

```python
When_ReceiveMessage("大升级",
    PlayAnimation("队长升级特效"),   # ← 特效作为"动画"直接触发，无需 Show/Hide
    PlayAnimationUntil("xingfen"),
    ...
)
```

**老做法（错误）**：用独立 MeshPart 挂点 + BlockScript 的 `Show()/Hide()` 控制 Effect 可见性 → 繁琐而且 Visible 设置容易让特效不播。

**老做法（已废弃）回看 git 历史即可，从此一律用此新机制。**

### R-7 · Effect props 严格对齐参考包 —— 禁止设 Visible=false [🔍]

**参考包实证**（`Basic/LabelBubble` 关卡 d#14-1#8）：Effect 节点的 props **只应包含**

```json
{"Name": "...", "EditMode": 0, "AssetId": <id>, "Loop": false, "FullScreenBeforeUI": true}
```

**不要**给 Effect 写 `Visible: false` —— 实证会导致特效永远不播放。
可见性由父容器（通常是一个 MeshPart 空挂点）的 `Visible` 控制，BlockScript 里用 `Show() / Hide()` 控制父容器即可。

---

## §4 · 角色表现

### R-8 · 角色放大必须"有过程" —— 用 ChangeSize 渐变 [🔍]

**设计师要求**："角色变大需要体现过程，比如重复执行 N 次等待 0.1 秒，角色大小增加 10"。

**错误写法**：瞬间 `SetSize(130)` —— 观众看到的是"一帧切换"，没有变身感。

**正确写法**：使用 `ChangeSize(delta)` 配合 `Repeat` 渐变

```python
Repeat_(
    "3",                # 重复 3 次
    WaitSeconds("0.1"),
    ChangeSize("10")    # 每次 +10% → 累计 +30%
)
```

**推荐渐变参数**：

| 最终增量 | 循环次数 | 每次增量 | 单次等待 | 总时长 |
|---|---|---|---|---|
| +30%（Lv.5） | 3 | 10 | 0.1s | 0.3s |
| +60%（Lv.10，从 130 到 160 再 +30）| 3 | 10 | 0.1s | 0.3s |
| +100%（缓慢展示）| 10 | 10 | 0.15s | 1.5s |

### R-9 · 表现时序设计 —— 并行 vs 串行 [🔍]

**核心原则**：**因果依赖 → 串行；同属一个"情绪单元" → 并行**。把所有表现要素分成 Phase，每个 Phase 内尽量并行以堆叠冲击感，Phase 之间串行以体现因果。

#### PlayAnimation vs PlayAnimationUntil 选择规则

| 积木 | 行为 | 使用场景 |
|------|------|---------|
| `PlayAnimation` | **非阻塞**，立即执行下一条 | 动画应与后续动作**并行**时（如惊讶+开箱同时） |
| `PlayAnimationUntil` | **阻塞**，等动画播完才继续 | 动画必须**完成后**才能继续时（如全屏特效播完再结算） |

**每次调用动画积木前，必须判断**：这个动画是否需要和下一个动作同时执行？
- 角色惊讶 + 开箱 → **并行** → `PlayAnimation`
- 全屏通过特效 → **必须播完** → `PlayAnimationUntil`
- 开箱动画（在箱子自己的脚本里） → **非阻塞即可** → `PlayAnimation`

**并行实现机制**：

| 需要并行 | 用什么积木 |
|---|---|
| 特效 + 动作（同一角色）| 两个 `PlayAnimation(...)`（非阻塞）连写即可，两者同时开始 |
| 角色变大 + 角色做动作（同一角色）| 在同一 Character 下新增一个 `WhenReceiveMessage("开始变大")` 片段，里面放 `Repeat + ChangeSize`。主脚本用 **`BroadcastMessage("开始变大")`（不带 AndWait，非阻塞）** 启动它，然后主脚本继续阻塞执行动作 `PlayAnimationUntil`。两条消息处理协程天然并行。 |
| UI 通知 + 角色动作 | UI 在独立 UIView 节点，不同节点的 `WhenReceiveMessage` 本身就是并行协程，不需要额外处理 |
| 背景音效 + 主流程 | `PlaySound`（非阻塞）主线继续 |

**串行实现机制**：

- `PlayAnimationUntil` 阻塞直到动作结束
- `BroadcastMessageAndWait` 阻塞直到所有监听者脚本执行完
- `WaitSeconds` 显式等待

**判据表**：

| 要素 A ↔ 要素 B | 关系 | 原因 |
|---|---|---|
| 特效爆发 ↔ 角色动作 | **并行** | 都是"爆发瞬间"，观众应同时感知 |
| 角色变大 ↔ 角色动作 | **并行** | 观众要看到"在动作中变大"，而非"动作完了才变大" |
| UI 通知 Show ↔ 主流程 | **并行** | UI 不应阻塞游戏节奏 |
| 角色动作完成 ↔ 变身形态闪烁 | **串行** | 动作是"蓄力"，形态是"成型"，有先后因果 |
| 形态闪烁完成 ↔ 回到 idle | **串行** | 必须闪完才能收尾 |
| 摄像机调整 ↔ 变大 | **串行在变大之后** | 相机要跟新身高走，需等变大结束 |

**"升级"类事件的参考模板**（3 Phase）：

```python
When_ReceiveMessage("大升级",
    # Phase 1 (0 ~ 2s) 爆发期：特效 / 变大 / 动作 三线并行
    PlayAnimation("队长升级特效"),    # 非阻塞
    BroadcastMessage("开始变大"),     # 非阻塞（触发下方副片段的渐变协程）
    PlayAnimationUntil("xingfen"),    # 阻塞 ~2s（变大 1.2s 已在期间悄悄完成）
    # Phase 2 (2 ~ 5s) 变身期：形态闪光（阻塞串行）
    BroadcastMessageAndWait("闪烁升级1"),
    # Phase 3 回归
    PlayAnimation("idle"))

When_ReceiveMessage("开始变大",        # 副片段：变大协程，与主线并行
    Repeat_("6", WaitSeconds("0.2"), ChangeSize("5")))
```

**关键陷阱**：如果把变大 `Repeat` 直接写在大升级主线里，它会**阻塞动作完成之后才开始**，导致观众看到"动作完 → 形态闪完 → 突然长大"的尴尬顺序。**必须用 `BroadcastMessage`（非阻塞）把变大拆到独立协程**。

**变大 1.2s 的选择理由**：xingfen 动作约 2s，变大 1.2s < 动作 2s，让观众在动作期间看到明显的"长大过程"，同时在动作收尾前变大就位，不会"边闪光边还在长大"。

---

## §5 · UI

### R-10 · UI View 可选样式（目前已知）[👀]

| View | Package | 外观 | 用途 |
|---|---|---|---|
| `LabelBubblenobg` | Basic | 纯文字无底框 | 跟随头顶的 Lv.X 标签、低干扰提示 |
| `LabelBubble` | Basic | 带气泡底框 | 中央/角落提示条，黑字在底框上更清晰 |

目前参考包内**仅见此两种**。若设计师要"金字/发光"等特殊样式，告知设计师"未在知识库中找到对应 View"，不要伪造 View 名。

### R-11 · UI 屏幕空间感（默认 1280 x 720）[🔍]

| 位置 | 坐标 + pivot | 典型用途 |
|---|---|---|
| 屏幕正中 | `position=[640, 360]`, `pivot=[0.5, 0.5]` | 重要对话框、结算画面 |
| 上方居中 | `position=[640, 120]`, `pivot=[0.5, 0]` | 剧情字幕、标题 |
| **右上角通知条** | `position=[1180, 90]`, `pivot=[1, 0]`, `size=[380, 100]` | 升级/成就通知 |
| 左下角 | `position=[100, 630]`, `pivot=[0, 1]` | 小提示、版本信息 |
| 跟随角色头顶 | 使用 `Follow` 字段 + `FollowNode=TopBoneCAPFix` | 血条/等级条 |

设计时**必须指出**位置是否会**遮挡**主角/核心场景元素。正中央对话框在"角色表演为主"的关卡要避开。

---

## §6 · 移动与碰撞

### R-12 · 禁止角色在同一时间段移动到同一位置（运行时碰撞）[🔍]

静态摆放规则（`resource_index.jsonl` 的 `size_tier` + `presets.md`）解决的是**初始 Position**；但 `MoveTo / WalkTo / MoveBy / RunToTargetAndWait / FollowTarget / Glide*` 等**移动类积木**在同一剧本时段内若让两个角色终点重合或接近，仍会视觉重叠 / 互相穿模。`verify_gates.py` 只看静态 JSON，**不拦截**运行时轨迹碰撞。

**"同一时间段"的判定（满足任一即算同时段）**：

- 共享同一父 `sections[*].children`，且中间不被 `WaitSeconds / Wait / Barrier` 类阻塞积木隔开
- 挂在同一广播响应（`WhenReceiveMessage` 同一 message）下同时启动
- 放在同一并发积木（如 `Parallel` / 同一 BlockScript 不同 fragment 但共享触发器）下同帧执行

**硬阈值**：

- 两个角色的**终点欧氏距离 < 1m** → 视为重叠，**禁止**（对应 MUST/NEVER 的 N7）
- 移动过程中轨迹交叉但**终点分开 ≥ 1m** → 允许
- 追逐 / 碰撞剧情需要"贴上去"的视觉效果：用 `PlayAnimation("被撞飞")` + 同帧 `Hide()` 或 `ChangeSize` 替代真的"MoveTo 到同一点"

**三种补偿做法（择其一）**：

1. **错位终点**：同一波次的两个角色目标点错开 ≥ 1m。例：队长 `MoveTo [1, 0.27, 0]`、队员 `MoveTo [1, 0.27, 1.2]`。
2. **时序隔开**：在两个 Move 之间插 `WaitSeconds(动作周期)` 或用一次广播串联，避免同帧执行。
3. **替身锚**：在终点放一个 `Visible=false` 的 MeshPart 作锚，每个角色 MoveTo 各自的锚，不同锚之间保持 ≥ 1m 间距。

---

### R-13 · 瞬时动画播完必须显式指定后续状态 [🔍]

> **背景**：`animation_dict.md` 把动画分为 **闲置**（可循环）和 **瞬时**（单次播放，播完停在最后一帧）。  
> 用 `PlayAnimation` 触发瞬时动画后，角色会**卡在最后帧**，没有任何引擎自动恢复逻辑。  
> 用 `PlayAnimationUntil` 同理，只是主线被阻塞了，结束后仍停在最后帧。

**强制要求**：每次使用瞬时动画，后续 **必须** 接一条动画状态指令（三选一）：

| 后续策略 | 何时使用 | 写法 |
|---------|---------|------|
| **恢复 idle** | 动画只是短暂反应，之后无特定姿态 | `PlayAnimation("idle")` |
| **接循环动画** | 动画结束后角色进入持续姿态（说话、思考、奔跑…）| `PlayAnimation("danxin")` / `PlayAnimation("tonghua_loop")` 等 |
| **触发下一动作** | 动画结束即开始下一段行为，靠主线 `BroadcastMessageAndWait` 衔接 | 瞬时动画用 `PlayAnimationUntil(…)` 阻塞，主线自然接下一条积木 |

**判断流程**：

```
播放瞬时动画后：
  └ 此角色之后还会被再次调用 → 不影响，idle 即可
  └ 此角色需要"保持某个情绪姿态"一段时间 → 接对应循环动画
  └ 此角色立刻进入下一段脚本（主线串行）→ 用 PlayAnimationUntil 阻塞，结束后 idle
```

**典型代码模板**：

```python
# ✅ 惊讶瞬时 → 恢复 idle
WhenReceiveMessage("震惊气泡"):
    PlayAnimationUntil("jingya")   # 阻塞直到播完
    PlayAnimation("idle")          # 显式恢复

# ✅ 惊讶瞬时 + 思考气泡同时展示（并行）→ 结束后 idle
WhenReceiveMessage("震惊气泡"):
    PlayAnimation("jingya")        # 非阻塞，开始播
    ThinkSeconds("！！", 2)        # 主线 2s 阻塞
    PlayAnimation("idle")          # 2s 后恢复（此时 jingya 单次早已播完）

# ✅ 瞬时 + 接循环（保持担心状态直到场景结束）
WhenReceiveMessage("雪球台词1"):
    PlayAnimation("jingxia")       # 非阻塞，惊跑起始
    PlayAnimation("danxin")        # 立即切换到循环担心姿态（覆盖前一条）
    SaySeconds("…", 3)
    PlayAnimation("idle")          # 台词结束后收尾

# ❌ 禁止：瞬时动画后无任何收尾
WhenReceiveMessage("震惊气泡"):
    PlayAnimation("jingya")        # ← 角色永久卡在最后帧
    ThinkSeconds("！！", 2)
    # 没有 idle → BUG
```

**在 `animation_dict.md` 的快速判断**：  
"瞬时" 列 → 必须收尾；"闲置/跑/走" 列 → 会自动循环，不强制收尾（但建议场景结束时统一 `PlayAnimation("idle")`）。

---

## §7 · 站位与阵型

> 完整规则与阵型模板见 `_knowledge/positioning.md`。以下为设计层核心约束。

### R-15 · 多角色站位 —— 禁止单排一字 [🔍]

三个及以上角色时，**至少使用两档 X 深度值**，形成有纵深的队形。不允许所有角色 X 值完全相同（单排一字）。

**必须按 `positioning.md §2 阵型系统` 排布**，从以下模板选择（或使用纯散点）：
- 三角形（前1后2 / 前2后1）
- 弧形/扇形（3~5人）
- 菱形（4人）
- V 字形（5人）
- 纵队（跟随/行军场景）

**判断准则**：
- ✅ 角色 X 值**不全相同** → 有纵深，通过
- ❌ 角色 X 值**完全相同** → 单排一字，禁止
- ⚠️ 两人场景 X 可相差 ≥ 0.5m 构成错位，无需强制大差异

**例外**：物件（MeshPart）用于数量展示时的单排排列可以；OJ关卡主角+control无NPC时无此约束。

---

### R-16 · 摄像机参数必须反推，禁止直接套固定预设 [🔍]

`CameraFollow` 的 distance / height / FOV 必须从角色分布的 spread 反推计算（见 `positioning.md §3`），不允许对任何场景直接套预设固定值。

**允许的例外**：设计师在确认单【视角参数】中已明确指定数值，交付报告中须注明"视角参数来自确认单"。

---

## §8 · 快速自检表（交付前对照）

| 规则 | 校验 | 交付前必看的字段 |
|---|---|---|
| R-1 遇疑必问 | 👀 | 交付消息"未决问题"栏为空，或已声明"由设计师授权继续" |
| R-2 动画名查表 | 👀 + 🔍 | 每个 PlayAnimation 的动画名在 asset_catalog 或 Effect.Name 出现过 |
| R-3 相机高度 50 | 🔍 | `CameraFollow` 第 4 参是否为 50（缩放关卡固定）|
| R-4 主角朝向反向 | 🔍 | `PointInDirection` 方向 vs 相机 offset 方向异号 |
| R-5 CamEdit 可用 | 👀 | Current 字段不强求 Camera45 |
| R-6 Effect 作为动画 | 🔍 | 挂 Character 的 Effect 通过 `PlayAnimation(Effect.Name)` 触发 |
| R-7 Effect 不设 Visible=false | 🔍 | props 仅含 Name/EditMode/AssetId/Loop/FullScreenBeforeUI |
| R-8 ChangeSize 渐变 | 🔍 | 放大动作走 `Repeat + ChangeSize`，无 `SetSize` 瞬间大数值 |
| R-9 并行 vs 串行 | 🔍 | 爆发期用非阻塞，因果期用 AndWait/Until |
| R-10 UI View 白名单 | 👀 | 只用 LabelBubble / LabelBubblenobg |
| R-11 UI 屏幕坐标 | 🔍 | 1280×720 基准，正中央别挡主角 |
| R-12 终点间距 ≥1m | 🔍 | 同时段 MoveTo 终点欧氏距离 ≥ 1m |
| R-13 瞬时动画收尾 | 🔍 | 每个 `PlayAnimation/Until(瞬时)` 后必须接 `PlayAnimation("idle")` 或循环动画；用 `animation_dict.md` 类型列判断是否瞬时 |
| R-14 摄像机模式禁混用 | 🔍 | `CameraFollow` 参数=相对偏移；`GlideSecsToPosition3D` 参数=世界绝对坐标；演出运镜用并行双片段 |
| R-15 站位三层流程 | 🔍 | 所有坐标来自步骤2.5三层流程输出（能站下→能动开→阵型）；多角色 X 值不全相同 |
| R-16 摄像机反推 | 🔍 | CameraFollow 参数由 spread 反推（见 `positioning.md §3`），非直接套预设固定值 |
| R-17 摄像机禁动画积木 | 🔍 | CameraService / Camera 节点及其 BlockScript 内无 `PlayAnimation` / `PlayAnimationUntil` / `ChangeSize` / `Hide` / `Show` |

---

## 相关文档

- `_shared/constraints.md` —— MUST / NEVER 元级硬红线
- `presets.md` —— 摄像机预设、NPC 胸部高度、坐标系统零条规则
- `positioning.md` —— 站位三层流程、阵型系统、摄像机反推（R-15/R-16 对应的完整执行手册）
- `resource_index.jsonl` / `asset_catalog.md` —— 角色动画清单（和 R-2 配套，用 rg 查角色的 `animations` 字段）
- `animation_dict.md` —— 拼音动画名释义
- `pitfalls.md` —— 已知坑库（各族专属坑）
