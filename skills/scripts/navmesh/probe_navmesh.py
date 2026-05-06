# -*- coding: utf-8 -*-
"""
探测 Unity NavMesh.asset 能拿到哪些字段。
"""
import sys, os, json
import UnityPy

def main(asset_path: str):
    env = UnityPy.load(asset_path)
    print(f"[file] {asset_path}")
    for obj in env.objects:
        print(f"  - type={obj.type.name}  path_id={obj.path_id}  container={getattr(obj,'container',None)}")
        try:
            tree = obj.read_typetree()
        except Exception as e:
            print(f"    read_typetree 失败: {e}")
            continue
        print("    keys:", list(tree.keys())[:40])
        if "m_NavMeshTiles" in tree:
            tiles = tree["m_NavMeshTiles"]
            print(f"    NavMesh tile count = {len(tiles)}")
            for i, t in enumerate(tiles[:3]):
                print(f"      tile[{i}] keys = {list(t.keys())}")
                md = t.get("m_MeshData")
                if md is not None:
                    print(f"      tile[{i}] m_MeshData len = {len(md)} bytes")
        for k in ("m_NavMeshBuildSettings","m_SourceBounds","m_Position","m_Rotation","m_AgentTypeID","m_HeightMeshes","m_Heightmaps","m_OffMeshLinks"):
            if k in tree:
                v = tree[k]
                if isinstance(v,(list,dict)):
                    print(f"    {k}: <{type(v).__name__} len={len(v)}>")
                else:
                    print(f"    {k}: {v}")

if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else r"D:\meishu\Assets\BundleResources\ide\scene\l1\l1-02-02-c\l1-02-02-c\NavMesh.asset"
    main(p)
