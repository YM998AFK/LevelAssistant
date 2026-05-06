"""单位复核: 扫描所有参考包里的 GotoPosition3D 参数值，汇总数值范围。
读每个参考包的 .ws JSON, 找出所有 GotoPosition3D / GlideSecsToPosition3D 的参数，
打印出来让人肉眼判断"这个量级是米还是厘米"。

单位判断基准:
- Character.Size[Y] 约 1~3，Scale 0.6~1，最终身高 ~1~3m
- Scene.BoundsSize = [16, 7.67, 12] (米)
- 如果 Goto 参数 abs 值 > 10 → 很可能是厘米 (米值会超出场景)
- 如果 Goto 参数 abs 值 < 10 → 很可能是米 (符合场景尺度)
"""

import json
import pathlib


def scan(obj, out, depth=0):
    if isinstance(obj, dict):
        d = obj.get("define")
        if d in ("GotoPosition3D", "GlideSecsToPosition3D"):
            try:
                ps = obj["sections"][0]["params"]
                vals = []
                for p in ps:
                    if isinstance(p, dict):
                        vals.append(p.get("val", "?"))
                    else:
                        vals.append("?")
                out.append((d, vals))
            except Exception:
                pass
        for v in obj.values():
            scan(v, out, depth + 1)
    elif isinstance(obj, list):
        for v in obj:
            scan(v, out, depth + 1)


def main():
    root = pathlib.Path("参考-extracted")
    by_pkg = {}
    for p in sorted(root.rglob("*.ws")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        bs = data.get("scene", {}).get("props", {}).get("BoundsSize", "?")
        out = []
        scan(data, out)
        if out:
            by_pkg[p.parent.name] = (bs, out)

    for pkg, (bs, calls) in by_pkg.items():
        print(f"=== {pkg} ===  BoundsSize={bs}  ({len(calls)} calls)")
        for d, vals in calls[:8]:
            try:
                nums = [float(str(x)) for x in vals]
                max_abs = max(abs(n) for n in nums)
                hint = "米-like" if max_abs < 10 else ("厘米-like" if max_abs > 30 else "?")
                print(f"   {d}({vals})  max|val|={max_abs:.3f}  [{hint}]")
            except Exception:
                print(f"   {d}({vals})  [non-numeric]")


if __name__ == "__main__":
    main()
