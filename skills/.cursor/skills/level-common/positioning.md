# 盘古3D关卡 · 站位与阵型系统

> **调用时机**：由 `creator_skill.md` 的**步骤2.5**（站位规划）和**步骤3.7**（摄像机反推）强制引用。
> 生成员不得跳过，不得在步骤3场景树配置时直接手拍坐标。

---

## §1 · 选址三层流程

> **决策优先级从高到低**。下一层只在上一层全部通过后才执行。任何一层失败，回到第一层重选坐标。

```
第1层：能站下（合法性硬约束）
  ↓ 全部通过
第2层：能动开（运动空间预留）
  ↓ 全部通过
第3层：视觉好看（阵型 + 中心）
  ↓ 全部通过
【输出：确定坐标表】→ 步骤3.7 反推摄像机
```

---

### 第1层：能站下

每个角色/物件坐标必须**全部满足**以下条件：

| 条件 | 说明 |
|---|---|
| navmesh 可行走 | `is_walkable(x, z) == True`；详见 `navmesh.md` |
| 离边界足够 | `dist_to_boundary(x, z) ≥ 0.5m`（角色碰撞体不穿墙） |
| 地面高度 | Y = `0.27`（地面常数，空中场景除外） |
| 角色两两间距 | 人形角色任意两人欧氏距离 ≥ 1m（对应 C6/N6） |
| 与 control 间距 | 每个角色离 control ≥ 0.5m |

**不满足 → 重选坐标，不得强行继续。**

> 默认室内场景 28746 无需工具验证（已知范围 X:0~3, Z:-5~+5 均合法），其他场景必须调用 `navmesh_validate.py`。

---

### 第2层：能动开

首先判断角色是否有移动行为，再按情况处理：

| 移动类型 | 预留规则 |
|---|---|
| 无移动积木（只有动画） | 无额外要求，第1层满足即可 |
| `MoveTo / WalkTo / MoveBy` | 终点坐标也须满足第1层；路径不穿障碍 |
| `FollowTarget / RunToTargetAndWait` | 跟随路径覆盖区域均需可行走 |
| 多角色同时移动 | 所有终点两两间距 ≥ 1m（N7），终点也满足第1层 |

**关键原则**：终点不合法时，**往回倒推初始站位**给运动留余量，而不是在终点附近打补丁。

---

### 第3层：视觉好看

前两层全部通过后，在合法坐标区内按以下优先级选位置：

1. **靠近场景开阔中心**（dist_to_boundary 较大的区域），而非贴墙一角
2. **队形有纵深**（多角色时 X 值不能全部相同，见 §2 阵型系统）
3. **control 在角色群重心**（所有角色坐标的 X/Z 均值）
4. **朝向自然**（按场景和演出类型选合适的 PointInDirection）

---

## §2 · 阵型系统

### 密度参数 S

**S 是队形的基准间距单位**，同时控制：核心槽之间的间距、散点与已放置角色的最小间距。

| 密度档 | S 值 | 适用场景 |
|---|---|---|
| **compact（紧凑）** | 1.0m | 亲密对话、小场景、默认教室单区域 |
| **normal（标准）** | 1.5m | 大多数演出关卡（推荐默认） |
| **loose（疏散）** | 2.0m | 大场景、战场感、角色需要大幅移动 |

> 选 S 的依据：场景可用区域 + 角色数量。若 compact 下所有角色都能放下且有 navmesh 余量，用 compact；否则依次升档。

---

### 阵型模板

以下坐标均相对**队形中心点 O = (cx, 0.27, cz)**，cx/cz 由第3层选址确定。

#### 三角形·前1后2（适合主角在前）

```
核心槽数：3
前排：O + (+S×0.7, 0, 0)        ← 主角/焦点角色
后左：O + (0, 0, -S)
后右：O + (0, 0, +S)
```

#### 三角形·前2后1（适合发令者/老师在后）

```
核心槽数：3
前左：O + (+S×0.7, 0, -S×0.7)
前右：O + (+S×0.7, 0, +S×0.7)
后中：O + (0, 0, 0)             ← 发令者/权威角色
```

#### 弧形/扇形（适合3~5人围绕焦点）

