# -*- coding: utf-8 -*-
"""
NavMesh 高阶接口 —— 提供给关卡生成 / 修改 agent 调用。

核心场景:
  1. 策划:"把 3 个 NPC 围场景跑一圈,间距 >= 12 米"
     => place_npcs_on_boundary(asset_id, count=3, min_spacing=12)
  2. 策划:"随便撒 5 个金币在可行走区域,别太靠边,别互相太近"
     => place_points_inside(asset_id, count=5, min_dist=5, margin=1.5)
  3. 生成器:"我打算把机器人放在 (3, 0, -75),小猴放在 (5, 0, -150),
     他们能互相跑到吗?"
     => validate_positions([...]) 返回详细报告
  4. 主角推荐:"给我 navmesh 最中心/最大岛上一个点"
     => centroid_of_largest_island(asset_id)

所有坐标都是 Unity 世界坐标 (x, y, z),Unity 左手坐标系,y 向上。
"""
from __future__ import annotations
import math
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple, Dict, Any

from navmesh_loader import load_navmesh, NavMesh, Vec3
import navmesh_query as Q


# ---------- 数据结构 ----------

@dataclass
class Placement:
    """一个 NPC/物件的建议放置点。"""
    name: str
    position: Tuple[float, float, float]
    island_id: int  # 它所在的连通分量 id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "pos": {"x": round(self.position[0], 3),
                    "y": round(self.position[1], 3),
                    "z": round(self.position[2], 3)},
            "island": self.island_id,
        }


@dataclass
class ValidationIssue:
    code: str          # "OFF_NAVMESH" / "UNREACHABLE" / "TOO_CLOSE" / "OUT_OF_BOUNDS"
    who: List[str]     # 涉及的点 name
    detail: str


@dataclass
class ValidationReport:
    ok: bool
    asset_id: int
    name: str
    placements: List[Placement]
    issues: List[ValidationIssue]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "asset_id": self.asset_id,
            "name": self.name,
            "placements": [p.to_dict() for p in self.placements],
            "issues": [{"code": i.code, "who": i.who, "detail": i.detail} for i in self.issues],
        }

    def pretty(self) -> str:
        lines = [f"=== 验证报告: scene #{self.asset_id} {self.name}  ({'PASS' if self.ok else 'FAIL'}) ==="]
        for p in self.placements:
            x, y, z = p.position
            lines.append(f"  [{p.name}] pos=({x:.2f},{y:.2f},{z:.2f})  island#{p.island_id}")
        if self.issues:
            lines.append("  issues:")
            for i in self.issues:
                lines.append(f"    - {i.code} ({'/'.join(i.who)}): {i.detail}")
        return "\n".join(lines)


# ---------- 内部工具 ----------

def _load(asset_id_or_mesh) -> NavMesh:
    if isinstance(asset_id_or_mesh, NavMesh):
        return asset_id_or_mesh
    return load_navmesh(asset_id_or_mesh)


def _raw_cid_to_rank(m: NavMesh) -> List[int]:
    """原始 DFS cid -> 按面积降序排好的 rank (0=最大岛)。
    缓存挂在 mesh 实例自己上,避免 id() 复用带来的脏数据。"""
    cached = getattr(m, "_raw2rank", None)
    if cached is not None:
        return cached
    islands = Q.components(m)  # 已按面积降序
    mapping: List[int] = [0] * len(islands)
    comp = Q._CC.tri_component(m)
    for rank, group in enumerate(islands):
        raw_cid = comp[group[0]]
        mapping[raw_cid] = rank
    object.__setattr__(m, "_raw2rank", mapping)
    return mapping


def _island_id_of(m: NavMesh, x: float, z: float) -> int:
    """返回"岛的 rank" (按面积降序,0 = 最大岛,-1 = 不在任何岛)。"""
    ti = Q.locate_tri(m, x, z)
    if ti < 0:
        return -1
    raw = Q._CC.tri_component(m)[ti]
    return _raw_cid_to_rank(m)[raw]


# ---------- 对外接口 ----------

