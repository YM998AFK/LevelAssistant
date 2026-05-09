# NavMesh 位置验证（非默认场景必做）

> **触发条件**：使用任何**非默认教室 28746** 的场景时必须执行本节验证。
> 默认室内 28746 按 `SKILL.md § 坐标系统 > 黄金法则` 放角色即可，最终跑一次 validate 兜底。

完整工具文档见 `scripts/navmesh/README.md`。

---

## 为什么要验证

非标准场景（大地图 / 室外 / 楼梯 / 多层）若不验证，会出现：

- **穿模**：角色脚下不是地面，一半埋土里
- **UNREACHABLE**：两个 NPC 分别站在断开的岛上，`RunToTargetAndWait` 跑不到
- **OUT_OF_BOUNDS**：坐标超出场景可行走面

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

## 4 个高阶接口（Python 里直接 import）

```python
import sys
sys.path.insert(0, "scripts/navmesh")
import navmesh_validate as V

# ① 先看一眼场景长啥样（agent 决策前必看）
s = V.scene_summary(28746)  # AssetId
# 关键字段：bounds_min/max, island_count, islands[{id,xz_area,bbox}], largest_island_centroid, agent(radius/height)

# ② 放多个角色后，一次性验证所有位置
rep = V.validate_positions(
    asset_id=28746,
    positions=[
        ("hero",   (0.0, 0.27, 0.0)),
        ("robot",  (2.0, 0.27, -1.0)),
        ("apple",  (-3.0, 0.27, 2.0)),
    ],
    require_reachable_pairs=[("hero", "robot"), ("hero", "apple")],
    min_spacing=1.0,   # 对应 N6
    snap=True,         # 小偏差自动吸附到 NavMesh
    max_snap_dist=3.0,
)
print(rep.pretty())     # 人看的
data = rep.to_dict()    # 机器读的（给生成器/审查员）
assert rep.ok, rep.issues  # 不 ok 就别生成

# ③ 沿外边界均匀放 N 个巡逻 NPC
npcs = V.place_npcs_on_boundary(28746, count=3, min_spacing=5.0)
for p in npcs:
    x, y, z = p.position
    # 写入 Character Position = [str(x), str(y), str(z)]

# ④ 主角/相机目标推荐：最大连通岛的重心
centroid = V.centroid_of_largest_island(28746)
# => (x, y, z) 可直接拿去当主角出生点
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

## 路径 waypoint 安全边距（2026-04-28 实测）

把跑操 / 巡逻路标（P1-P4 等）放在 navmesh **边界采样点**上会出现贴墙 / 穿模，
原因：`sample_boundary()` 返回的是可行走面的最外缘，正好对应真实场景里的墙根 / 家具背面。

**waypoint 必须同时满足两条：**

| 条件 | 函数 | 说明 |
|---|---|---|
| 可行走 | `is_walkable(x, z)` | 点落在可行走三角面内 |
| 安全距离 | `dist_to_boundary(x, z) >= 1.0` | 距 navmesh 边界 ≥ 1.0 ws 单位 |

对**正方形路径**，推荐网格搜索找内切正方形后**取最大边长的 80%**（留 20% 容错），四顶点均满足上述两条件。  
参考脚本：`scripts/_find_v6_square.py`；坑记录：`pitfalls.md §11.2`；  
SKILL.md"NavMesh 位置验证"节有摘要。
