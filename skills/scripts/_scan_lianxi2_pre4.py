import sys, json
sys.stdout.reconfigure(encoding='utf-8')

ws_path = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1_workdir\55457a4f-886a-4f76-b0ce-fbed8c682ea1.ws'
with open(ws_path, encoding='utf-8') as f:
    ws = json.load(f)

scene = ws['scene']

def find_all_frags(node, path=''):
    results = []
    frags = node.get('fragments', [])
    for i, frag in enumerate(frags):
        head = frag.get('head', {})
        results.append((path, i, frag, head))
    for child in node.get('children', []):
        cname = child.get('props', {}).get('Name', child.get('name', '?'))
        results.extend(find_all_frags(child, path + '/' + cname))
    return results

all_frags = find_all_frags(scene)

def get_hat_msg(head):
    """Get message name for WhenReceiveMessage hat (in sections[0].params[0].val)"""
    define = head.get('define', '')
    if define == 'WhenReceiveMessage':
        secs = head.get('sections', [])
        if secs and secs[0].get('params'):
            p = secs[0]['params'][0]
            if isinstance(p, dict):
                return define, p.get('val', '')
    return define, ''

def fmt_param(p, depth=0):
    if isinstance(p, dict):
        if p.get('type') == 'block':
            inner = p.get('val', {})
            if isinstance(inner, dict):
                d = inner.get('define', '?')
                secs = inner.get('sections', [])
                iparams = secs[0].get('params', []) if secs else []
                ipstrs = [fmt_param(ip, depth+1) for ip in iparams]
                return f'[{d}({",".join(ipstrs)})]'
        return str(p.get('val', ''))
    return str(p)

def print_block(block, indent=0, max_depth=8):
    if not isinstance(block, dict) or indent > max_depth * 2:
        return
    define = block.get('define', '')
    secs = block.get('sections', [])
    
    # Get params from first section
    main_params = secs[0].get('params', []) if secs else []
    pstrs = [fmt_param(p) for p in main_params]
    
    print(' ' * indent + f'{define}({"|".join(pstrs)})')
    
    # Print children sections
    for sec_i, sec in enumerate(secs):
        children = sec.get('children', [])
        if children:
            if len(secs) > 1:
                pass  # could print section label
            for child in children:
                print_block(child, indent + 2, max_depth)

key_msgs = ['计算速度', '换行', '开始走路', 'judge', '能否运行', '运行']

print('=== 关键 handler 详细积木 ===')
for path, idx, frag, head in all_frags:
    define, msg = get_hat_msg(head)
    if msg in key_msgs or (define == 'WhenGameStarts' and '控制台' in path):
        print(f'\n--- {path}[{idx}] {define}({msg}) ---')
        # Print hat
        print_block(head)

# Now print all fragments with correct message names
print('\n=== 全部 fragments (带正确消息名) ===')
for path, idx, frag, head in all_frags:
    define, msg = get_hat_msg(head)
    print(f'  {path}[{idx}] {define}({msg})')
