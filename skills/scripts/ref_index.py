"""ref_index.py — 聚合所有包的 _analysis.json → 一张 参考-extracted/index.md

列出每个包的关键指标，按模板族聚类，新包一目了然。
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTRACT_DIR = ROOT / '参考-extracted'


def load_all():
    records = []
    for p in sorted(EXTRACT_DIR.iterdir()):
        if not p.is_dir() or p.name == '_mine':
            continue
        aj = p / '_analysis.json'
        if not aj.exists():
            continue
        try:
            data = json.load(open(aj, encoding='utf-8'))
            data['_pack_dir'] = str(p)
            records.append(data)
        except Exception as e:
            print(f"[warn] skip {p.name}: {e}")
    return records


def render(records):
    L = []
    L.append("# 参考包索引 (refs_index)\n")
    L.append(f"> 由 `scripts/ref_index.py` 聚合 `{EXTRACT_DIR.name}/*/_analysis.json` 生成。")
    L.append(f"> 共 **{len(records)}** 个参考包（不含 `_mine/`）。\n")
    L.append("")

    # Bucket by family
    buckets = defaultdict(list)
    for r in records:
        fams = r.get('family') or []
        if not fams:
            buckets['未知'].append(r)
        else:
            for f in fams:
                buckets[f['code']].append(r)

    L.append("## 模板族分布\n")
    L.append("| 族 | 包数 |")
    L.append("|---|---|")
    for fam, recs in sorted(buckets.items(), key=lambda x: -len(x[1])):
        L.append(f"| `{fam}` | {len(recs)} |")
    L.append("")

    # Main index table
    L.append("## 包清单（按 L0 骨架得分排序）\n")
    L.append("| 包 | 模式 | 族 | L0 变量 | L0 消息 | L1 | props2 | #EVENT | fragments | handlers | 子节点 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")

    def score(r):
        s = r.get('skel_score', {})
        v_ratio = s.get('L0_vars_ratio', '0/12').split('/')[0]
        e_ratio = s.get('L0_events_ratio', '0/6').split('/')[0]
        try:
            return int(v_ratio), int(e_ratio)
        except Exception:
            return 0, 0

    records_sorted = sorted(records, key=lambda r: (-score(r)[0], -score(r)[1], r.get('pack', '')))
    for r in records_sorted:
        s = r.get('skel_score', {})
        fams = ', '.join(f['code'] for f in (r.get('family') or []))
        hats = r.get('hats') or {}
        frag_total = sum(hats.values())
        handlers = len(r.get('handlers') or {})
        scene_kids = len(r.get('scene_children') or [])
        L.append(f"| `{r.get('pack')}` | {r.get('mode')} | {fams or '-'} "
                 f"| {s.get('L0_vars_ratio')} | {s.get('L0_events_ratio')} "
                 f"| {len(s.get('L1_events', []))}/2 "
                 f"| {len(r.get('props2_vars') or [])} | {len(r.get('events') or [])} "
                 f"| {frag_total} | {handlers} | {scene_kids} |")
    L.append("")

    L.append("## 按族详单\n")
    for fam, recs in sorted(buckets.items(), key=lambda x: -len(x[1])):
        L.append(f"\n### {fam}（{len(recs)} 个包）\n")
        for r in sorted(recs, key=lambda x: x.get('pack', '')):
            s = r.get('skel_score', {})
            fams = ', '.join(f['code'] for f in (r.get('family') or []))
            # 特别点出 missing
            missing = []
            if s.get('L0_vars_missing'):
                missing.append(f"缺变量 {s['L0_vars_missing']}")
            if s.get('L0_events_missing'):
                missing.append(f"缺消息 {s['L0_events_missing']}")
            miss_s = ('；' + '；'.join(missing)) if missing else ''
            L.append(f"- **{r.get('pack')}**  模式={r.get('mode')}  "
                     f"L0={s.get('L0_vars_ratio')}+{s.get('L0_events_ratio')}{miss_s}")

    return '\n'.join(L)


def main():
    records = load_all()
    md = render(records)
    out = EXTRACT_DIR / 'index.md'
    out.write_text(md, encoding='utf-8')
    print(f"[index] wrote {out}  packs={len(records)}")


if __name__ == '__main__':
    main()
