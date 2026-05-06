# NavMesh 工具链

从 Unity 项目导出每个关卡场景的 NavMesh,再做下游查询 / 采样 / 验证 / 预览。
**目标**:给关卡生成/修改 agent 提供"这个场景哪里能走、NPC 该放哪、坐标合不合法"的能力。

---

## 一、整体流程

```
 Unity 工程 (D:\meishu)
        |  NavMeshExporter.cs  (Editor 脚本,每场景一次)
        v
 scripts/navmesh/navmesh_cache/<asset_id>.json   ← 每个场景一份
        |
        |  navmesh_loader.py  (加载 + 去重 + 邻接 + 边界环)
        v
    NavMesh 对象
        |
        +-- navmesh_query.py     (基础查询: snap / contains / is_reachable / sample)
        +-- navmesh_validate.py  (对外主接口: place_npcs / validate_positions / scene_summary)
        +-- navmesh_cli.py       (命令行: summary / edge / inside / validate / preview)
```

---

## 二、一次性准备

1. 安装 Unity 2021.3.11f1(全局版),放在 `C:\Program Files\Unity\Hub\Editor\2021.3.11f1`。
2. 用 Unity Hub 打开 `D:\meishu`,登录账号并激活 **Personal License**(免费)。
3. `D:\meishu\Assets\Editor\NavMeshExporter.cs` 已部署,会自动编译。
4. `scripts/navmesh/scene_index.json` 已通过 `build_scene_index.py` 生成(181 个场景,160 个有 NavMesh)。

## 三、批量导出

```powershell
# 全部场景 (只重导缺失的)
python scripts\navmesh\run_unity_export.py --mode all

# 单场景
python scripts\navmesh\run_unity_export.py --mode single --asset-id 12836

# 全部 + 强制覆盖
python scripts\navmesh\run_unity_export.py --mode all --force
```

完成后:

- `navmesh_cache/<asset_id>.json` —— 每个场景的 NavMesh 几何
- `navmesh_cache/_summary.json` —— 导出汇总(成功/失败计数)
- `unity_editor_scripts/unity_batch.log` —— Unity 日志

---

## 四、Python API 用法

### 4.1 加载 (`navmesh_loader.py`)

```python
from navmesh_loader import load_navmesh

m = load_navmesh(12836)        # 按 asset_id 查 cache
m = load_navmesh("path.json")  # 直接给路径
print(m.summary())
```

`NavMesh` 对象关键字段:

- `bounds_min / bounds_max`:轴对齐包围盒(Unity 世界坐标,单位米)
- `cverts`:去重后的顶点 `[(x,y,z), ...]`
- `tris`:三角形,每个是 3 个 `cverts` 索引
- `tri_adj`:三角形邻接表(用于连通性)
- `boundary_loops`:外边界环路(第 0 个是面积最大的外轮廓)
- `total_walkable_xz_area`:可行走总面积(m²)
- `agent_radius / agent_height / agent_step / agent_slope`

### 4.2 查询 (`navmesh_query.py`)

```python
import navmesh_query as Q

Q.contains(m, x, y, z)                 # 点是否在可行走面上
Q.snap_to_navmesh(m, x, y, z)          # 吸附到最近 navmesh 点,返回 (x,y,z) 或 None
Q.is_reachable(m, p1, p2)              # p1、p2 是否可互达
Q.components(m)                        # 所有连通岛,按面积降序
Q.sample_boundary(m, n, spacing=None)  # 沿外边界采 n 个点 / 或固定 spacing
Q.sample_inside(m, n, min_dist=2.0)    # 内部随机采 n 点,两两距离 >= min_dist
Q.all_boundary_samples(m, spacing=5.0) # 所有岛的边界各采一圈
```

### 4.3 高阶接口 (`navmesh_validate.py`)

给关卡生成 / 修改 agent 直接调的 4 个函数:

```python
import navmesh_validate as V

# 场景摘要(bounds, 岛数, 每岛面积, agent, 最大岛中心点)
s = V.scene_summary(12836)

# 沿外轮廓放 3 个 NPC,间距 >= 12m
npcs = V.place_npcs_on_boundary(12836, count=3, min_spacing=12)

# 最大岛内撒 5 个物件,互相距离 >= 5m,离边界 >= 1.5m
items = V.place_points_inside(12836, count=5, min_dist=5, margin=1.5, island_index=0)

# 验证一组已有坐标是否合法
rep = V.validate_positions(
    12836,
    [("hero", (0, 0, -76)), ("robot", (5, 0, -70)), ("apple", (1, 0, -150))],
    require_reachable_pairs=[("hero", "robot"), ("hero", "apple")],
    min_spacing=3.0,
)
print(rep.ok, rep.pretty())

# 主角推荐出生点 / 相机 target
centroid = V.centroid_of_largest_island(12836)
```

`ValidationReport` 里 `issues` 的 `code` 取值:

| code           | 含义                                           |
| -------------- | ---------------------------------------------- |
| `OFF_NAVMESH`  | 点不在可行走面上且 snap 距离超限                   |
| `UNREACHABLE`  | 两个点不在同一连通岛,NPC 跑不到                   |
| `TOO_CLOSE`    | 两点 XZ 距离 < `min_spacing`                   |
| `OUT_OF_BOUNDS`| 点不在场景 bounds 内                             |

### 4.4 命令行 (`navmesh_cli.py`)

```powershell
python scripts\navmesh\navmesh_cli.py summary 12836              # 详细
python scripts\navmesh\navmesh_cli.py summary --all              # 总览所有已导出场景
python scripts\navmesh\navmesh_cli.py edge 12836 --count 3 --min-spacing 12
python scripts\navmesh\navmesh_cli.py inside 12836 --count 5 --min-dist 5 --margin 1.5
python scripts\navmesh\navmesh_cli.py validate 12836 --positions "hero,0,0,-76;apple,1,0,-150" --reachable "hero,apple"
python scripts\navmesh\navmesh_cli.py preview 12836 --width 80   # ASCII 俯视图
python scripts\navmesh\navmesh_cli.py export-index               # 产出 _scene_summary_index.json
```

---

## 五、坐标系约定

- Unity 左手系,**Y 向上**,XZ 为地面
- 所有接口传入/返回的坐标都是 Unity **世界坐标**
- NavMesh 三角形所有 y 值都是"脚下地面"的 Y,NPC 站在上面时应保持/贴合

## 六、踩坑记

| 坑                                                      | 解                                                |
| ------------------------------------------------------- | ------------------------------------------------- |
| Unity 2021.3.11f1c2 (国内版) 打不开 → 只能用全球版        | 全球版+把 `Launch.cs:32` 用 `#if !UNITY_EDITOR` 包住 |
| Batch 模式 "license is unavailable"                     | Unity Hub → Licenses → Add Personal License       |
| `CalculateTriangulation()` 顶点按 tile 独立,一个物理点有多个索引 | `navmesh_loader._dedupe_vertices` 做了空间去重      |
| 同一场景可能有多个不相连的可行走岛(楼梯/平台分离)         | `components()` + `validate` 会报 `UNREACHABLE`     |
