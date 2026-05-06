# -*- coding: utf-8 -*-
"""
NavMesh JSON 加载器 + 预处理。

把 Unity 导出的 navmesh_cache/<asset_id>.json 读进来,做三件事:
  1. 解析顶点 / 三角形 / area / agent / bounds
  2. 按空间坐标去重(Unity CalculateTriangulation 会为每个 tile 独立存顶点,
     一个物理点可能有多个索引,不去重没法建连通图)
  3. 构建三角形邻接表 + 外边界环路 (boundary loops)

使用:
    from navmesh_loader import load_navmesh
    nm = load_navmesh(12836)            # 按 asset_id 查 cache
    nm = load_navmesh("path/to/12836.json")  # 直接给文件路径
    print(nm.summary())
"""
from __future__ import annotations
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = REPO_ROOT / "scripts" / "navmesh" / "navmesh_cache"

Vec3 = Tuple[float, float, float]
Vec2 = Tuple[float, float]

# 空间去重精度:小于 1mm 视为同一个点 (Unity 默认 NavMesh 精度足够)
SPATIAL_EPS = 1e-3


@dataclass
class NavMesh:
    """预处理后的 NavMesh 数据。"""
    # 元数据
    asset_id: int
    name: str
    unity_file: str
    unity_version: str
    exported_at: str

    # agent 参数
    agent_radius: float
    agent_height: float
    agent_step: float
    agent_slope: float

    # 轴对齐包围盒
    bounds_min: Vec3
    bounds_max: Vec3

    # 原始(可能含重复点)顶点 —— 只作引用,查询用的是 cverts
    raw_verts: List[Vec3]
    # 三角形(原始索引,注意使用前通常要映射到 cverts)
    raw_tris: List[Tuple[int, int, int]]
    # 每个三角形的 area id
    areas: List[int]

    # === 预处理产出 ===
    # 去重后的顶点 (canonical)
    cverts: List[Vec3] = field(default_factory=list)
    # raw_index -> canonical_index
    raw2c: List[int] = field(default_factory=list)
    # 三角形(使用 canonical 索引)
    tris: List[Tuple[int, int, int]] = field(default_factory=list)
    # 三角形邻接: tri_adj[i] = {j,k,l} 最多 3 个
    tri_adj: List[List[int]] = field(default_factory=list)
    # 外边界环路: 每个环是一串 canonical vertex 索引, 首尾相连
    # 多个环的情况: 第 0 个通常是外轮廓,其余是洞
    boundary_loops: List[List[int]] = field(default_factory=list)
    # 每个三角形的 2D 面积 (XZ 平面) —— 采样时按面积加权
    tri_xz_areas: List[float] = field(default_factory=list)
    # 总可行走 XZ 面积
    total_walkable_xz_area: float = 0.0

    # -- 便捷属性 --
    @property
    def path_source(self) -> str:
        return f"{self.asset_id} {self.name}"

    def summary(self) -> str:
        bmin, bmax = self.bounds_min, self.bounds_max
        size = (bmax[0] - bmin[0], bmax[1] - bmin[1], bmax[2] - bmin[2])
        return (
            f"NavMesh #{self.asset_id} {self.name}\n"
            f"  verts (raw/canonical): {len(self.raw_verts)} / {len(self.cverts)}\n"
            f"  tris: {len(self.tris)}  areas_set: {sorted(set(self.areas))}\n"
            f"  bounds size XYZ: [{size[0]:.2f}, {size[1]:.2f}, {size[2]:.2f}] m\n"
            f"  walkable XZ area: {self.total_walkable_xz_area:.2f} m^2\n"
            f"  boundary loops: {len(self.boundary_loops)}  "
            f"(total edges: {sum(len(l) for l in self.boundary_loops)})\n"
            f"  agent: r={self.agent_radius} h={self.agent_height} "
            f"step={self.agent_step} slope={self.agent_slope}"
        )


# ---------- loader ----------

def _resolve_path(src) -> Path:
    if isinstance(src, Path):
        return src
    if isinstance(src, int) or (isinstance(src, str) and src.isdigit()):
        p = CACHE_DIR / f"{int(src)}.json"
        if not p.exists():
            raise FileNotFoundError(f"缓存里没有 {src} 对应的 navmesh json: {p}")
        return p
    return Path(src)


def load_navmesh(src) -> NavMesh:
    """src 可以是 asset_id (int 或数字字符串) 或 json 文件路径。"""
    p = _resolve_path(src)
    data = json.loads(p.read_text(encoding="utf-8"))

    nm = data["navmesh"]
    bounds = data["bounds"]
    agent = data["agent"]

    raw_verts: List[Vec3] = [tuple(v) for v in nm["vertices"]]
    raw_tris: List[Tuple[int, int, int]] = [tuple(t) for t in nm["triangles"]]
    areas: List[int] = list(nm.get("areas", [0] * len(raw_tris)))

    mesh = NavMesh(
        asset_id=int(data["asset_id"]),
        name=data.get("name", ""),
        unity_file=data.get("unity_file", ""),
        unity_version=data.get("unity_version", ""),
        exported_at=data.get("exported_at", ""),
        agent_radius=float(agent.get("radius", 0.5)),
        agent_height=float(agent.get("height", 2.0)),
        agent_step=float(agent.get("step_height", 0.4)),
        agent_slope=float(agent.get("slope", 45.0)),
        bounds_min=tuple(bounds["min"]),
        bounds_max=tuple(bounds["max"]),
        raw_verts=raw_verts,
        raw_tris=raw_tris,
        areas=areas,
    )

    _preprocess(mesh)
    return mesh


