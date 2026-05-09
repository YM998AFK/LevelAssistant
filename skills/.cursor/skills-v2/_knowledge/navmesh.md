# NavMesh 位置验证（非默认场景必做）

> **触发条件**：使用任何**非默认教室 28746** 的场景时必须执行本节验证。
> 默认室内 28746 按 `_knowledge/presets.md §一 摄像机预设·摆放黄金法则` 放角色即可，最终跑一次 validate 兜底。

**v0.0.4 起：优先用 MCP 原生接口**，旧脚本退为批量布点专用。完整旧工具文档见 `scripts/navmesh/README.md`。

---

## 为什么要验证

非标准场景（大地图 / 室外 / 楼梯 / 多层）若不验证，会出现：

- **穿模**：角色脚下不是地面，一半埋土里
- **UNREACHABLE**：两个 NPC 分别站在断开的岛上，`RunToTargetAndWait` 跑不到
- **OUT_OF_BOUNDS**：坐标超出场景可行走面

---

---

## MCP v0.0.4+ 优先用法

### 1. 设置场景元素位置并自动贴地（替代 `scene_utils.set_character_position` + 手动 snap）

```python
# navmesh snap + strict 模式：落点不合法直接报错，无需事后 validate_positions
data = update_scene_element_position(data,
    element_name="主角",
    position=[x, y, z],
    navmesh={"enabled": True, "max_sample_distance": 2, "strict": True})
```

### 2. 验证跨角色可达性（替代 `navmesh_validate.validate_positions` 的 `require_reachable_pairs`）

```python
import sys
sys.path.insert(0, "skills/mcp/hetu_mcp")
from navigation.scene_navmesh import get_scene_connected_component

cc_a = get_scene_connected_component(scene_id, [xa, ya, za])
cc_b = get_scene_connected_component(scene_id, [xb, yb, zb])
assert cc_a.component == cc_b.component, "两点不在同一连通岛，RunToTarget 无法到达"
```

### 3. WalkToTarget / RunToTarget 目标落点（自动，无需手动）

`validate_workspace` 在存在 Scene AssetId 时会**自动检测**寻路积木目标坐标的 NavMesh 合法性。无需额外调用脚本。`GotoPosition3D` 等直接坐标移动积木不参与检测。

### 4. 单点 snap / 最近边界距离

```python
from navigation.scene_navmesh import sample_scene_position, find_scene_closest_edge

hit  = sample_scene_position(scene_id, [x, y, z], max_distance=2).to_dict()
edge = find_scene_closest_edge(scene_id, [x, y, z]).to_dict()
# edge["distance"] < 1.0 时换点，避免贴墙
```

### 5. 路径计算 / 直线检测（新增）

```python
from navigation.scene_navmesh import calculate_scene_path, raycast_scene

path = calculate_scene_path(scene_id, [sx,sy,sz], [tx,ty,tz]).to_dict()
# path["status"] == "complete" 表示完整路径可达
ray  = raycast_scene(scene_id, [sx,sy,sz], [tx,ty,tz]).to_dict()
# ray["blocked"] == False 表示直线无阻挡
```

---

## 仍需旧脚本的场景（批量布点）

| 需求 | 函数 | 说明 |
|---|---|---|
| 沿外轮廓均匀放 N 个巡逻点 | `V.place_npcs_on_boundary(scene_id, count, min_spacing)` | MCP 无等价接口 |
| 内部随机撒物件，离边界 ≥ margin | `V.place_points_inside(scene_id, count, min_dist, margin)` | MCP 无等价接口 |
| 主角推荐出生点（最大岛质心） | `V.centroid_of_largest_island(scene_id)` | MCP 无等价接口 |
| 场景全量摘要（岛数 / 面积 / bounds） | `V.scene_summary(scene_id)` | 可参考 `scene.json` 字段，但无一步调用 |

```python
import sys
sys.path.insert(0, "scripts/navmesh")
import navmesh_validate as V

# 仍然有效，保留用于上述批量场景
waypoints = V.place_npcs_on_boundary(scene_id, count=4, min_spacing=8.0)
items     = V.place_points_inside(scene_id, count=5, min_dist=3.0, margin=1.0)
centroid  = V.centroid_of_largest_island(scene_id)
```

---

## 工具链一览（`scripts/navmesh/`）

| 层次 | 文件 | 作用 |
|---|---|---|
| 数据 | `navmesh_cache/<asset_id>.json` | 每个场景的 NavMesh 几何（160 个场景已导出） |
| 数据 | `navmesh_cache/_scene_summary_index.json` | 所有场景摘要的总索引（5MB，一次 load 可查全部） |
| 库 | `navmesh_loader.py` | 加载 + 去重 + 连通性预处理 |
| 库 | `navmesh_query.py` | 底层查询：`snap_to_navmesh` / `is_reachable` / `components` / `sample_boundary` / `sample_inside` |
| **库** | **`navmesh_validate.py`** | **agent 直接调的 4 个高阶接口（优先用这层）** |
| CLI | `navmesh_cli.py` | 命令行：`summary / edge / inside / validate / preview` |
| 索引 | `scene_index.json` | 181 个场景的 AssetId → Unity 路径 → 是否有 NavMesh |

