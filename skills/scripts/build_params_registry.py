"""Scan all reference .ws files and derive the block params-count registry.

Strategy:
  1. Walk every node in each .ws (scene tree + BlockScript.fragments + nested blocks).
  2. For every block node (with "define" field), record len(sections[0].params).
  3. Aggregate: {define: Counter({params_count: freq})}.
  4. Classify each define:
       - "strict":   one params_count observed (>=3 sightings). Hard-enforced.
       - "variable": multiple params_counts observed. Warn, not fail.
       - "rare":     observed < 3 times total. Skip strict check.
  5. Write scripts/params_registry.json.

Run:  python scripts/build_params_registry.py
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

REF_DIR = Path(r"c:\Users\Hetao\Desktop\公司\参考-extracted")
OUT = Path(r"c:\Users\Hetao\Desktop\公司\scripts\params_registry.json")

MIN_STRICT_SIGHTINGS = 3


def walk_block(block, out_counts: dict):
    """Recurse a block tree, counting every block occurrence."""
    if not isinstance(block, dict):
        return
    define = block.get("define")
    if define:
        sections = block.get("sections", [])
        params = sections[0].get("params", []) if sections else []
        out_counts[define][len(params)] += 1

    for sec in block.get("sections", []) or []:
        for p in sec.get("params", []) or []:
            if isinstance(p, dict) and p.get("type") == "block":
                val = p.get("val")
                if val:
                    walk_block(val, out_counts)
        for c in sec.get("children", []) or []:
            walk_block(c, out_counts)


def walk_node(node, out_counts: dict):
    """Recurse a scene node: descend children, and scan any BlockScript.fragments."""
    if not isinstance(node, dict):
        return
    if node.get("type") == "BlockScript":
        for frag in node.get("fragments", []) or []:
            head = frag.get("head")
            if head:
                walk_block(head, out_counts)
        for mb in node.get("myblocks", []) or []:
            frag = mb.get("fragment") if isinstance(mb, dict) else None
            if frag and frag.get("head"):
                walk_block(frag["head"], out_counts)
    for c in node.get("children", []) or []:
        walk_node(c, out_counts)


def main() -> int:
    ws_files = sorted(REF_DIR.rglob("*.ws"))
    if not ws_files:
        print(f"[FAIL] no .ws files under {REF_DIR}")
        return 2

    counts: dict[str, Counter] = defaultdict(Counter)
    per_level: dict[str, int] = defaultdict(int)

    for ws in ws_files:
        try:
            data = json.loads(ws.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[skip] {ws.name}: {e}")
            continue
        scene = data.get("scene")
        if scene:
            walk_node(scene, counts)
            per_level[str(ws.parent.name)] += 1

    registry = {
        "__meta__": {
            "source": "参考-extracted/*.ws",
            "levels_scanned": len(ws_files),
            "distinct_defines": len(counts),
            "min_strict_sightings": MIN_STRICT_SIGHTINGS,
            "rule": {
                "strict": "only one params_count seen AND sightings >= min_strict_sightings",
                "variable": "multiple params_counts seen",
                "rare": "total sightings < min_strict_sightings",
            },
        },
        "entries": {},
    }

    classification_stats = Counter()
    for define, by_count in sorted(counts.items()):
        total = sum(by_count.values())
        distinct = len(by_count)
        if total < MIN_STRICT_SIGHTINGS:
            kind = "rare"
            expect = None
        elif distinct == 1:
            kind = "strict"
            expect = next(iter(by_count))
        else:
            kind = "variable"
            expect = by_count.most_common(1)[0][0]
        classification_stats[kind] += 1
        registry["entries"][define] = {
            "kind": kind,
            "expect": expect,
            "total": total,
            "distribution": dict(by_count),
        }

    OUT.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    print(f"[OK] wrote {OUT}")
    print(f"  levels scanned: {len(ws_files)}")
    print(f"  distinct defines: {len(counts)}")
    for kind, n in classification_stats.most_common():
        print(f"  {kind}: {n}")

    print("\n--- variable (ambiguous params-count) ---")
    for define, meta in registry["entries"].items():
        if meta["kind"] == "variable":
            dist = ", ".join(f"{k}={v}" for k, v in sorted(meta["distribution"].items()))
            print(f"  {define}: expect={meta['expect']} (seen: {dist})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
