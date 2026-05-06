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

print(f'Total fragments: {len(all_frags)}')

def get_define_msg(head):
    define = head.get('define', '')
    params = head.get('params', [])
    msg = ''
    if define == 'WhenReceiveMessage' and params:
        p = params[0]
        if isinstance(p, dict):
            if p.get('type') == 'block':
                msg = p.get('val', {}).get('params', [{}])[0].get('val', '') if isinstance(p.get('val', {}), dict) else ''
            else:
                msg = p.get('val', '')
        else:
            msg = str(p)
    return define, msg

print('\n=== All fragments ===')
for path, idx, frag, head in all_frags:
    define, msg = get_define_msg(head)
    print(f'  {path}[{idx}] {define}({msg})')

# Show head structure of first few
print('\n=== Sample head structures ===')
for path, idx, frag, head in all_frags[:5]:
    print(f'\n{path}[{idx}]:')
    print(json.dumps(head, ensure_ascii=False, indent=2)[:300])

# Focus on key handlers
key_msgs = ['计算速度', '换行', '开始走路', 'judge', '能否运行', '运行']

def print_block(block, indent=0):
    if not isinstance(block, dict):
        return
    define = block.get('define', '')
    params = block.get('params', [])
    pstrs = []
    for p in params:
        if isinstance(p, dict):
            if p.get('type') == 'block':
                inner = p.get('val', {})
                if isinstance(inner, dict):
                    inner_define = inner.get('define', '?')
                    inner_params = inner.get('params', [])
                    ipstrs = [str(ip.get('val', '')) if isinstance(ip, dict) else str(ip) for ip in inner_params]
                    pstrs.append(f'[{inner_define}({",".join(ipstrs)})]')
                else:
                    pstrs.append(f'[block:{inner}]')
            else:
                pstrs.append(str(p.get('val', '')))
        else:
            pstrs.append(str(p))
    print(' ' * indent + f'{define}({"|".join(pstrs)})')
    # Handle sections (for If/Repeat etc)
    for sec in block.get('sections', []):
        for child in sec.get('children', []):
            print_block(child, indent + 2)

def print_chain(block, indent=0):
    print_block(block, indent)
    if 'next' in block and block['next']:
        print_chain(block['next'], indent)

print('\n=== Key handler details ===')
for path, idx, frag, head in all_frags:
    define, msg = get_define_msg(head)
    if msg in key_msgs or (define == 'WhenGameStarts' and '控制台' in path):
        print(f'\n--- {path}[{idx}] {define}({msg}) ---')
        # The head is the first block, then traverse
        print_chain(head)