---

## 旧脚本高阶接口（仅批量布点时使用）

> **v0.0.4 起**：① 坐标设置和 snap 用 `update_scene_element_position`；② 跨角色可达性用 `get_scene_connected_component`；③ WalkToTarget 目标检测由 `validate_workspace` 自动完成。下列旧接口只在需要**批量均匀布点 / 质心 / 全量摘要**时调用。

```python
import sys
sys.path.insert(0, "scripts/navmesh")
import navmesh_validate as V

# ① 场景摘要（仅批量布点前参考；单点操作已由 MCP 覆盖）
s = V.scene_summary(28746)

# ② 沿外边界均匀放 N 个巡逻 NPC（MCP 无等价接口，仍用此）
npcs = V.place_npcs_on_boundary(28746, count=3, min_spacing=5.0)
for p in npcs:
    x, y, z = p.position
    data = update_scene_element_position(data, element_name=p.name, position=[x, y, z])

# ③ 主角/相机目标推荐：最大连通岛的重心（MCP 无等价接口，仍用此）
centroid = V.centroid_of_largest_island(28746)

# ④ 一次性验证多个已有坐标（备用；单点 snap 已在 step3 完成，WalkToTarget 已在 validate_workspace 覆盖）
rep = V.validate_positions(
    asset_id=28746,
    positions=[("hero", (0.0, 0.27, 0.0)), ("robot", (2.0, 0.27, -1.0))],
    require_reachable_pairs=[("hero", "robot")],  # 跨角色可达性（可改用 get_scene_connected_component）
    min_spacing=1.0,
    snap=True, max_snap_dist=3.0,
)
assert rep.ok, rep.issues
```

---

## ValidationReport 的 4 种 issue code

| code | 含义 | 常见原因 | 怎么救 |
|---|---|---|---|
| `OFF_NAVMESH` | 坐标不在可行走面 + snap 距离超限 | Y 写错 / 地面高度差 | 改用 `snap_to_navmesh` 返回的坐标 |
| `UNREACHABLE` | 两点不在同一连通岛 | 场景被楼梯/平台切成多块 | 把点挪到同一个 island_id，或换场景 |
| `TOO_CLOSE` | XZ 距离 < min_spacing | 角色挤在一起 | 拉开距离（对应 N6） |
| `OUT_OF_BOUNDS` | 超出场景 bounds | 坐标写成厘米 / 场景搞错 | 检查单位 |

---

## 什么时候必须调

| 场景条件 | 必做 | 推荐 |
|---|---|---|
| 默认教室 28746（16×12 m 标准） | ❌ 按黄金法则 | ✅ 最终跑一次 validate 兜底 |
| 其他室内场景（非 28746） | ✅ | - |
| 室外 / 大地图 / 地形 | ✅✅ | - |
| 多层 / 楼梯 / 多平台 | ✅✅（重点看 `island_count`） | - |
| `_scene_summary_index.json` 里 `island_count > 20` | ✅✅ 检查每个角色的 `island_id`，确认可达 | - |

---

## 坐标系对齐

- NavMesh 输出坐标和本 skill JSON `Position` **数值 1:1 直接对应**（同为 ws 单位，可直接互用）
- `agent.height` 不是角色身高（默认 2m），是 NavMesh 构建时的"最小净空高度"；人形 0.6 Scale 的乌拉呼也能走
- `agent.radius=0.5` 意味着 NavMesh 边缘已内缩了 0.5m，所以 `place_npcs_on_boundary` 返回的点**不会贴墙**

---

## 路径 waypoint 安全边距（2026-04-28 实测；v0.0.4 已有 MCP 接口）

把跑操 / 巡逻路标（P1-P4 等）放在 navmesh **边界采样点**上会出现贴墙 / 穿模。

**v0.0.4+ 推荐做法（MCP）：**

```python
from navigation.scene_navmesh import find_scene_closest_edge, sample_scene_position

# 采样最近合法点并贴地
hit  = sample_scene_position(scene_id, [x, y, z], max_distance=2).to_dict()
# 检查到边界距离，< 1.0 时换点
edge = find_scene_closest_edge(scene_id, hit["position"]).to_dict()
assert edge["distance"] >= 1.0, f"点距边界仅 {edge['distance']:.2f}m，贴墙风险"
```

或直接用 `update_scene_element_position` + navmesh snap，点会自动落在 NavMesh 上（但不保证 ≥ 1m 边距，需额外用 `find_scene_closest_edge` 验证）。

坑记录：`pitfalls.md §11.2`。
