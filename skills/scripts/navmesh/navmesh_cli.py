# -*- coding: utf-8 -*-
"""
NavMesh 命令行工具 —— 日常诊断 / 预览 / 报告。

用法:
  # 场景概览
  python scripts/navmesh/navmesh_cli.py summary 12836
  python scripts/navmesh/navmesh_cli.py summary --all            # 全部场景

  # 沿边界放 NPC,间距 >= 12
  python scripts/navmesh/navmesh_cli.py edge 12836 --count 3 --min-spacing 12

  # 在最大岛内随机撒点
  python scripts/navmesh/navmesh_cli.py inside 12836 --count 5 --min-dist 5 --margin 1.5

  # 验证一组坐标
  python scripts/navmesh/navmesh_cli.py validate 12836 --positions "hero,0,0,-80;apple,1,0,-150"

  # 预览:导出一张 ASCII 俯视图(XZ)
  python scripts/navmesh/navmesh_cli.py preview 12836

  # 导出 scene_summary.json 索引 (对全部已导出场景)
  python scripts/navmesh/navmesh_cli.py export-index
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = REPO_ROOT / "scripts" / "navmesh" / "navmesh_cache"

sys.path.insert(0, str(Path(__file__).parent))
from navmesh_loader import load_navmesh  # noqa
import navmesh_query as Q                 # noqa
import navmesh_validate as V              # noqa


def _iter_cached_asset_ids():
    for p in sorted(CACHE_DIR.glob("*.json")):
        if p.name.startswith("_"):
            continue
        try:
            yield int(p.stem)
        except ValueError:
            continue


def cmd_summary(args):
    if args.all:
        out = []
        for aid in _iter_cached_asset_ids():
            try:
                s = V.scene_summary(aid)
                out.append({
                    "asset_id": s["asset_id"],
                    "name": s["name"],
                    "island_count": s["island_count"],
                    "xz_area": s["total_walkable_xz_area"],
                    "bbox_size": [
                        round(s["bounds_max"][i] - s["bounds_min"][i], 2)
                        for i in range(3)
                    ],
                })
            except Exception as e:
                out.append({"asset_id": aid, "error": str(e)})
        if args.json:
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            print(f"{'asset_id':>8}  {'name':<22}  {'islands':>7}  {'area(m^2)':>10}  bbox_size(x,y,z)")
            for s in out:
                if "error" in s:
                    print(f"{s['asset_id']:>8}  ERROR: {s['error']}")
                    continue
                bx, by, bz = s["bbox_size"]
                print(f"{s['asset_id']:>8}  {s['name'][:22]:<22}  "
                      f"{s['island_count']:>7}  {s['xz_area']:>10.2f}  "
                      f"({bx:.1f},{by:.1f},{bz:.1f})")
        return 0

    s = V.scene_summary(args.asset_id)
    print(json.dumps(s, ensure_ascii=False, indent=2))
    return 0


def cmd_edge(args):
    ps = V.place_npcs_on_boundary(
        args.asset_id, count=args.count,
        min_spacing=args.min_spacing,
        loop_index=args.loop,
        start_offset=args.start,
    )
    out = {
        "asset_id": args.asset_id,
        "count_requested": args.count,
        "count_returned": len(ps),
        "placements": [p.to_dict() for p in ps],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if ps else 1


def cmd_inside(args):
    ps = V.place_points_inside(
        args.asset_id, count=args.count,
        min_dist=args.min_dist,
        margin=args.margin,
        seed=args.seed,
        island_index=args.island,
    )
    out = {
        "asset_id": args.asset_id,
        "count_requested": args.count,
        "count_returned": len(ps),
        "placements": [p.to_dict() for p in ps],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if len(ps) >= args.count else 2


def _parse_positions(s: str) -> List[Tuple[str, Tuple[float, float, float]]]:
    out = []
    for piece in s.split(";"):
        piece = piece.strip()
        if not piece:
            continue
        parts = piece.split(",")
        if len(parts) != 4:
            raise ValueError(f"位置格式错误: {piece}, 需要 name,x,y,z")
        name, x, y, z = parts
        out.append((name.strip(), (float(x), float(y), float(z))))
    return out


def _parse_pairs(s: str) -> List[Tuple[str, str]]:
    out = []
    for piece in s.split(";"):
        piece = piece.strip()
        if not piece:
            continue
        a, b = [x.strip() for x in piece.split(",")]
        out.append((a, b))
    return out


def cmd_validate(args):
    poses = _parse_positions(args.positions)
    pairs = _parse_pairs(args.reachable) if args.reachable else None
    rep = V.validate_positions(
        args.asset_id, poses,
        require_reachable_pairs=pairs,
        min_spacing=args.min_spacing,
        snap=not args.no_snap,
        max_snap_dist=args.max_snap,
    )
    if args.json:
        print(json.dumps(rep.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(rep.pretty())
    return 0 if rep.ok else 3


def cmd_preview(args):
    """把 navmesh 渲染成 ASCII 俯视图 (XZ 平面)。"""
    m = load_navmesh(args.asset_id)
    W = args.width
    x0, _, z0 = m.bounds_min
    x1, _, z1 = m.bounds_max
    dx = x1 - x0
    dz = z1 - z0
    if dx < 1e-6 or dz < 1e-6:
        print("场景尺寸过小")
        return 1
    # 保持等比例,按 Z 长条方向决定高度
    # 字符纵横比 ~2:1 (字符高度 ~= 宽度 2 倍), 所以 Z/H 需要除以 2
    aspect = (dz / dx) / 2.0
    H = max(6, min(args.max_height, int(W * aspect)))

    grid = [[" "] * W for _ in range(H)]

    def plot(x, z, ch):
        if x0 <= x <= x1 and z0 <= z <= z1:
            u = int((x - x0) / dx * (W - 1))
            v = int((z - z0) / dz * (H - 1))
            if 0 <= u < W and 0 <= v < H:
                if grid[v][u] == " " or ch in "@*":
                    grid[v][u] = ch

    # 用每个三角形的重心 "点画",按 island rank 用不同字符
    comp = Q._CC.tri_component(m)
    r2r = V._raw_cid_to_rank(m)
    CHARS = ".oxbq+#=%$"
    for ti, (a, b, c) in enumerate(m.tris):
        ax, _, az = m.cverts[a]
        bx, _, bz = m.cverts[b]
        cx, _, cz = m.cverts[c]
        rank = r2r[comp[ti]]
        ch = CHARS[rank % len(CHARS)]
        # 粗略在三角形上散点
        for t in range(10):
            u, v = (t + 1) / 11, ((t * 3) % 10 + 1) / 12
            if u + v > 1:
                u, v = 1 - u, 1 - v
            w = 1 - u - v
            x = u * ax + v * bx + w * cx
            z = u * az + v * bz + w * cz
            plot(x, z, ch)

    # 边界
    for loop in m.boundary_loops:
        pts = [m.cverts[i] for i in loop]
        for i in range(len(pts)):
            a = pts[i]
            b = pts[(i + 1) % len(pts)]
            steps = max(2, int(max(abs(a[0] - b[0]), abs(a[2] - b[2])) * 2))
            for k in range(steps + 1):
                t = k / steps
                x = a[0] + (b[0] - a[0]) * t
                z = a[2] + (b[2] - a[2]) * t
                plot(x, z, "*")

    print(f"# NavMesh preview  scene #{m.asset_id} {m.name}")
    print(f"# X: {x0:.2f} -> {x1:.2f}   Z: {z0:.2f} (top) -> {z1:.2f} (bottom)")
    print(f"# islands (按面积降序):")
    for rank in range(len(set(r2r))):
        print(f"#   rank#{rank}: '{CHARS[rank % len(CHARS)]}'")
    print("# 边界: '*'")
    print("+" + "-" * W + "+")
    for row in grid:
        print("|" + "".join(row) + "|")
    print("+" + "-" * W + "+")
    return 0


def cmd_export_index(args):
    """把所有已缓存的 navmesh 汇总成一个大 JSON (供 MCP / 关卡生成器用)。"""
    out = {}
    for aid in _iter_cached_asset_ids():
        try:
            out[str(aid)] = V.scene_summary(aid)
        except Exception as e:
            out[str(aid)] = {"error": str(e)}
    dest = CACHE_DIR / "_scene_summary_index.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"写入 {dest}  共 {len(out)} 个场景")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="NavMesh 命令行工具")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("summary", help="场景概览")
    p.add_argument("asset_id", nargs="?", type=int, default=0)
    p.add_argument("--all", action="store_true", help="输出所有已缓存场景的简表")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_summary)

    p = sub.add_parser("edge", help="沿外轮廓等距放点(默认最大岛)")
    p.add_argument("asset_id", type=int)
    p.add_argument("--count", type=int, default=3)
    p.add_argument("--min-spacing", type=float, default=None)
    p.add_argument("--loop", type=int, default=0)
    p.add_argument("--start", type=float, default=0.0)
    p.set_defaults(func=cmd_edge)

    p = sub.add_parser("inside", help="在可行走面内随机撒点")
    p.add_argument("asset_id", type=int)
    p.add_argument("--count", type=int, default=3)
    p.add_argument("--min-dist", type=float, default=None)
    p.add_argument("--margin", type=float, default=0.0, help="距离边界最小保留距离")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--island", type=int, default=None, help="0=最大岛,留空=任意")
    p.set_defaults(func=cmd_inside)

    p = sub.add_parser("validate", help="验证一组坐标")
    p.add_argument("asset_id", type=int)
    p.add_argument("--positions", required=True,
                   help="格式: name,x,y,z;name2,x,y,z")
    p.add_argument("--reachable", default=None,
                   help="需要互达的 name 对: a,b;c,d")
    p.add_argument("--min-spacing", type=float, default=None)
    p.add_argument("--max-snap", type=float, default=3.0)
    p.add_argument("--no-snap", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("preview", help="ASCII 俯视预览 (XZ)")
    p.add_argument("asset_id", type=int)
    p.add_argument("--width", type=int, default=100)
    p.add_argument("--max-height", type=int, default=60)
    p.set_defaults(func=cmd_preview)

    p = sub.add_parser("export-index", help="生成 _scene_summary_index.json")
    p.set_defaults(func=cmd_export_index)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
