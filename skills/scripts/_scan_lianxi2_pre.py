import sys, json
sys.stdout.reconfigure(encoding='utf-8')

ws_path = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1_workdir\55457a4f-886a-4f76-b0ce-fbed8c682ea1.ws'
with open(ws_path, encoding='utf-8') as f:
    ws = json.load(f)

def find_frags(node, path=''):
    results = []
    bs = node.get('BlockScript')
    if bs:
        for i, frag in enumerate(bs.get('fragments', [])):
            hat = frag.get('blocks', [{}])[0] if frag.get('blocks') else {}
            label = frag.get('label', '')
            define = hat.get('define', '')
            params = hat.get('params', [])
            msg = ''
            if define == 'WhenReceiveMessage' and params:
                msg = params[0].get('val', '') if isinstance(params[0], dict) else ''
            results.append((path, i, label, define, msg, frag))
    for child in node.get('children', []):
        results.extend(find_frags(child, path + '/' + child.get('name', '?')))
    return results

scene = ws.get('scene', ws)
all_frags = find_frags(scene)

print('=== 全部 fragments ===')
for path, idx, label, define, msg, frag in all_frags:
    print(f'  {path}[{idx}] {define}({msg}) label={label}')

def print_blocks(blocks, indent=2):
    for b in blocks:
        d = b.get('define', '')
        p = b.get('params', [])
        pstrs = []
        for pp in p:
            if isinstance(pp, dict):
                if pp.get('type') == 'block':
                    inner = pp.get('val', {})
                    pstrs.append(f'[block:{inner.get("define","?")}({",".join(str(x.get("val","")) if isinstance(x,dict) else str(x) for x in inner.get("params",[]))})]')
                else:
                    pstrs.append(str(pp.get('val', '')))
            else:
                pstrs.append(str(pp))
        print(' ' * indent + f'{d}({"|".join(pstrs)})')
        for sec in b.get('sections', []):
            for sub in sec.get('children', []):
                print_blocks([sub], indent + 2)

key_msgs = ['计算速度', '换行', '开始走路', 'judge', '能否运行', '运行']
print('\n=== 关键 handler 详细积木 ===')
for path, idx, label, define, msg, frag in all_frags:
    if msg in key_msgs or (define == 'WhenGameStarts' and '控制台' in path):
        print(f'\n--- {path}[{idx}] {define}({msg}) ---')
        print_blocks(frag.get('blocks', []))

# Also print props2
print('\n=== props2 变量 ===')
props2 = ws.get('scene', ws).get('props2', {})
for k, v in props2.items():
    print(f'  {k}: {json.dumps(v, ensure_ascii=False)[:80]}')
