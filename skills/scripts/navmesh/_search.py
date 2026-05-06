# -*- coding: utf-8 -*-
import io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
idx = json.load(open(r"scripts\navmesh\navmesh_cache\_scene_summary_index.json", encoding="utf-8"))
kw = sys.argv[1] if len(sys.argv) > 1 else "藏画"
hits = [(aid, v) for aid, v in idx.items() if kw in v.get("name","")]
print(f"搜 '{kw}': {len(hits)} 个匹配")
for aid, v in hits:
    print(f"  {aid}  {v['name']}  islands={v['island_count']}  area={v['total_walkable_xz_area']:.0f}m^2  centroid={v['largest_island_centroid']}")