def place_npcs_on_boundary(
    asset_id,
    count: int,
    min_spacing: Optional[float] = None,
    loop_index: int = 0,
    name_prefix: str = "npc",
    start_offset: float = 0.0,
) -> List[Placement]:
    """
    沿外轮廓(默认最大的一个 loop)等距放 count 个 NPC。
    min_spacing: 硬下限,若周长不够容纳则 count 会被降低并打印提示。
    """
    m = _load(asset_id)
    if not m.boundary_loops:
        return []
    pts_all = [m.cverts[i] for i in m.boundary_loops[loop_index]]
    perimeter = Q._loop_perimeter(pts_all)

    if min_spacing is not None and min_spacing > 0:
        max_count = max(1, int(perimeter // min_spacing))
        if count > max_count:
            print(f"[place_npcs_on_boundary] 周长 {perimeter:.1f}m,"
                  f"min_spacing={min_spacing}m 最多容 {max_count} 个,"
                  f"已把 count 从 {count} 降到 {max_count}")
            count = max_count

    pts = Q.sample_boundary(m, count, loop_index=loop_index, start_offset=start_offset)
    result: List[Placement] = []
    for i, p in enumerate(pts):
        island = _island_id_of(m, p[0], p[2])
        result.append(Placement(name=f"{name_prefix}{i+1}", position=p, island_id=island))
    return result


def place_points_inside(
    asset_id,
    count: int,
    min_dist: Optional[float] = None,
    margin: float = 0.0,
    seed: int = 0,
    name_prefix: str = "pt",
    island_index: Optional[int] = None,
) -> List[Placement]:
    """
    在可行走面内随机撒 count 个点,两两距离 >= min_dist。
    margin: 距离边界的最小保留距离(控制"不要贴边"),默认 0。
    island_index: None 表示全部岛都接受,传 0 只在最大岛上采。
    """
    m = _load(asset_id)
    min_dist = min_dist if min_dist is not None else m.agent_radius * 4.0

    target_cc: Optional[int] = None
    if island_index is not None:
        islands = Q.components(m)
        if island_index >= len(islands):
            return []
        # 按面积降序排,island_index=0 就是最大岛
        target_cc = Q._CC.tri_component(m)[islands[island_index][0]]

    # 如果要 margin,用简单拒绝:对每个候选点检查到最近边界距离
    def dist_to_any_boundary_xz(px, pz) -> float:
        best = float("inf")
        for loop in m.boundary_loops:
            for i in range(len(loop)):
                a = m.cverts[loop[i]]
                b = m.cverts[loop[(i + 1) % len(loop)]]
                d, _, _ = Q._dist_pt_to_seg_xz(px, pz, a[0], a[2], b[0], b[2])
                if d < best:
                    best = d
                    if best < 1e-6:
                        return best
        return best

    candidates = Q.sample_inside(m, count * 3, min_dist=min_dist, seed=seed)
    picked: List[Vec3] = []
    for p in candidates:
        if target_cc is not None:
            ti = Q.locate_tri(m, p[0], p[2])
            if ti < 0 or Q._CC.tri_component(m)[ti] != target_cc:
                continue
        if margin > 0:
            if dist_to_any_boundary_xz(p[0], p[2]) < margin:
                continue
        ok = True
        for q in picked:
            if (p[0] - q[0]) ** 2 + (p[2] - q[2]) ** 2 < min_dist * min_dist:
                ok = False
                break
        if ok:
            picked.append(p)
            if len(picked) >= count:
                break

    return [
        Placement(name=f"{name_prefix}{i+1}", position=p,
                  island_id=_island_id_of(m, p[0], p[2]))
        for i, p in enumerate(picked)
    ]


def validate_positions(
    asset_id,
    positions: List[Tuple[str, Tuple[float, float, float]]],
    require_reachable_pairs: Optional[List[Tuple[str, str]]] = None,
    min_spacing: Optional[float] = None,
    snap: bool = True,
    max_snap_dist: float = 3.0,
) -> ValidationReport:
    """
    给一组 (name, (x,y,z)) 坐标,检查:
      - 是否在 navmesh 内 (snap=True 时会吸附到最近可行走点)
      - 是否在 bounds 内
      - 指定的成对可达性
      - 两两间距是否 >= min_spacing
    """
    m = _load(asset_id)
    issues: List[ValidationIssue] = []
    placements: List[Placement] = []
    name_to_pos: Dict[str, Tuple[float, float, float]] = {}

    for name, (x, y, z) in positions:
        # bounds
        if not (m.bounds_min[0] - 0.5 <= x <= m.bounds_max[0] + 0.5 and
                m.bounds_min[2] - 0.5 <= z <= m.bounds_max[2] + 0.5):
            issues.append(ValidationIssue("OUT_OF_BOUNDS", [name],
                                          f"({x:.2f},{y:.2f},{z:.2f}) 不在场景 bounds 里"))
            continue

        ti = Q.locate_tri(m, x, z)
        if ti < 0:
            if snap:
                sp = Q.snap_to_navmesh(m, x, y, z, max_dist=max_snap_dist)
                if sp is None:
                    issues.append(ValidationIssue("OFF_NAVMESH", [name],
                                                  f"XZ 平面 {max_snap_dist}m 内找不到可行走面"))
                    continue
                x, y, z = sp
                ti = Q.locate_tri(m, x, z)
            else:
                issues.append(ValidationIssue("OFF_NAVMESH", [name],
                                              f"({x:.2f},{y:.2f},{z:.2f}) 不在可行走面上"))
                continue

        if ti >= 0:
            raw = Q._CC.tri_component(m)[ti]
            island = _raw_cid_to_rank(m)[raw]
        else:
            island = -1
        placements.append(Placement(name=name, position=(x, y, z), island_id=island))
        name_to_pos[name] = (x, y, z)

    # 两两间距
    if min_spacing is not None and min_spacing > 0:
        names = [p.name for p in placements]
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a = name_to_pos[names[i]]
                b = name_to_pos[names[j]]
                d = math.hypot(a[0] - b[0], a[2] - b[2])
                if d < min_spacing:
                    issues.append(ValidationIssue(
                        "TOO_CLOSE", [names[i], names[j]],
                        f"间距 {d:.2f}m < min_spacing {min_spacing}m"))

    # 成对可达(直接用已记好的 island_id 比对,避免重复 snap)
    if require_reachable_pairs:
        name_to_island = {p.name: p.island_id for p in placements}
        for a, b in require_reachable_pairs:
            ia = name_to_island.get(a, -2)
            ib = name_to_island.get(b, -2)
            if ia < 0 or ib < 0 or ia != ib:
                issues.append(ValidationIssue(
                    "UNREACHABLE", [a, b],
                    f"在不同岛 (island#{ia} vs island#{ib})"))

    report = ValidationReport(
        ok=(len(issues) == 0),
        asset_id=m.asset_id,
        name=m.name,
        placements=placements,
        issues=issues,
    )
    return report


def centroid_of_largest_island(asset_id) -> Optional[Vec3]:
    """返回 navmesh 最大岛的"重心":按三角形面积加权,吸附回 navmesh 上。
    可用作:主角推荐出生点 / 相机兴趣点。"""
    m = _load(asset_id)
    islands = Q.components(m)
    if not islands:
        return None
    big = islands[0]
    total = 0.0
    cx = cy = cz = 0.0
    for ti in big:
        w = m.tri_xz_areas[ti]
        a, b, c = m.tris[ti]
        ax, ay, az = m.cverts[a]
        bx, by, bz = m.cverts[b]
        ccx, ccy, ccz = m.cverts[c]
        tx = (ax + bx + ccx) / 3.0
        ty = (ay + by + ccy) / 3.0
        tz = (az + bz + ccz) / 3.0
        cx += tx * w
        cy += ty * w
        cz += tz * w
        total += w
    if total <= 0:
        return None
    cx /= total
    cy /= total
    cz /= total
    # 吸附回 navmesh
    sp = Q.snap_to_navmesh(m, cx, cy, cz, max_dist=100.0)
    return sp if sp is not None else (cx, cy, cz)


def scene_summary(asset_id) -> Dict[str, Any]:
    """一页纸场景摘要:bounds / 岛数 / 岛面积 / agent / 最大岛中心。
    适合让关卡生成器一开始先看一眼。"""
    m = _load(asset_id)
    islands = Q.components(m)
    island_info = []
    for idx, group in enumerate(islands):
        area = sum(m.tri_xz_areas[t] for t in group)
        verts = set()
        for t in group:
            verts.update(m.tris[t])
        xs = [m.cverts[v][0] for v in verts]
        ys = [m.cverts[v][1] for v in verts]
        zs = [m.cverts[v][2] for v in verts]
        island_info.append({
            "island_id": idx,
            "tri_count": len(group),
            "xz_area": round(area, 2),
            "bbox_min": [round(min(xs), 2), round(min(ys), 2), round(min(zs), 2)],
            "bbox_max": [round(max(xs), 2), round(max(ys), 2), round(max(zs), 2)],
        })
    centroid = centroid_of_largest_island(m)
    return {
        "asset_id": m.asset_id,
        "name": m.name,
        "agent": {
            "radius": m.agent_radius,
            "height": m.agent_height,
            "step": m.agent_step,
            "slope": m.agent_slope,
        },
        "bounds_min": list(m.bounds_min),
        "bounds_max": list(m.bounds_max),
        "island_count": len(islands),
        "islands": island_info,
        "total_walkable_xz_area": round(m.total_walkable_xz_area, 2),
        "largest_island_centroid": (
            [round(c, 3) for c in centroid] if centroid else None
        ),
        "notes": [
            "坐标均为 Unity 世界坐标 (x,y,z),y 向上",
            "island_id 越小面积越大(已按面积降序)",
            "validate_positions 跨 island 的 pair 会报 UNREACHABLE",
        ],
    }


# ---------- CLI 测试 ----------

if __name__ == "__main__":
    import sys, json
    asset = int(sys.argv[1]) if len(sys.argv) > 1 else 12836

    print(">>> 场景摘要")
    print(json.dumps(scene_summary(asset), ensure_ascii=False, indent=2))

    print("\n>>> 在外轮廓放 3 个 NPC,间距 >= 12m")
    npcs = place_npcs_on_boundary(asset, 3, min_spacing=12.0)
    for p in npcs:
        print(" ", p.to_dict())

    print("\n>>> 在最大岛上撒 5 个物件,min_dist=5,margin=1.5")
    items = place_points_inside(asset, 5, min_dist=5.0, margin=1.5, island_index=0, seed=42)
    for p in items:
        print(" ", p.to_dict())

    print("\n>>> 验证一组坐标")
    rep = validate_positions(
        asset,
        [
            ("hero",   (0.0, 0.0, -80.0)),
            ("robot",  (5.0, 0.0, -75.0)),
            ("apple",  (1.0, 0.0, -150.0)),
            ("cheat",  (100.0, 0.0, 100.0)),  # 故意越界
        ],
        require_reachable_pairs=[("hero", "robot"), ("hero", "apple")],
        min_spacing=3.0,
    )
    print(rep.pretty())