# ---------- preprocess ----------

def _preprocess(m: NavMesh) -> None:
    _dedupe_vertices(m)
    _build_adjacency(m)
    _extract_boundary_loops(m)
    _compute_tri_areas(m)


def _dedupe_vertices(m: NavMesh) -> None:
    """按 SPATIAL_EPS 做空间去重,产生 canonical 顶点表和 tri 的 canonical 索引。"""
    eps = SPATIAL_EPS
    key_to_idx: Dict[Tuple[int, int, int], int] = {}
    cverts: List[Vec3] = []
    raw2c: List[int] = [0] * len(m.raw_verts)

    for i, (x, y, z) in enumerate(m.raw_verts):
        key = (round(x / eps), round(y / eps), round(z / eps))
        ci = key_to_idx.get(key)
        if ci is None:
            ci = len(cverts)
            cverts.append((x, y, z))
            key_to_idx[key] = ci
        raw2c[i] = ci

    m.cverts = cverts
    m.raw2c = raw2c
    m.tris = [(raw2c[a], raw2c[b], raw2c[c]) for (a, b, c) in m.raw_tris]


def _tri_edges(a: int, b: int, c: int) -> List[Tuple[int, int]]:
    """返回三角形的 3 条无向边 (small, large)。"""
    return [
        (min(a, b), max(a, b)),
        (min(b, c), max(b, c)),
        (min(a, c), max(a, c)),
    ]


def _build_adjacency(m: NavMesh) -> None:
    """三角形邻接: 共享一条边就是邻居。"""
    edge_owner: Dict[Tuple[int, int], List[int]] = {}
    for ti, (a, b, c) in enumerate(m.tris):
        for e in _tri_edges(a, b, c):
            edge_owner.setdefault(e, []).append(ti)

    adj: List[List[int]] = [[] for _ in m.tris]
    for owners in edge_owner.values():
        if len(owners) == 2:
            t1, t2 = owners
            adj[t1].append(t2)
            adj[t2].append(t1)
        # len >= 3 : non-manifold, 忽略
    m.tri_adj = adj


def _extract_boundary_loops(m: NavMesh) -> None:
    """
    提取外边界: 只被一个三角形拥有的边就是边界边。
    把这些边连成有向环路 (按三角形方向), 每个环是一串顶点 id (首尾不重复记录)。
    """
    edge_count: Dict[Tuple[int, int], int] = {}
    # 有向边(按三角形逆/顺时针方向): 用来后面定方向
    directed: List[Tuple[int, int]] = []
    for (a, b, c) in m.tris:
        for u, v in ((a, b), (b, c), (c, a)):
            key = (min(u, v), max(u, v))
            edge_count[key] = edge_count.get(key, 0) + 1
            directed.append((u, v))

    # 边界: 无向边只出现过一次
    boundary_dir: Dict[int, int] = {}  # from -> to (有向), 每个边界顶点最多出边一条
    for (u, v) in directed:
        key = (min(u, v), max(u, v))
        if edge_count[key] == 1:
            # 只记一次(有向)
            boundary_dir[u] = v

    loops: List[List[int]] = []
    visited: set = set()
    for start in list(boundary_dir.keys()):
        if start in visited:
            continue
        loop = []
        cur = start
        guard = 0
        while cur not in visited and cur in boundary_dir and guard < len(boundary_dir) + 2:
            visited.add(cur)
            loop.append(cur)
            cur = boundary_dir[cur]
            guard += 1
        if len(loop) >= 3:
            loops.append(loop)

    # 外轮廓排在第 0 位: 按 XZ 面积最大的那个
    def _loop_xz_area(loop: List[int]) -> float:
        pts = [m.cverts[i] for i in loop]
        s = 0.0
        for i in range(len(pts)):
            x1, _, z1 = pts[i]
            x2, _, z2 = pts[(i + 1) % len(pts)]
            s += x1 * z2 - x2 * z1
        return abs(s) * 0.5

    loops.sort(key=_loop_xz_area, reverse=True)
    m.boundary_loops = loops


def _compute_tri_areas(m: NavMesh) -> None:
    areas: List[float] = []
    total = 0.0
    for (a, b, c) in m.tris:
        ax, _, az = m.cverts[a]
        bx, _, bz = m.cverts[b]
        cx, _, cz = m.cverts[c]
        s = abs((bx - ax) * (cz - az) - (cx - ax) * (bz - az)) * 0.5
        areas.append(s)
        total += s
    m.tri_xz_areas = areas
    m.total_walkable_xz_area = total


# ---------- 命令行 smoke test ----------

if __name__ == "__main__":
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else 12836
    nm = load_navmesh(src)
    print(nm.summary())
    for i, loop in enumerate(nm.boundary_loops[:3]):
        pts = [nm.cverts[j] for j in loop]
        length = 0.0
        for k in range(len(pts)):
            x1, _, z1 = pts[k]
            x2, _, z2 = pts[(k + 1) % len(pts)]
            length += math.hypot(x2 - x1, z2 - z1)
        print(f"  loop#{i}: verts={len(loop)}  perimeter={length:.2f} m")
