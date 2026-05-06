"""查每个参考包的 BoundsCenter / BoundsSize, 与 Character Position 对比。"""
import json
import pathlib

pkgs = [
    "参考-extracted/14-3-6",
    "参考-extracted/d#14-1#8",
    "参考-extracted/d#13-4#9",
    "参考-extracted/15-2 关卡3",
    "参考-extracted/14-1 低 练习14",
    "参考-extracted/13-3 高 练习19",
]
for t in pkgs:
    ws = next(pathlib.Path(t).glob("*.ws"))
    data = json.loads(ws.read_text(encoding="utf-8"))
    p = data.get("scene", {}).get("props", {})
    bc = p.get("BoundsCenter", "?")
    bs = p.get("BoundsSize", "?")
    print(f"\n=== {t} ===")
    print(f"  BoundsCenter = {bc}")
    print(f"  BoundsSize   = {bs}")

    def walk(n, out):
        if isinstance(n, dict):
            if n.get("type") == "Character":
                props = n.get("props", {})
                out.append((props.get("Name"), props.get("Position"), props.get("Size"), props.get("Scale")))
            for c in n.get("children", []) or []:
                walk(c, out)

    chars = []
    walk(data.get("scene", {}), chars)
    for name, pos, size, scale in chars:
        print(f"  Character {name!r}: Position={pos}, Size={size}, Scale={scale}")
