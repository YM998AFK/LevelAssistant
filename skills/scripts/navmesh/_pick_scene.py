# -*- coding: utf-8 -*-
"""从 160 个场景里挑一个"完整连通 + 面积适中 + 有内部空间"的好场景做演示。"""
import io, json, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

idx = Path(__file__).parent / "navmesh_cache" / "_scene_summary_index.json"
data = json.loads(idx.read_text(encoding="utf-8"))

rows = []
for aid_s, s in data.items():
    if "error" in s:
        continue
    rows.append({
        "aid": int(aid_s),
        "name": s["name"],
        "islands": s["island_count"],
        "area": s["total_walkable_xz_area"],
        "size_x": s["bounds_max"][0] - s["bounds_min"][0],
        "size_z": s["bounds_max"][2] - s["bounds_min"][2],
        "centroid": s["largest_island_centroid"],
    })

# 筛选: 1 岛完整连通, 面积 100 ~ 2000 m², XZ 都在 50m 内 (好取景)
candidates = [
    r for r in rows
    if r["islands"] == 1
    and 100 <= r["area"] <= 2000
    and r["size_x"] < 50 and r["size_z"] < 50
]
candidates.sort(key=lambda r: r["area"])

print(f"=== 1 岛完整连通 + 小/中型场景候选 ({len(candidates)} 个) ===\n")
print(f"{'aid':>6}  {'name':<18}  {'area':>8}  bbox    centroid")
for r in candidates[:20]:
    cx, cy, cz = r["centroid"]
    print(f"{r['aid']:>6}  {r['name'][:18]:<18}  {r['area']:>8.0f}  "
          f"({r['size_x']:.0f}x{r['size_z']:.0f})    ({cx:.2f},{cy:.2f},{cz:.2f})")
