"""扫描 15-2 题组1 的两个母本（挑战2 / 挑战3）。"""
import json, re, sys
from pathlib import Path

ROOT = Path(r'c:\Users\Hetao\Desktop\公司\参考-extracted')

LEVELS = {
    '挑战2': ROOT / '挑战2' / '1bea6453-32ce-487e-9b13-61ecfc30d634.ws',
    '挑战3': ROOT / '挑战3' / 'a40f5060-698d-46ea-8cae-7aff6e11c780.ws',
}

EVENT_HATS = {'WhenGameStarts', 'WhenStartup', 'WhenReceiveMessage',
              'WhenClick', 'WhenKeyPressed', 'Trigger',
              'WhenThisSpriteClicked', 'OnMessage', 'OnCollide'}


def load(p):
    return json.load(open(p, encoding='utf-8'))


def walk(node, cb, path=''):
    if isinstance(node, dict):
        cb(node, path)
        for k, v in node.items():
            walk(v, cb, path + '/' + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, cb, path + f'[{i}]')


def collect_broadcasts(data):
    msgs = set()
    def cb(n, p):
        if not isinstance(n, dict): return
        if n.get('define') in ('BroadcastMessage', 'BroadcastMessageAndWait'):
            ps = n.get('sections', [{}])[0].get('params', [])
            if ps and ps[0].get('type') == 'var':
                msgs.add(ps[0].get('val'))
    walk(data, cb)
    return msgs


def collect_setvars(data):
    out = []
    def cb(n, p):
        if not isinstance(n, dict): return
        if n.get('define') == 'SetVar':
            ps = n.get('sections', [{}])[0].get('params', [])
            if len(ps) >= 2 and ps[0].get('type') == 'var':
                out.append((p, ps[0].get('val'), ps[1].get('val') if ps[1].get('type')=='var' else '[block]'))
    walk(data, cb)
    return out


def dump_summary(name, path):
    d = load(path)
    s = d['scene']
    print(f"\n{'='*60}\n{name}  ws={path.name}  file_bytes={path.stat().st_size}")
    print(f"scene.props2 vars: {list((s.get('props2') or {}).keys())}")
    # Event registry
    print(f"#EVENT: {(s.get('props2') or {}).get('#EVENT', {}).get('value')}")
    # Scene tree top-level
    print(f"\nscene children [{len(s.get('children',[]))}]:")
    for i, c in enumerate(s.get('children', [])):
        nm = (c.get('props') or {}).get('Name', '?')
        t = c.get('type')
        vis = (c.get('props') or {}).get('Visible', '-')
        pos = (c.get('props') or {}).get('Position', '')
        aid = (c.get('props') or {}).get('AssetId', '-')
        # inner fragment count?
        frags = 0
        if c.get('children'):
            for cc in c['children']:
                if cc.get('type') == 'BlockScript':
                    frags += len(cc.get('fragments', []))
        extra = ''
        if c.get('fragments'):
            frags += len(c.get('fragments'))
        if frags:
            extra = f'  fragments={frags}'
        print(f"  [{i:>2}] {t:<12} {str(nm)[:22]:<22} Asset={aid!s:<6} Visible={vis!s:<6} Pos={pos}{extra}")
    # Broadcasts used
    bcs = collect_broadcasts(d)
    print(f"\nBroadcasts sent (set): {sorted(bcs)}")
    # Find all WhenReceiveMessage names
    handlers = set()
    def collect_handlers(n, p):
        if isinstance(n, dict) and n.get('define') == 'WhenReceiveMessage':
            ps = n.get('sections', [{}])[0].get('params', [])
            if ps and ps[0].get('type') == 'var':
                handlers.add(ps[0].get('val'))
    walk(d, collect_handlers)
    print(f"WhenReceiveMessage handlers: {sorted(handlers)}")
    orphan_msgs = handlers - bcs
    print(f"  -> Handlers never broadcast (candidate B1/B2): {sorted(orphan_msgs)}")
    extra_bcs = bcs - handlers
    print(f"  -> Broadcasts with no handler on same node-ish: {sorted(extra_bcs)}")

    # cid-like vars
    setv = collect_setvars(d)
    interesting = [x for x in setv if x[1] in ('cid','mode','cut_n','i','n')]
    print(f"\nSetVar on control vars (cid/mode/i/n):")
    for p, k, v in interesting:
        print(f"  {k:<8} = {v!r:<8} at {p[:90]}")
    # Mode detection
    is_cloud = '参数注入' in bcs
    has_candidate = '参数注入' in handlers
    print(f"\n运行模式推断: 云编译={is_cloud} / 存在候补(参数注入 hat)={has_candidate}")
    if not is_cloud and not has_candidate:
        print("  -> 判定: OJ 模式")
    elif is_cloud:
        print("  -> 判定: 云编译")
    else:
        print("  -> 判定: 疑似 OJ，但含未激活候补")


for name, p in LEVELS.items():
    dump_summary(name, p)

# diff overview
print(f"\n{'='*60}\nTop-level diff (挑战2 vs 挑战3)")
d2 = load(LEVELS['挑战2'])
d3 = load(LEVELS['挑战3'])
for k in sorted(set(d2.keys()) | set(d3.keys())):
    a = json.dumps(d2.get(k), ensure_ascii=False, sort_keys=True)
    b = json.dumps(d3.get(k), ensure_ascii=False, sort_keys=True)
    if a != b:
        print(f"  != {k}  (len2={len(a)}, len3={len(b)})")

print("\nscene.children structural diff:")
c2 = {c.get('id',''): c for c in d2['scene']['children']}
c3 = {c.get('id',''): c for c in d3['scene']['children']}
print(f"  only in 挑战2: {len(c2.keys()-c3.keys())}")
print(f"  only in 挑战3: {len(c3.keys()-c2.keys())}")
for i in sorted(c2.keys() & c3.keys()):
    a = json.dumps(c2[i], ensure_ascii=False, sort_keys=True)
    b = json.dumps(c3[i], ensure_ascii=False, sort_keys=True)
    if a != b:
        nm = (c2[i].get('props') or {}).get('Name', '?')
        print(f"  != {c2[i].get('type')} / {nm}  len2={len(a)} len3={len(b)}")
