# -*- coding: utf-8 -*-
"""
NavMesh 核心查询工具。

给定一个 NavMesh 对象(由 navmesh_loader.load_navmesh 拿到),提供:

  contains(x, y, z)           -> bool          点是否在可行走区域内(XZ 投影)
  snap_to_navmesh(x,y,z, max_dist=?) -> (x,y,z) | None
                                               把任意一个粗坐标 "吸附" 到最近 navmesh 表面
  is_reachable(p1, p2)        -> bool          两个点是否互达(连通分量判断)
  components()                -> List[List[int]]  所有连通分量(三角形 id 列表)
  sample_boundary(n, spacing=None, loop_index=0)
                              -> List[Vec3]    沿外边界环均匀采样 n 个点
  sample_inside(n, min_dist=None, seed=0)
                              -> List[Vec3]    在可行走面内按面积加权均匀采样 n 个点
                                               保证点两两距离 >= min_dist(默认=agent_radius*4)
  all_boundary_samples(spacing) -> List[Vec3]  沿所有外边界每 spacing 米采一个点

所有坐标都是 Unity 世界坐标 (x, y, z),XZ 平面是地面,Y 是上。
"""
from __future__ import annotations
import math
import random
from typing import List, Optional, Tuple, Dict, Set

from navmesh_loader import NavMesh, Vec3


# ---------- 基本几何 ----------

def _tri_xz(m: NavMesh, ti: int):
    a, b, c = m.tris[ti]
    return m.cverts[a], m.cverts[b], m.cverts[c]


def _point_in_tri_xz(px: float, pz: float, ax: float, az: float,
                     bx: float, bz: float, cx: float, cz: float) -> bool:
    """点是否在三角形内(XZ),含边。"""
    d1 = (px - bx) * (az - bz) - (ax - bx) * (pz - bz)
    d2 = (px - cx) * (bz - cz) - (bx - cx) * (pz - cz)
    d3 = (px - ax) * (cz - az) - (cx - ax) * (pz - az)
    has_neg = (d1 < -1e-9) or (d2 < -1e-9) or (d3 < -1e-9)
    has_pos = (d1 > 1e-9) or (d2 > 1e-9) or (d3 > 1e-9)
    return not (has_neg and has_pos)


def _tri_bary_y(m: NavMesh, ti: int, px: float, pz: float) -> float:
    """已知点在三角形内,返回其 Y (按重心插值)。"""
    a, b, c = m.tris[ti]
    ax, ay, az = m.cverts[a]
    bx, by, bz = m.cverts[b]
    cx, cy, cz = m.cverts[c]
    denom = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz)
    if abs(denom) < 1e-12:
        return (ay + by + cy) / 3.0
    w1 = ((bz - cz) * (px - cx) + (cx - bx) * (pz - cz)) / denom
    w2 = ((cz - az) * (px - cx) + (ax - cx) * (pz - cz)) / denom
    w3 = 1.0 - w1 - w2
    return w1 * ay + w2 * by + w3 * cy


def _dist_pt_to_seg_xz(px, pz, ax, az, bx, bz) -> Tuple[float, float, float]:
    """返回 (距离, 最近点x, 最近点z)"""
    abx = bx - ax
    abz = bz - az
    ab2 = abx * abx + abz * abz
    if ab2 < 1e-12:
        dx = px - ax
        dz = pz - az
        return math.hypot(dx, dz), ax, az
    t = ((px - ax) * abx + (pz - az) * abz) / ab2
    t = max(0.0, min(1.0, t))
    cx = ax + t * abx
    cz = az + t * abz
    return math.hypot(px - cx, pz - cz), cx, cz


# ---------- 连通分量 ----------

class _CC:
    """三角形连通分量缓存,挂在 NavMesh 对象自己的 __dict__ 里,
    避免跨实例的 id(m) 复用导致的脏缓存 (Python 会回收并复用对象地址)。"""

    @classmethod
    def tri_component(cls, m: NavMesh) -> List[int]:
        cached = getattr(m, "_cc_tri_component", None)
        if cached is not None:
            return cached
        n = len(m.tris)
        comp = [-1] * n
        cid = 0
        for i in range(n):
            if comp[i] != -1:
                continue
            stack = [i]
            comp[i] = cid
            while stack:
                t = stack.pop()
                for nb in m.tri_adj[t]:
                    if comp[nb] == -1:
                        comp[nb] = cid
                        stack.append(nb)
            cid += 1
        # 直接挂在实例上,实例被回收时缓存一起消失
        object.__setattr__(m, "_cc_tri_component", comp)
        return comp


def components(m: NavMesh) -> List[List[int]]:
    """返回每个连通分量的三角形 id 列表,按面积从大到小排序。"""
    comp = _CC.tri_component(m)
    groups: Dict[int, List[int]] = {}
    for ti, c in enumerate(comp):
        groups.setdefault(c, []).append(ti)
    lst = list(groups.values())
    lst.sort(key=lambda g: sum(m.tri_xz_areas[t] for t in g), reverse=True)
    return lst


