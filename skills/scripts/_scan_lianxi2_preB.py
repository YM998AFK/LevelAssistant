import sys, json
sys.stdout.reconfigure(encoding='utf-8')

ws_path = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1_workdir\55457a4f-886a-4f76-b0ce-fbed8c682ea1.ws'
with open(ws_path, encoding='utf-8') as f:
    ws = json.load(f)

# Find all blocks that reference cout_cut, 显示L,R, and the full 运行 handler
scene = ws['scene']

def search_var_usage(block, var_name, path=''):
    results = []
    if not isinstance(block, dict):
        return results
    d = block.get('define', '')
    secs = block.get('sections', [])
    params = secs[0].get('params', []) if secs else []
    
    # Check if any param references the variable
    for p in params:
        if isinstance(p, dict):
            pstr = json.dumps(p, ensure_ascii=False)
            if var_name in pstr:
                results.append((path, d, pstr[:100]))
    
    for sec in secs:
        for child in sec.get('children', []):
            results.extend(search_var_usage(child, var_name, path+'/'))
    return results

def scan_node_for_var(node, var_name, path=''):
    results = []
    frags = node.get('fragments', [])
    for i, frag in enumerate(frags):
        head = frag.get('head', {})
        d = head.get('define', '')
        secs = head.get('sections', [])
        msg = ''
        if d == 'WhenReceiveMessage' and secs and secs[0].get('params'):
            p = secs[0]['params'][0]
            msg = f"({p.get('val','')})" if isinstance(p, dict) else ''
        r = search_var_usage(head, var_name, f'{path}[{i}]{d}{msg}')
        results.extend(r)
    for child in node.get('children', []):
        cname = child.get('props', {}).get('Name', '?')
        results.extend(scan_node_for_var(child, var_name, f'{path}/{cname}'))
    return results

print('=== cout_cut usage ===')
for r in scan_node_for_var(scene, 'cout_cut'):
    print(f'  {r}')

print('\n=== 显示L,R handler ===')
kongzhi_frags = scene['children'][6]['children'][0]['fragments']
# Find 显示L,R  
for i, frag in enumerate(kongzhi_frags):
    head = frag['head']
    d = head.get('define','')
    secs = head.get('sections', [])
    if d == 'WhenReceiveMessage' and secs and secs[0].get('params'):
        msg = secs[0]['params'][0].get('val', '')
        if '显示' in msg or 'L' in msg:
            print(f'Found handler [{i}] {msg}')
            print(json.dumps(head, ensure_ascii=False, indent=2)[:1000])

# Also look for any handler with 显示 or cout_cut reference in all frags
print('\n=== All frags with cout_cut reference ===')
top_frags = scene['children'][1]['fragments']
for i, frag in enumerate(top_frags):
    head_str = json.dumps(frag['head'], ensure_ascii=False)
    if 'cout_cut' in head_str or '显示' in head_str:
        print(f'top[{i}]: {head_str[:200]}')
