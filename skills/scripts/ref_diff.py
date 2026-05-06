"""ref_diff.py — 两个参考包（或母本 vs 变体）的结构化 diff

用法:
    python scripts/ref_diff.py <base_dir> <variant_dir>
    # 例：改关卡前对比
    python scripts/ref_diff.py 参考-extracted/练习5 参考-extracted/练习7

输出到 stdout（写入 `<variant>/_diff_vs_<base>.md` 如果 --save）:
  §1 props2 变量差异（新增 / 删除 / 同名不同值）
  §2 #EVENT 差异
  §3 handlers 差异
  §4 场景顶层 children 差异（按 name+type 匹配）
  §5 BlockScript fragments 差异（hat 签名逐条对比）
  §6 Broadcast 序列差异
"""
import argparse
import json
from pathlib import Path

# 复用 ref_scan 的提取器
import sys
sys.path.insert(0, str(Path(__file__).parent))
from ref_scan import (  # noqa: E402
    extract_props2, extract_scene_children, extract_fragments,
    extract_broadcast_sequences, extract_handlers,
)


def load_ws(pack_dir: Path):
    for f in pack_dir.iterdir():
        if f.suffix == '.ws':
            return f, json.load(open(f, encoding='utf-8'))
    return None, None


def diff_sets(a, b, label_a, label_b):
    sa, sb = set(a), set(b)
    only_a = sorted(sa - sb)
    only_b = sorted(sb - sa)
    both = sorted(sa & sb)
    return only_a, only_b, both


def render(base_dir, var_dir):
    _, base_ws = load_ws(base_dir)
    _, var_ws = load_ws(var_dir)
    if not base_ws or not var_ws:
        raise SystemExit('未能加载两个包的 .ws')

    L = []
    L.append(f"# 结构化 diff: `{var_dir.name}` vs `{base_dir.name}`\n")
    L.append(f"> 由 `scripts/ref_diff.py` 生成。")
    L.append("")

    # §1 props2 vars
    bv, be = extract_props2(base_ws)
    vv, ve = extract_props2(var_ws)
    only_b, only_v, both = diff_sets(bv, vv, 'base', 'variant')
    L.append("## §1 props2 变量差异\n")
    L.append(f"- base 独有（{len(only_b)}）: `{', '.join(only_b) or '-'}`")
    L.append(f"- variant 独有（{len(only_v)}）: `{', '.join(only_v) or '-'}`")
    L.append(f"- 共有: {len(both)} 个\n")

    # §2 #EVENT
    only_be, only_ve, both_e = diff_sets(be, ve, 'base', 'variant')
    L.append("## §2 #EVENT 差异\n")
    L.append(f"- base 独有（{len(only_be)}）: `{', '.join(only_be) or '-'}`")
    L.append(f"- variant 独有（{len(only_ve)}）: `{', '.join(only_ve) or '-'}`")
    L.append(f"- 共有: {len(both_e)} 个\n")

    # §3 handlers
    bh = extract_handlers(base_ws)
    vh = extract_handlers(var_ws)
    only_bh, only_vh, both_h = diff_sets(bh.keys(), vh.keys(), 'base', 'variant')
    L.append("## §3 WhenReceiveMessage handlers 差异\n")
    L.append(f"- base 独有 handler（{len(only_bh)}）: `{', '.join(only_bh) or '-'}`")
    L.append(f"- variant 独有 handler（{len(only_vh)}）: `{', '.join(only_vh) or '-'}`")
    # 共有但内容不同
    changed = []
    for m in both_h:
        b_defs = sorted(['|'.join(x) for x in bh.get(m, [])])
        v_defs = sorted(['|'.join(x) for x in vh.get(m, [])])
        if b_defs != v_defs:
            changed.append(m)
    L.append(f"- 共有 {len(both_h)} 个；其中 {len(changed)} 个内容差异：`{', '.join(changed) or '-'}`\n")

    # §4 scene children
    bc = extract_scene_children(base_ws)
    vc = extract_scene_children(var_ws)
    b_sig = {(c['type'], c['name']) for c in bc}
    v_sig = {(c['type'], c['name']) for c in vc}
    only_bc = sorted(b_sig - v_sig)
    only_vc = sorted(v_sig - b_sig)
    L.append("## §4 场景顶层 children 差异（(type, name) 配对）\n")
    L.append(f"- base 独有（{len(only_bc)}）:")
    for t, n in only_bc:
        L.append(f"  - `{t}` / `{n}`")
    L.append(f"- variant 独有（{len(only_vc)}）:")
    for t, n in only_vc:
        L.append(f"  - `{t}` / `{n}`")
    L.append("")

    # §5 fragments hat signatures
    bf = extract_fragments(base_ws)
    vf = extract_fragments(var_ws)
    b_tags = [f"{f['parent']}::{f['tag']}" for f in bf]
    v_tags = [f"{f['parent']}::{f['tag']}" for f in vf]
    only_bt, only_vt, both_t = diff_sets(b_tags, v_tags, 'base', 'variant')
    L.append("## §5 BlockScript fragments hat 差异（parent::hat）\n")
    L.append(f"- base 独有 hat（{len(only_bt)}）:")
    for t in only_bt[:30]:
        L.append(f"  - `{t}`")
    if len(only_bt) > 30:
        L.append(f"  - ...+{len(only_bt)-30}")
    L.append(f"- variant 独有 hat（{len(only_vt)}）:")
    for t in only_vt[:30]:
        L.append(f"  - `{t}`")
    if len(only_vt) > 30:
        L.append(f"  - ...+{len(only_vt)-30}")
    L.append(f"- 共有 hat: {len(both_t)} 条\n")

    # §6 broadcast sequences 差异（按 parent+tag）
    bs = extract_broadcast_sequences(base_ws)
    vs = extract_broadcast_sequences(var_ws)
    b_map = {f"{s['parent']}::{s['tag']}": s['sequence'] for s in bs}
    v_map = {f"{s['parent']}::{s['tag']}": s['sequence'] for s in vs}
    L.append("## §6 Broadcast 序列差异（同一 hat 下序列不同）\n")
    diff_any = False
    for k in sorted(set(b_map) & set(v_map)):
        if b_map[k] != v_map[k]:
            diff_any = True
            L.append(f"- **{k}**")
            L.append(f"   - base:    `{' → '.join(b_map[k]) or '(空)'}`")
            L.append(f"   - variant: `{' → '.join(v_map[k]) or '(空)'}`")
    if not diff_any:
        L.append("所有共有 hat 下 Broadcast 序列完全一致。")

    return '\n'.join(L)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('base')
    p.add_argument('variant')
    p.add_argument('--save', action='store_true', help='写入 <variant>/_diff_vs_<base>.md')
    args = p.parse_args()

    base = Path(args.base).resolve()
    variant = Path(args.variant).resolve()
    md = render(base, variant)
    if args.save:
        out = variant / f'_diff_vs_{base.name}.md'
        out.write_text(md, encoding='utf-8')
        print(f'[diff] wrote {out}')
    else:
        print(md)


if __name__ == '__main__':
    main()
