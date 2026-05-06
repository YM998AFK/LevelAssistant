"""Batch-scan D-phase MVP 参考包，跨包聚合 OJ 骨架。写 utf-8 md。"""
import json, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(r'c:\Users\Hetao\Desktop\公司\参考-extracted')

MVP = [
    '挑战2',
    '挑战3',
    '练习5',
    '练习7',
    '低16-2 练习2',
    '挑战9-教师端',
]


def find_ws(pack_dir):
    for f in pack_dir.iterdir():
        if f.suffix == '.ws':
            return f
    return None


def extract_broadcast_sequences(ws):
    results = []
    def collect_seq(block, out):
        if not isinstance(block, dict):
            return
        if block.get('define') in ('BroadcastMessage', 'BroadcastMessageAndWait'):
            for sec in (block.get('sections') or []):
                for p in (sec.get('params') or []):
                    if isinstance(p, dict) and p.get('type') == 'var':
                        out.append(p.get('val')); break
        for sec in (block.get('sections') or []):
            for c in (sec.get('children') or []):
                collect_seq(c, out)

    def walk_bs(bs):
        for frag in bs.get('fragments', []):
            head = frag.get('head') or {}
            hat = head.get('define', '?')
            hat_arg = ''
            for sec in (head.get('sections') or []):
                for p in (sec.get('params') or []):
                    if isinstance(p, dict) and p.get('type') == 'var':
                        hat_arg = p.get('val'); break
                break
            tag = f"{hat}('{hat_arg}')" if hat_arg else hat
            seq = []
            collect_seq(head, seq)
            if seq:
                results.append((tag, seq))

    def find_bs(node):
        if isinstance(node, dict):
            if node.get('type') == 'BlockScript':
                walk_bs(node)
            if node.get('fragments') and node.get('type') != 'BlockScript':
                walk_bs(node)
            for v in node.values():
                find_bs(v)
        elif isinstance(node, list):
            for v in node:
                find_bs(v)
    find_bs(ws)
    return results


def extract_handlers(ws):
    out = []
    def walk(node):
        if isinstance(node, dict):
            if node.get('define') == 'WhenReceiveMessage':
                msg = None; kids = []
                for sec in (node.get('sections') or []):
                    for p in (sec.get('params') or []):
                        if isinstance(p, dict) and p.get('type') == 'var':
                            msg = p.get('val')
                    for c in (sec.get('children') or []):
                        kids.append(c.get('define', '?'))
                out.append((msg, kids))
            for v in node.values(): walk(v)
        elif isinstance(node, list):
            for v in node: walk(v)
    walk(ws)
    return out


def extract_props2(ws):
    p2 = (ws.get('scene') or {}).get('props2') or {}
    vars_ = list(p2.keys())
    events = (p2.get('#EVENT') or {}).get('value') or []
    return vars_, events


def extract_uis(ws):
    scn = ws.get('scene') or {}
    out = []
    for c in scn.get('children', []):
        if c.get('type') in ('UIView', 'ImageSet'):
            nm = (c.get('props') or {}).get('Name', '?')
            pos = (c.get('props') or {}).get('Position', '')
            vis = (c.get('props') or {}).get('Visible', '-')
            out.append((c['type'], nm, vis, pos))
    return out


def per_pack(name):
    pd = ROOT / name
    ws_path = find_ws(pd)
    if not ws_path:
        return None
    d = json.load(open(ws_path, encoding='utf-8'))
    return {
        'name': name, 'ws': ws_path.name,
        'props2': extract_props2(d),
        'seqs': extract_broadcast_sequences(d),
        'handlers': extract_handlers(d),
        'uis': extract_uis(d),
    }