# ---------- 点查询 ----------

def locate_tri(m: NavMesh, x: float, z: float) -> int:
    """XZ 平面上找包含 (x,z) 的三角形,返回 -1 表示不在 navmesh 内。"""
    for ti in range(len(m.tris)):
        (ax, _, az), (bx, _, bz), (cx, _, cz) = _tri_xz(m, ti)
        if _point_in_tri_xz(x, z, ax, az, bx, bz, cx, cz):
            return ti
    return -1


def contains(m: NavMesh, x: float, y: float, z: float,
             y_tolerance: float = 2.0) -> bool:
    """点是否落在可行走面上(XZ 在 navmesh 里,且 Y 与 navmesh 表面相差 <= y_tolerance)。"""
    ti = locate_tri(m, x, z)
    if ti < 0:
        return False
    ny = _tri_bary_y(m, ti, x, z)
    return abs(y - ny) <= y_tolerance


def snap_to_navmesh(m: NavMesh, x: float, y: float, z: float,
                    max_dist: Optional[float] = None) -> Optional[Vec3]:
    """
    把任意点吸附到 navmesh 上最近的可行走点 (XZ 平面距离最近)。
    max_dist: XZ 平面最大容忍距离 (米),超出返回 None。默认=agent_radius*20。
    """
    ti = locate_tri(m, x, z)
    if ti >= 0:
        return (x, _tri_bary_y(m, ti, x, z), z)

    if max_dist is None:
        max_dist = m.agent_radius * 20.0

    best_d = float("inf")
    best = None
    best_ti = -1
    for ti in range(len(m.tris)):
        verts = _tri_xz(m, ti)
        for i in range(3):
            ax, _, az = verts[i]
            bx, _, bz = verts[(i + 1) % 3]
            d, cx, cz = _dist_pt_to_seg_xz(x, z, ax, az, bx, bz)
            if d < best_d:
                best_d = d
                best = (cx, cz)
                best_ti = ti
                if d < 1e-6:
                    break
    if best is None or best_d > max_dist:
        return None
    cx, cz = best
    return (cx, _tri_bary_y(m, best_ti, cx, cz), cz)


def is_reachable(m: NavMesh, p1: Vec3, p2: Vec3,
                 max_snap_dist: Optional[float] = None) -> bool:
    """两个世界坐标是否可互相抵达 (同一连通分量)。
    会先 snap 到 navmesh (XZ 平面)。"""
    s1 = snap_to_navmesh(m, p1[0], p1[1], p1[2], max_snap_dist)
    s2 = snap_to_navmesh(m, p2[0], p2[1], p2[2], max_snap_dist)
    if s1 is None or s2 is None:
        return False
    t1 = locate_tri(m, s1[0], s1[2])
    t2 = locate_tri(m, s2[0], s2[2])
    if t1 < 0 or t2 < 0:
        return False
    comp = _CC.tri_component(m)
    return comp[t1] == comp[t2]


# ---------- 采样 ----------

def _loop_points(m: NavMesh, loop_idx: int) -> List[Vec3]:
    if not m.boundary_loops:
        return []
    loop = m.boundary_loops[loop_idx]
    return [m.cverts[i] for i in loop]


def _loop_perimeter(pts: List[Vec3]) -> float:
    s = 0.0
    for i in range(len(pts)):
        x1, _, z1 = pts[i]
        x2, _, z2 = pts[(i + 1) % len(pts)]
        s += math.hypot(x2 - x1, z2 - z1)
    return s