```
核心槽数：3~5（按角色数取）
半径 R = S × 1.2
角度范围：-60° ~ +60°（3人）/ -80° ~ +80°（5人），从中心 Z 轴均匀分配
中间角色 X 偏移最大（最靠摄像机），两侧递减：
  X_i = O.x + R × cos(angle_i)
  Z_i = O.z + R × sin(angle_i)
  ← 注意：angle=0 对应 Z 轴，即屏幕正中
```

#### 菱形（4人标准阵）

```
核心槽数：4
前：O + (+S, 0, 0)
左：O + (0, 0, -S)
右：O + (0, 0, +S)
后：O + (-S×0.7, 0, 0)
```

#### V 字形（5人，适合"出击"感）

```
核心槽数：5
顶点：O + (+S×1.5, 0, 0)       ← 最前
左翼前：O + (+S×0.7, 0, -S)
右翼前：O + (+S×0.7, 0, +S)
左翼后：O + (0, 0, -S×2)
右翼后：O + (0, 0, +S×2)
```

#### 并排（2~N人，适合静态展示/OJ）

```
核心槽数：N
全部 X = O.x
Z_i = O.z + (i - (N-1)/2) × S   ← 均匀分布，居中
```

> ⚠️ 并排（单排一字）是**物件展示的正确做法**，但对**人形角色不推荐**（缺乏纵深感）。仅在角色数≤2 或有明确"站成一排"剧情要求时使用。

#### 纵队（跟随/行军）

```
核心槽数：N
全部 Z = O.z（或略有偏移以防完全重叠）
X_i = O.x + i × S               ← 从后到前排列，第0位最靠镜头
```

#### 纯散点（无阵型）

```
核心槽数：0
全部角色走散点放置逻辑（见下方）
适用：自然聚集感、临时站位、无固定关系的NPC群
```

---

### 角色数 > 核心槽容量时

多出来的角色**自动变散点**，不强行塞入阵型：

```
if len(chars) > formation.core_slots:
    core_chars   = chars[:formation.core_slots]   # 按主次排序
    scatter_chars = chars[formation.core_slots:]  # 剩余走散点
```

---

### 散点放置规则

```
对每个散点角色，依次执行：
  1. 候选区 = navmesh可行走 ∩ dist_to_boundary ≥ 0.5m ∩ 摄像机可见范围内
  2. 过滤：距任何已放置角色 < S 的位置排除
  3. 在候选区内优先选 dist_to_boundary 较大的位置（靠近开阔处，不贴墙）
  4. 若候选区为空 → 停止，报告"散点[角色名]无合法位置"，等主 agent 指示
  5. 放置后更新已占用位置列表，供后续散点使用
```

---

### 朝向参考

| 场景类型 | 推荐朝向 |
|---|---|
| 演出/讲解（面向摄像机） | `PointInDirection(90)` |
| 游戏主角奔跑（背对摄像机） | `PointInDirection(-90)` |
| 两人 Z 轴相对站位（面对面） | A: `PointInDirection(0)` / B: `PointInDirection(180)` |
| 两人 X 轴相对站位（一前一后面对面） | 前者: `PointInDirection(-90)` / 后者: `PointInDirection(90)` |
| 背靠背（Z 轴排列） | A: `PointInDirection(180)` / B: `PointInDirection(0)` |
| 弧形/围圈（各自朝中心点） | `PointInDirection(degrees(atan2(dx, dz)))`，dx/dz 为朝中心的向量 |
| 纵队跟随 | 全部与领队相同朝向 |

**移动后朝向重置**：`MoveTo / WalkTo` 完成后角色自动面朝移动方向，演出结束时必须显式 `PointInDirection` 复位。

---

### 特殊情况

| 情况 | 处理方式 |
|---|---|
| 角色 Scale 差异大（如 0.6 vs 1.0） | 视觉间距感不均，建议 compact 下 S 适当增加 0.2~0.3m |
| 非默认场景（多岛/走廊） | 第1层必须调 `navmesh_validate.py`；走廊场景优先用纵队阵型 |
| 有大型物件（宝箱/机器等）占位 | 物件也算占位，散点放置时与物件间距同样 ≥ S |
| OJ关卡（主角+control，无NPC） | 跳过阵型，直接用单人站位（面向摄像机），摄像机反推仍需执行 |
| 摄像机可见范围限制 | 横向 Z 超过 ±5m 可能出画；弧形/V字阵型横向需校验 |

