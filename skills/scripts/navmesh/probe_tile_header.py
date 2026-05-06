# -*- coding: utf-8 -*-
"""
查看 Unity NavMeshData 中每个 tile.m_MeshData 的二进制头,
判断是否为 Detour dtNavMeshCreate/dtMeshHeader 标准格式。
"""
import sys, struct
import UnityPy

def main(asset_path: str):
    env = UnityPy.load(asset_path)
    for obj in env.objects:
        if obj.type.name != "NavMeshData":
            continue
        tree = obj.read_typetree()
        tiles = tree.get("m_NavMeshTiles", [])
        for i, t in enumerate(tiles):
            md = bytes(t["m_MeshData"])
            print(f"tile[{i}] bytes={len(md)}")
            head = md[:64]
            print("  hex :", " ".join(f"{b:02X}" for b in head))
            magic = md[:4]
            print("  magic(ascii):", repr(magic))
            if len(md) >= 8:
                m_int_be = struct.unpack(">I", md[:4])[0]
                m_int_le = struct.unpack("<I", md[:4])[0]
                v_int_le = struct.unpack("<I", md[4:8])[0]
                print(f"  u32 be=0x{m_int_be:08X}  u32 le=0x{m_int_le:08X}  version(le)={v_int_le}")
            print()

if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else r"D:\meishu\Assets\BundleResources\ide\scene\l1\l1-02-02-c\l1-02-02-c\NavMesh.asset"
    main(p)
