# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "mcp/hetu_mcp")
from script_definitions import load_script_block_definitions
defs = load_script_block_definitions()
print(f"全部积木: {len(defs)} 个")
cats = {}
for k, v in defs.items():
    c = v.get("category", "?")
    cats.setdefault(c, []).append(k)
for cat, names in sorted(cats.items()):
    print(f"\n  [{cat}] {len(names)} 个:")
    for n in sorted(names):
        print(f"    {n}")
