import sys, json
sys.stdout.reconfigure(encoding='utf-8')

ws_path = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1_workdir\55457a4f-886a-4f76-b0ce-fbed8c682ea1.ws'
with open(ws_path, encoding='utf-8') as f:
    ws = json.load(f)

# Find ALL SetVar and ListReplaceItemAt blocks across the entire ws
results = []

def scan_block(block, path=''):
    if not isinstance(block, dict):
        return
    d = block.get('define', '')
    secs = block.get('sections', [])
    params = secs[0].get('params', []) if secs else []
    if d in ('SetVar', 'ListReplaceItemAt', 'IncVar'):
        p0 = params[0].get('val', '') if params and isinstance(params[0], dict) else ''
        p1 = json.dumps(params[1], ensure_ascii=False) if len(params) > 1 else ''
        p2 = json.dumps(params[2], ensure_ascii=False) if len(params) > 2 else ''
        results.append((path, d, p0, p1, p2))
    
    for sec in secs:
        for child in sec.get('children', []):
            scan_block(child, path + f'/{d}()')

def scan_fragment(frag, frag_path=''):
    scan_block(frag.get('head', {}), frag_path)

def scan_node(node, path=''):
    frags = node.get('fragments', [])
    for i, frag in enumerate(frags):
        head = frag.get('head', {})
        d = head.get('define', '')
        secs = head.get('sections', [])
        msg = ''
        if d == 'WhenReceiveMessage' and secs and secs[0].get('params'):
            p = secs[0]['params'][0]
            msg = f"({p.get('val','')})" if isinstance(p, dict) else ''
        scan_fragment(frag, f'{path}[{i}]{d}{msg}')
    for child in node.get('children', []):
        cname = child.get('props', {}).get('Name', '?')
        scan_node(child, f'{path}/{cname}')

scene = ws['scene']
scan_node(scene)

print('=== All SetVar/IncVar/ListReplaceItemAt ===')
for path, d, p0, p1, p2 in results:
    print(f'{d}({p0}, {p1[:40]}, {p2[:40]})  @  {path}')

print('\n=== Just z-related ===')
for path, d, p0, p1, p2 in results:
    if p0 == 'z' or 'z' in p1:
        print(f'{d}({p0}, {p1[:60]}, {p2[:40]})  @  {path}')
