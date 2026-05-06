"""ref_scan.py — 单个参考包分析器

对一个 参考-extracted/<pack>/ 目录（含 *.ws），生成 <pack>/_analysis.md。

用法:
    python scripts/ref_scan.py <pack_dir>
    python scripts/ref_scan.py <pack_dir> --json           # 额外输出 _analysis.json
    python scripts/ref_scan.py 参考-extracted/挑战2        # 也接受相对路径
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


# ============================================================
# JSON 走廊：遍历 .ws 的积木树
# ============================================================

def walk_blocks(node, cb):
    """对每个 block-like dict（含 define/sections）调用 cb(block)。"""
    if isinstance(node, dict):
        if 'define' in node:
            cb(node)
        for v in node.values():
            walk_blocks(v, cb)
    elif isinstance(node, list):
        for v in node:
            walk_blocks(v, cb)


def find_child_blocks(block):
    """返回 block.sections[*].children 里的所有 block。"""
    out = []
    if not isinstance(block, dict):
        return out
    for sec in (block.get('sections') or []):
        for c in (sec.get('children') or []):
            if isinstance(c, dict):
                out.append(c)
    return out


def block_first_string_arg(block):
    """取 block.sections[0].params[0] 的字符串（若是 var 类型）。"""
    if not isinstance(block, dict):
        return None
    secs = block.get('sections') or []
    if not secs:
        return None
    params = secs[0].get('params') or []
    for p in params:
        if isinstance(p, dict) and p.get('type') == 'var':
            return p.get('val')
    return None


# ============================================================
# 特征提取
# ============================================================

def extract_props2(ws):
    p2 = (ws.get('scene') or {}).get('props2') or {}
    vars_ = list(p2.keys())
    events = (p2.get('#EVENT') or {}).get('value') or []
    return vars_, list(events)


def extract_scene_children(ws):
    """返回 scene.children 的扁平摘要。"""
    scn = ws.get('scene') or {}
    out = []
    for c in scn.get('children', []):
        t = c.get('type', '?')
        props = c.get('props') or {}
        name = props.get('Name', '?')
        asset = props.get('AssetId', '-')
        vis = props.get('Visible', '-')
        pos = props.get('Position', '')
        # 子节点 fragments 计数
        frag_cnt = 0
        for cc in c.get('children', []) or []:
            frag_cnt += len(cc.get('fragments') or [])
        frag_cnt += len(c.get('fragments') or [])
        out.append({
            'type': t, 'name': name, 'asset': str(asset),
            'visible': vis, 'position': pos, 'fragments': frag_cnt,
        })
    return out


def extract_fragments(ws):
    """返回所有 BlockScript 的 fragments，标注 hat 和父节点名。"""
    out = []

    def walk_bs(bs, parent_name):
        for frag in (bs.get('fragments') or []):
            head = frag.get('head') or {}
            hat = head.get('define', '?')
            hat_arg = block_first_string_arg(head)
            tag = f"{hat}('{hat_arg}')" if hat_arg else hat
            out.append({
                'parent': parent_name, 'hat': hat, 'hat_arg': hat_arg,
                'tag': tag, 'head': head,
            })

    def walk_node(node, name='?'):
        if isinstance(node, dict):
            nm = (node.get('props') or {}).get('Name', name)
            if node.get('type') == 'BlockScript':
                walk_bs(node, name)
            if node.get('fragments') and node.get('type') != 'BlockScript':
                walk_bs(node, name)
            for v in node.values():
                walk_node(v, nm)
        elif isinstance(node, list):
            for v in node:
                walk_node(v, name)

    walk_node(ws.get('scene'))
    return out


def collect_broadcasts_in(block):
    """在一个 block 的 children 里按出现顺序收集 Broadcast 的消息名。"""
    out = []
    def rec(b):
        if not isinstance(b, dict):
            return
        if b.get('define') in ('BroadcastMessage', 'BroadcastMessageAndWait'):
            msg = block_first_string_arg(b)
            if msg is not None:
                out.append(msg)
        for sec in (b.get('sections') or []):
            for c in (sec.get('children') or []):
                rec(c)
    rec(block)
    return out


def extract_broadcast_sequences(ws):
    """按 fragment 收集 Broadcast 序列。"""
    seqs = []
    for f in extract_fragments(ws):
        seq = collect_broadcasts_in(f['head'])
        if seq:
            seqs.append({
                'parent': f['parent'], 'tag': f['tag'], 'sequence': seq,
            })
    return seqs


def extract_handlers(ws):
    """所有 WhenReceiveMessage('msg') 的 handler，返回 msg→[top-level child defines]。"""
    handlers = defaultdict(list)

    def cb(b):
        if b.get('define') == 'WhenReceiveMessage':
            msg = block_first_string_arg(b)
            kids = find_child_blocks(b)
            handlers[msg].append([k.get('define', '?') for k in kids])

    walk_blocks(ws, cb)
    return dict(handlers)


def extract_hats_summary(ws):
    """统计每种 hat 的出现次数。"""
    c = defaultdict(int)
    for f in extract_fragments(ws):
        c[f['hat']] += 1
    return dict(c)


def extract_playanims(ws):
    """所有 PlayAnimation/PlayAnimationUntil 调用的 (target, animName)。"""
    out = []
    def cb(b):
        if b.get('define') not in ('PlayAnimation', 'PlayAnimationUntil', 'StopAnimation'):
            return
        names = []
        for sec in (b.get('sections') or []):
            for p in (sec.get('params') or []):
                if isinstance(p, dict) and p.get('type') == 'var':
                    names.append(p.get('val'))
        out.append({'define': b.get('define'), 'args': names})
    walk_blocks(ws, cb)
    return out


def extract_setvars(ws):
    """所有 SetVar 调用，返回 (var, value 或 '[block]')。"""
    out = []
    def cb(b):
        if b.get('define') != 'SetVar':
            return
        secs = b.get('sections') or [{}]
        ps = secs[0].get('params') or []
        if len(ps) < 2: return
        vp, xp = ps[0], ps[1]
        if not (isinstance(vp, dict) and vp.get('type') == 'var'):
            return
        key = vp.get('val')
        if isinstance(xp, dict):
            if xp.get('type') == 'var':
                val = xp.get('val')
            elif xp.get('type') == 'block':
                val = '[block]'
            else:
                val = '?'
        else:
            val = '?'
        out.append((key, val))
    walk_blocks(ws, cb)
    return out


# ============================================================
# 模板族推断
# ============================================================

TEMPLATE_FAMILIES = [
    ('F.tree',    {'机器人左转', '机器人右转', '生成成长树', '机器人发射'},
     '成长树 / 计数机器人'),
    ('F.sundial', {'打开日晷', '开启测算', '测算输入', '周期循环', '长老验算'},
     '日晷测算'),
    ('F.beast',   {'鸡狗对打', '鸡狗大战', '机械狗被伤', '机械狗加血', '机械狗格档'},
     '机械兽对打'),
    ('F.nonstd',  {'判断是否输入', '判断输入数据范围', '能否运行'},
     '非标准 OJ 架（反例）'),
]


def infer_family(events):
    ev = set(events)
    hits = []
    for code, markers, desc in TEMPLATE_FAMILIES:
        matched = markers & ev
        if matched:
            hits.append({'code': code, 'desc': desc,
                         'matched_markers': sorted(matched),
                         'score': f"{len(matched)}/{len(markers)}"})
    return hits


def infer_mode(events, handlers):
    """粗判：OJ / 云编 / 对白 / 其他。"""
    ev = set(events)
    hd = set(handlers.keys())
    if {'cin判断', 'cout判断'} & ev and {'cin判断', 'cout判断'} & hd:
        return 'OJ（标准）'
    if {'判断是否输入', '判断输入数据范围'} & ev:
        return 'OJ（非标准 F.nonstd）'
    if '参数注入' in ev:
        return '云编译'
    if '运行' in ev and '传递成功' in ev and '传递失败' in ev:
        return 'OJ-like（有骨架但判题 handler 缺失）'
    return '未知/对白'


# ============================================================
# 打分：OJ 标准骨架符合度
# ============================================================

L0_VARS = {'#EVENT', '*OJ-Judge', '*OJ-执行结果', '*OJ-输入信息',
           'cin_cut', 'cmd', 'cout_cut', 'n', 'space-flag',
           'variable', '输入元素', '输出元素'}
L0_EVENTS = {'CMD_NewMessage', 'judge', '传递失败', '传递成功', '初始化', '运行'}
L1_EVENTS = {'cin判断', 'cout判断'}


def oj_skeleton_score(vars_, events, handlers):
    ev = set(events)
    hd = set(handlers.keys())
    vset = set(vars_)
    return {
        'L0_vars':        sorted(L0_VARS & vset),
        'L0_vars_missing':sorted(L0_VARS - vset),
        'L0_events':      sorted(L0_EVENTS & ev),
        'L0_events_missing': sorted(L0_EVENTS - ev),
        'L1_events':      sorted(L1_EVENTS & ev),
        'L1_events_missing': sorted(L1_EVENTS - ev),
        'L0_vars_ratio':  f"{len(L0_VARS & vset)}/{len(L0_VARS)}",
        'L0_events_ratio':f"{len(L0_EVENTS & ev)}/{len(L0_EVENTS)}",
    }


# ============================================================
# 写入 _analysis.md
# ============================================================

def render(pack_dir, ws_path, ws):
    vars_, events = extract_props2(ws)
    children = extract_scene_children(ws)
    fragments = extract_fragments(ws)
    seqs = extract_broadcast_sequences(ws)
    handlers = extract_handlers(ws)
    hats = extract_hats_summary(ws)
    anims = extract_playanims(ws)
    setvars = extract_setvars(ws)

    family = infer_family(events)
    mode = infer_mode(events, handlers)
    skel = oj_skeleton_score(vars_, events, handlers)

    # solution.json 元数据
    sol = pack_dir / 'solution.json'
    sol_meta = {}
    if sol.exists():
        try:
            sd = json.load(open(sol, encoding='utf-8'))
            for k in ('name', 'uuid', 'id', 'mode', 'type'):
                if k in sd:
                    sol_meta[k] = sd[k]
        except Exception:
            pass

    L = []
    L.append(f"# {pack_dir.name} · 结构分析\n")
    L.append(f"> 由 `scripts/ref_scan.py` 生成，用于建立跨包语料库。\n")
    L.append("")
    L.append("## 元数据\n")
    L.append(f"- **包目录**：`{pack_dir}`")
    L.append(f"- **ws 文件**：`{ws_path.name}`（{ws_path.stat().st_size:,} bytes）")
    if sol_meta:
        for k, v in sol_meta.items():
            L.append(f"- **solution.{k}**：{v}")
    L.append(f"- **运行模式推断**：{mode}")
    if family:
        for f in family:
            L.append(f"- **模板族匹配**：`{f['code']}`  {f['desc']}  ({f['score']})  命中: {f['matched_markers']}")
    else:
        L.append(f"- **模板族匹配**：未命中已知族（可能新族候选）")
    L.append("")

    L.append("## OJ 骨架符合度\n")
    L.append(f"- **L0 变量覆盖**：{skel['L0_vars_ratio']}")
    if skel['L0_vars_missing']:
        L.append(f"  - ⚠️ 缺失：{skel['L0_vars_missing']}")
    L.append(f"- **L0 消息覆盖**：{skel['L0_events_ratio']}")
    if skel['L0_events_missing']:
        L.append(f"  - ⚠️ 缺失：{skel['L0_events_missing']}")
    L.append(f"- **L1 判题消息**：有 {skel['L1_events']}；缺 {skel['L1_events_missing']}")
    L.append("")

    L.append("## 场景树（顶层 children）\n")
    L.append("| # | type | name | Asset | Visible | fragments | Position |")
    L.append("|---|---|---|---|---|---|---|")
    for i, c in enumerate(children):
        L.append(f"| {i} | {c['type']} | `{c['name']}` | {c['asset']} | {c['visible']} | {c['fragments']} | `{c['position']}` |")
    L.append("")

    L.append("## props2 变量\n")
    L.append(f"共 {len(vars_)} 个：`{', '.join(vars_)}`\n")

    L.append("## #EVENT 消息\n")
    L.append(f"共 {len(events)} 个：`{', '.join(events)}`\n")

    L.append("## Hat 汇总（fragments 分类）\n")
    L.append("| Hat | 次数 |")
    L.append("|---|---|")
    for hat, cnt in sorted(hats.items(), key=lambda x: -x[1]):
        L.append(f"| {hat} | {cnt} |")
    L.append("")

    L.append("## BlockScript Fragments（按 hat 展开的 Broadcast 序列）\n")
    for i, s in enumerate(seqs):
        seq_s = ' → '.join(s['sequence'])
        L.append(f"- **[{i}] {s['parent']} / {s['tag']}**  `{seq_s}`")
    if not seqs:
        L.append("_无 Broadcast 调用_")
    L.append("")

    L.append("## WhenReceiveMessage Handlers\n")
    L.append("| 消息 | handler 条数 | 首条顶层 children defines |")
    L.append("|---|---|---|")
    for msg in sorted(handlers.keys(), key=lambda x: (x or '')):
        hlist = handlers[msg]
        top = hlist[0][:6] if hlist else []
        dots = '...' if (hlist and len(hlist[0]) > 6) else ''
        L.append(f"| `{msg}` | {len(hlist)} | {top}{dots} |")
    L.append("")

    L.append("## PlayAnimation 调用\n")
    if anims:
        anim_count = defaultdict(int)
        for a in anims:
            key = tuple(a['args'][:2]) if len(a['args']) >= 2 else tuple(a['args'])
            anim_count[(a['define'], key)] += 1
        L.append("| 调用类型 | 角色 | 动画名 | 次数 |")
        L.append("|---|---|---|---|")
        for (define, key), cnt in sorted(anim_count.items(), key=lambda x: -x[1]):
            role = key[0] if len(key) >= 1 else ''
            name = key[1] if len(key) >= 2 else ''
            L.append(f"| {define} | {role} | {name} | {cnt} |")
    else:
        L.append("_无_")
    L.append("")

    L.append("## SetVar 统计\n")
    sv_count = defaultdict(int)
    for k, v in setvars:
        sv_count[(k, v)] += 1
    L.append(f"共 {len(setvars)} 次 SetVar，去重 {len(sv_count)} 种：\n")
    for (k, v), cnt in sorted(sv_count.items(), key=lambda x: -x[1]):
        L.append(f"- `{k}` = `{v}`  × {cnt}")
    L.append("")

    return '\n'.join(L)


def find_ws(pack_dir: Path):
    for f in pack_dir.iterdir():
        if f.suffix == '.ws':
            return f
    return None


def scan_one(pack_dir: Path, write_json: bool = False):
    pack_dir = pack_dir.resolve()
    ws_path = find_ws(pack_dir)
    if not ws_path:
        return {'ok': False, 'dir': str(pack_dir), 'error': 'no .ws file'}
    try:
        ws = json.load(open(ws_path, encoding='utf-8'))
    except Exception as e:
        return {'ok': False, 'dir': str(pack_dir), 'error': f'ws parse failed: {e}'}

    md = render(pack_dir, ws_path, ws)
    (pack_dir / '_analysis.md').write_text(md, encoding='utf-8')

    if write_json:
        vars_, events = extract_props2(ws)
        payload = {
            'pack': pack_dir.name,
            'ws': ws_path.name,
            'props2_vars': vars_,
            'events': events,
            'family': infer_family(events),
            'mode': infer_mode(events, extract_handlers(ws)),
            'scene_children': extract_scene_children(ws),
            'broadcast_sequences': extract_broadcast_sequences(ws),
            'handlers': {k: [h for h in v] for k, v in extract_handlers(ws).items()},
            'hats': extract_hats_summary(ws),
            'skel_score': oj_skeleton_score(vars_, events, extract_handlers(ws)),
        }
        (pack_dir / '_analysis.json').write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    return {'ok': True, 'dir': str(pack_dir), 'ws': ws_path.name, 'md': str(pack_dir / '_analysis.md')}


def main():
    parser = argparse.ArgumentParser(description='单包结构分析 → _analysis.md')
    parser.add_argument('pack_dir', help='参考包目录（含 .ws 文件）')
    parser.add_argument('--json', action='store_true', help='同时输出 _analysis.json 方便跨包聚合')
    args = parser.parse_args()

    r = scan_one(Path(args.pack_dir), write_json=args.json)
    if r['ok']:
        print(f"[OK  ] {r['dir']}  -> {Path(r['md']).name}")
    else:
        print(f"[FAIL] {r['dir']}  {r['error']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