def main():
    packs = {}
    for n in MVP:
        r = per_pack(n)
        if r is None:
            sys.stderr.write(f"[WARN] not found: {n}\n"); continue
        packs[n] = r

    lines = ["# MVP scan report", ""]
    names = list(packs.keys())

    lines.append("## 1. 每包规模\n")
    lines.append("| 包 | ws | props2 | #EVENT | fragments | handlers | UI | ")
    lines.append("|---|---|---|---|---|---|---|")
    for n, r in packs.items():
        lines.append(f"| {n} | {r['ws'][:8]}… | {len(r['props2'][0])} | {len(r['props2'][1])} | {len(r['seqs'])} | {len(r['handlers'])} | {len(r['uis'])} |")

    lines.append("\n## 2. props2 变量共现\n")
    all_vars = sorted({v for r in packs.values() for v in r['props2'][0]})
    lines.append("| 变量 | " + ' | '.join(names) + " | 共现 |")
    lines.append('|---' * (len(names)+2) + '|')
    shared_vars = []
    for v in all_vars:
        row = [v]; cnt = 0
        for n in names:
            has = v in packs[n]['props2'][0]
            row.append('●' if has else '')
            if has: cnt += 1
        row.append(str(cnt))
        if cnt == len(packs):
            shared_vars.append(v)
        lines.append('| ' + ' | '.join(row) + ' |')
    lines.append(f"\n**全部 {len(packs)} 包都有的变量（骨架必需候选）**：`{', '.join(shared_vars)}`")

    lines.append("\n## 3. #EVENT 消息共现\n")
    all_evs = sorted({e for r in packs.values() for e in r['props2'][1]})
    lines.append("| 消息 | " + ' | '.join(names) + " | 共现 |")
    lines.append('|---' * (len(names)+2) + '|')
    shared_evs = []
    for e in all_evs:
        row = [e]; cnt = 0
        for n in names:
            has = e in packs[n]['props2'][1]
            row.append('●' if has else '')
            if has: cnt += 1
        row.append(str(cnt))
        if cnt == len(packs): shared_evs.append(e)
        lines.append('| ' + ' | '.join(row) + ' |')
    lines.append(f"\n**全部 {len(packs)} 包都有的消息（骨架必需候选）**：`{', '.join(shared_evs)}`")

    lines.append("\n## 4. 跨包复现的 Broadcast 子序列（桥段候选）\n")
    all_ng = defaultdict(lambda: defaultdict(int))
    for n, r in packs.items():
        for hat, seq in r['seqs']:
            for k in (3, 4, 5, 6, 7, 8):
                if len(seq) < k: continue
                for i in range(len(seq)-k+1):
                    all_ng[tuple(seq[i:i+k])][n] += 1
    cross = []
    for ng, pm in all_ng.items():
        if len(pm) >= 2:
            cross.append((len(ng), len(pm), sum(pm.values()), ng, dict(pm)))
    cross.sort(key=lambda x: (-x[0], -x[1], -x[2]))
    kept = []
    for item in cross:
        _,_,_, ng, _ = item
        skip = False
        for k_item in kept:
            _,_,_, kng, kpm = k_item
            if len(ng) < len(kng):
                for i in range(len(kng)-len(ng)+1):
                    if kng[i:i+len(ng)] == ng and set(item[4].keys()) == set(kpm.keys()):
                        skip = True; break
            if skip: break
        if not skip:
            kept.append(item)
    lines.append(f"合计 {len(kept)} 个非冗余候选子序列（len>=3, 出现在>=2包）：\n")
    for klen, npacks, total, ng, pm in kept[:60]:
        src = ', '.join(f"{k}×{v}" for k, v in pm.items())
        lines.append(f"- **[L{klen}]×{npacks}包({total}次)**  `{' → '.join(ng)}`  _来源: {src}_")

    lines.append("\n## 5. WhenReceiveMessage 处理器覆盖\n")
    all_msgs = set()
    phm = {}
    for n, r in packs.items():
        mm = {msg: kids for msg, kids in r['handlers']}
        phm[n] = mm
        all_msgs.update(mm.keys())
    lines.append("| 消息 | " + ' | '.join(names) + " |")
    lines.append('|---' * (len(names)+1) + '|')
    for m in sorted(all_msgs, key=lambda x: (x or '')):
        row = [str(m)]
        for n in names:
            row.append('●' if m in phm[n] else '')
        lines.append('| ' + ' | '.join(row) + ' |')

    # 6. UI components
    lines.append("\n## 6. UI 组件（Name, Visible, Position）\n")
    for n, r in packs.items():
        lines.append(f"\n### {n}")
        for t, nm, vis, pos in r['uis']:
            lines.append(f"- {t}  `{nm}`  Visible={vis}  Pos={pos}")

    out_path = Path(r'c:\Users\Hetao\Desktop\公司\scripts\_mvp_scan.md')
    out_path.write_text('\n'.join(lines), encoding='utf-8')
    sys.stderr.write(f"wrote {out_path}  lines={len(lines)}\n")


if __name__ == '__main__':
    main()
