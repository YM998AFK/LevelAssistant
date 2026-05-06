# -*- coding: utf-8 -*-
"""对 160 个 NavMesh 场景做宏观统计:面积分布 / 岛数 / 大小分类。"""
import io, json, sys
from pathlib import Path
from collections import Counter
# Windows 控制台默认 gbk,强制 utf-8 输出避免乱码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))
import navmesh_validate as V

CACHE = Path(__file__).parent / "navmesh_cache"

rows = []
for p in sorted(CACHE.glob("*.json")):
    if p.name.startswith("_"):
        continue
    try:
        aid = int(p.stem)
    except ValueError:
        continue
    try:
        s = V.scene_summary(aid)
        rows.append({
            "asset_id": aid,
            "name": s["name"],
            "islands": s["island_count"],
            "area": s["total_walkable_xz_area"],
            "size_x": s["bounds_max"][0] - s["bounds_min"][0],
            "size_z": s["bounds_max"][2] - s["bounds_min"][2],
        })
    except Exception as e:
        print(f"[ERR] {aid} {e}")

n = len(rows)
print(f"\n=== 160 个场景宏观统计 ({n} 成功) ===\n")

print("按面积分段:")
def bucket(a):
    if a < 100: return "A) <100 m² (小房间)"
    if a < 500: return "B) 100-500 m² (中等)"
    if a < 2000: return "C) 500-2k m² (大关卡)"
    if a < 20000: return "D) 2k-20k m² (大地图)"
    if a < 200000: return "E) 20k-200k m² (开阔世界)"
    return "F) >200k m² (海量场景,可能包含远景/地形)"
buckets = Counter(bucket(r["area"]) for r in rows)
for k in sorted(buckets):
    print(f"  {k:40} : {buckets[k]}")

print("\n按岛数(连通分量):")
ibuckets = Counter(
    "1 (完整连通)" if r["islands"] == 1 else
    f"2-5" if r["islands"] <= 5 else
    f"6-20" if r["islands"] <= 20 else
    f"21-100" if r["islands"] <= 100 else
    f">100 (极度碎裂)"
    for r in rows
)
for k in ("1 (完整连通)", "2-5", "6-20", "21-100", ">100 (极度碎裂)"):
    if k in ibuckets:
        print(f"  {k:20} : {ibuckets[k]}")

print("\n前 10 大场景 (按可行走面积):")
for r in sorted(rows, key=lambda x: -x["area"])[:10]:
    print(f"  {r['asset_id']:>6}  {r['name'][:20]:<20}  {r['area']:>12.0f} m²  "
          f"islands={r['islands']:>3}  "
          f"bbox=({r['size_x']:.0f},{r['size_z']:.0f})")

print("\n最碎裂的 10 个场景 (岛数最多):")
for r in sorted(rows, key=lambda x: -x["islands"])[:10]:
    print(f"  {r['asset_id']:>6}  {r['name'][:20]:<20}  islands={r['islands']:>3}  area={r['area']:>10.0f} m²")

print(f"\n全部数据已可用: scripts/navmesh/navmesh_cache/*.json  ({n} 个)")