---

## §3 · 摄像机反推

> **调用时机**：步骤3.7，所有角色/物件坐标已确定后执行。
> **输出**：control 节点坐标 + `CameraFollow` 完整参数（直接写入步骤4 BlockScript）。

---

### Step A：计算 control 位置

```python
positions = [角色坐标列表] + [关键物件坐标列表]  # 排除 control 本身

cx = mean(p.x for p in positions)
cz = mean(p.z for p in positions)
control.position = (cx, 0.27, cz)

# 横向/纵向跨度
spread_z = max(p.z for p in positions) - min(p.z for p in positions)
spread_x = max(p.x for p in positions) - min(p.x for p in positions)
spread = max(spread_z, spread_x)   # 取两者中较大值作为约束
```

---

### Step B：选预设档位（锁俯仰角）

| spread | 档位 | Pitch | 基准 distance | 基准 FOV |
|---|---|---|---|---|
| ≤ 2m | 预设A | 135（俯45°） | 200cm | 25° |
| 2m ~ 5m | 预设B | 135（俯45°） | 640cm | 25° |
| > 5m 或矩阵布局 | 预设C | 180（俯90°） | — | 30° |
| 设计师明确要平视 | 预设D | 90（平视） | 300cm | 35° |

**Pitch 锁死，不可修正。**

---

### Step C：精算 distance 和 FOV（预设A/B/D适用，预设C固定height=800不走此步）

```python
import math

base_distance = preset.base_distance  # 单位：厘米
base_fov = preset.base_fov

# 0. spread 从米转厘米（base_distance 单位为 cm，必须统一）
spread_cm = spread * 100

# 1. 固定 FOV，算需要的 distance（让 spread 占画面约 70%）
required_distance = (spread_cm / 0.7) / (2 * math.tan(math.radians(base_fov / 2)))

# 2. 限幅在基准值 ±30% 内（保持预设视觉风格）
distance = max(base_distance * 0.7, min(base_distance * 1.3, required_distance))

# 3. 若被限幅，用 FOV 补偿（最多 ±5°）
if abs(distance - required_distance) > 1:
    fov = math.degrees(2 * math.atan((spread_cm / 0.7) / (2 * distance)))
    fov = max(base_fov - 5, min(base_fov + 5, fov))
else:
    fov = base_fov

# 4. 俯45°时 height = distance（保持俯仰角）
if preset.pitch == 135:
    height = distance
elif preset.pitch == 90:   # 平视
    height = 50            # 见 presets.md NPC 胸部高度规范
else:
    height = distance      # 其他俯仰角近似处理

# 5. offsetY 固定为 0（左右居中）
offset_y = 0
```

---

### Step D：输出参数表

```
【摄像机反推结果】
control 位置  : ({cx:.2f}, 0.27, {cz:.2f})
档位          : 预设X（Pitch={pitch}°）
CameraFollow  : distance={distance:.0f}  offsetY=0  height={height:.0f}
FOV           : {fov:.0f}°（基准{base_fov}° {'无修正' if fov==base_fov else f'修正{fov-base_fov:+.0f}°'}）
spread        : Z={spread_z:.1f}m  X={spread_x:.1f}m  → 约束值={spread:.1f}m
```

此参数直接用于步骤4 BlockScript 的 `CameraFollow` 积木，不再手动选预设。

---

### 特殊情况

| 情况 | 处理 |
|---|---|
| OJ单角色无物件 | spread=0，直接用预设A最小值（distance=200, height=200, FOV=25） |
| spread > 8m，预设C也不够 | 报告"场景跨度过大，建议缩减横向布局至8m内"，等主agent指示 |
| 设计师已在确认单中指定视角参数 | 跳过反推，直接用确认单参数，在交付报告注明"视角参数来自确认单" |

---

## 相关文档

- `navmesh.md` —— 第1层合法性验证工具链
- `presets.md` —— 摄像机预设基准值（档位基准 distance/FOV/height 来源）
- `design_rules.md §R-15/R-16` —— 站位规则在设计层的约束条目
- `creator_skill.md §四 步骤2.5/3.7` —— 本文件的调用入口