def sample_boundary(m: NavMesh, n: int,
                    spacing: Optional[float] = None,
                    loop_index: int = 0,
                    start_offset: float = 0.0) -> List[Vec3]:
    """
    沿一个边界环 (默认外轮廓) 均匀采样 n 个点。
    spacing 非空时按固定间距采(会覆盖 n);None 则按 n 均分周长。
    start_offset: 从环起点偏移多少米再开始采(控制起始位置)。
    """
    pts = _loop_points(m, loop_index)
    if len(pts) < 3:
        return []
    perimeter = _loop_perimeter(pts)
    if perimeter < 1e-6:
        return []

    if spacing is not None and spacing > 0:
        count = max(1, int(perimeter // spacing))
        step = perimeter / count
    else:
        count = max(1, n)
        step = perimeter / count

    # 把环按弧长参数化
    seg_lens = []
    for i in range(len(pts)):
        x1, _, z1 = pts[i]
        x2, _, z2 = pts[(i + 1) % len(pts)]
        seg_lens.append(math.hypot(x2 - x1, z2 - z1))
    cum = [0.0]
    for L in seg_lens:
        cum.append(cum[-1] + L)

    def point_at(s: float) -> Vec3:
        s = s % perimeter
        # 二分查找
        lo, hi = 0, len(cum) - 1
        while lo < hi - 1:
            mid = (lo + hi) // 2
            if cum[mid] <= s:
                lo = mid
            else:
                hi = mid
        seg_i = lo
        t = 0.0 if seg_lens[seg_i] < 1e-9 else (s - cum[seg_i]) / seg_lens[seg_i]
        x1, y1, z1 = pts[seg_i]
        x2, y2, z2 = pts[(seg_i + 1) % len(pts)]
        return (x1 + (x2 - x1) * t,
                y1 + (y2 - y1) * t,
                z1 + (z2 - z1) * t)

    return [point_at(start_offset + i * step) for i in range(count)]


def all_boundary_samples(m: NavMesh, spacing: float) -> List[Vec3]:
    """沿所有外边界(每个不相连的岛)按 spacing 米采点,合并返回。"""
    result: List[Vec3] = []
    for li in range(len(m.boundary_loops)):
        result.extend(sample_boundary(m, 0, spacing=spacing, loop_index=li))
    return result


def sample_inside(m: NavMesh, n: int,
                  min_dist: Optional[float] = None,
                  seed: int = 0,
                  max_retry_factor: int = 30) -> List[Vec3]:
    """
    在可行走区域内按三角形面积加权随机采 n 个点,
    保证任意两点 XZ 距离 >= min_dist (默认 = agent_radius * 4 = 2m)。
    达不到 n 个时返回尽可能多的。
    """
    if not m.tris:
        return []
    if min_dist is None:
        min_dist = m.agent_radius * 4.0

    rng = random.Random(seed)
    total = m.total_walkable_xz_area
    if total <= 0:
        return []
    # 累积面积用于加权抽样
    cum = []
    s = 0.0
    for a in m.tri_xz_areas:
        s += a
        cum.append(s)

    def rand_tri() -> int:
        r = rng.random() * total
        lo, hi = 0, len(cum) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if cum[mid] < r:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def rand_point_in_tri(ti: int) -> Vec3:
        a, b, c = m.tris[ti]
        ax, ay, az = m.cverts[a]
        bx, by, bz = m.cverts[b]
        cx, cy, cz = m.cverts[c]
        u, v = rng.random(), rng.random()
        if u + v > 1.0:
            u, v = 1.0 - u, 1.0 - v
        w = 1.0 - u - v
        return (u * ax + v * bx + w * cx,
                u * ay + v * by + w * cy,
                u * az + v * bz + w * cz)

    out: List[Vec3] = []
    md2 = min_dist * min_dist
    max_try = max(100, n * max_retry_factor)
    tries = 0
    while len(out) < n and tries < max_try:
        tries += 1
        p = rand_point_in_tri(rand_tri())
        ok = True
        for q in out:
            dx = p[0] - q[0]
            dz = p[2] - q[2]
            if dx * dx + dz * dz < md2:
                ok = False
                break
        if ok:
            out.append(p)
    return out


# ---------- 命令行 smoke test ----------

if __name__ == "__main__":
    import sys
    from navmesh_loader import load_navmesh

    src = sys.argv[1] if len(sys.argv) > 1 else 12836
    m = load_navmesh(src)
    print(m.summary())
    print()

    # 连通分量
    cc = components(m)
    print(f"[components] 共 {len(cc)} 个连通分量")
    for i, g in enumerate(cc[:5]):
        area = sum(m.tri_xz_areas[t] for t in g)
        print(f"  #{i}: {len(g)} tris, {area:.2f} m^2")

    # bounds 中心点做 contains / snap 测试
    cx = (m.bounds_min[0] + m.bounds_max[0]) / 2
    cy = (m.bounds_min[1] + m.bounds_max[1]) / 2
    cz = (m.bounds_min[2] + m.bounds_max[2]) / 2
    print(f"\n[contains] bounds center ({cx:.2f},{cy:.2f},{cz:.2f}) => {contains(m, cx, cy, cz)}")
    sp = snap_to_navmesh(m, cx, cy, cz)
    print(f"[snap]     bounds center snap => {sp}")

    # 外边界采 8 个点
    bs = sample_boundary(m, 8, loop_index=0)
    print(f"\n[boundary] 外轮廓采 8 个点:")
    for i, p in enumerate(bs):
        print(f"  #{i}: ({p[0]:.2f}, {p[1]:.2f}, {p[2]:.2f})")

    # 内部采 5 个点,min_dist=3
    insp = sample_inside(m, 5, min_dist=3.0, seed=1)
    print(f"\n[inside] 内部采 5 个点 min_dist=3:")
    for i, p in enumerate(insp):
        print(f"  #{i}: ({p[0]:.2f}, {p[1]:.2f}, {p[2]:.2f})")

    # 可达性测试
    if len(bs) >= 2:
        r = is_reachable(m, bs[0], bs[len(bs) // 2])
        print(f"\n[reachable] boundary[0] <-> boundary[mid] => {r}")
