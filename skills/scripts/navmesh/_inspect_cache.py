# -*- coding: utf-8 -*-
"""快速检查一个 navmesh_cache/<assetid>.json 的结构和合理性。"""
import json, sys
from pathlib import Path

p = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\Hetao\Desktop\公司\scripts\navmesh\navmesh_cache\12836.json"
d = json.load(open(p, "r", encoding="utf-8"))

print(f"=== 文件: {p}  ({Path(p).stat().st_size} bytes) ===\n")

print("=== 顶层字段 ===")
for k in d.keys():
    print(f"  {k}")
print()

print("=== 基本信息 ===")
for k in ("asset_id", "name", "unity_file", "unity_version", "exported_at", "export_version"):
    print(f"  {k:15} = {d.get(k)}")
print()

print("=== agent ===")
for k, v in d["agent"].items():
    print(f"  {k:12} = {v}")
print()

print("=== bounds ===")
bmin, bmax = d["bounds"]["min"], d["bounds"]["max"]
print(f"  min  = [{bmin[0]:.2f}, {bmin[1]:.2f}, {bmin[2]:.2f}]")
print(f"  max  = [{bmax[0]:.2f}, {bmax[1]:.2f}, {bmax[2]:.2f}]")
print(f"  size = [{bmax[0]-bmin[0]:.2f}, {bmax[1]-bmin[1]:.2f}, {bmax[2]-bmin[2]:.2f}] (米)")
print()

nm = d["navmesh"]
print("=== navmesh ===")
print(f"  vert_count = {nm['vert_count']}")
print(f"  tri_count  = {nm['tri_count']}")
if nm['vert_count'] > 0:
    print(f"  first 3 verts = {nm['vertices'][:3]}")
if nm['tri_count'] > 0:
    print(f"  first 3 tris  = {nm['triangles'][:3]}")
    areas = nm.get("areas", [])
    print(f"  areas unique  = {sorted(set(areas))}")
print()

print("=== areas_legend ===")
for k, v in d.get("areas_legend", {}).items():
    print(f"  {k} => {v}")
