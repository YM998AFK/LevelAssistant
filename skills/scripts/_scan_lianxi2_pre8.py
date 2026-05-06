import sys, json
sys.stdout.reconfigure(encoding='utf-8')

ws_path = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1_workdir\55457a4f-886a-4f76-b0ce-fbed8c682ea1.ws'
with open(ws_path, encoding='utf-8') as f:
    ws = json.load(f)

scene = ws['scene']
kongzhi_frags = scene['children'][6]['children'][0]['fragments']
fazhen_frags = scene['children'][12]['children'][0]['fragments']
top_frags = scene['children'][1]['fragments']

def print_block(block, indent=0):
    if not isinstance(block, dict):
        return
    d = block.get('define', '')
    secs = block.get('sections', [])
    main_params = secs[0].get('params', []) if secs else []
    pstrs = []
    for p in main_params:
        if isinstance(p, dict):
            if p.get('type') == 'block':
                inner = p.get('val', {})
                if isinstance(inner, dict):
                    id2 = inner.get('define', '?')
                    secs2 = inner.get('sections', [])
                    ip = secs2[0].get('params', []) if secs2 else []
                    ipstrs = []
                    for pp in ip:
                        if isinstance(pp, dict):
                            if pp.get('type') == 'block':
                                ipstrs.append('[block...]')
                            else:
                                ipstrs.append(str(pp.get('val', '')))
                        else:
                            ipstrs.append(str(pp))
                    pstrs.append(f'[{id2}({",".join(ipstrs)})]')
                else:
                    pstrs.append(f'[?{inner}]')
            elif p.get('type') == 'var':
                pstrs.append(p.get('val', ''))
            else:
                pstrs.append(str(p.get('val', '')))
        else:
            pstrs.append(str(p))
    print(' '*indent + f'{d}({"|".join(pstrs)})')
    for sec_i, sec in enumerate(secs):
        children = sec.get('children', [])
        if children:
            for child in children:
                print_block(child, indent+2)

print('=== 控制台 frag[4] 初始化 handler ===')
print_block(kongzhi_frags[4]['head'])

print('\n=== 控制台 frag[1] WhenStartup ===')
print_block(kongzhi_frags[1]['head'])

print('\n=== 法阵的星星 frag[0] WhenIStartAsAClone ===')
print_block(fazhen_frags[0]['head'])

print('\n=== 法阵的星星 frag[4] (GotoPosition3D?) ===')
print_block(fazhen_frags[4]['head'])

print('\n=== top BlockScript frags ===')
for i, frag in enumerate(top_frags):
    head = frag['head']
    d = head.get('define','')
    secs = head.get('sections',[])
    msg = ''
    if d == 'WhenReceiveMessage' and secs and secs[0].get('params'):
        msg = secs[0]['params'][0].get('val','') if isinstance(secs[0]['params'][0], dict) else ''
    print(f'\n--- top[{i}] {d}({msg}) ---')
    print_block(head)

print('\n=== 控制台 所有 SetVar orphan fragments (7-12) ===')
for i in range(7, 13):
    print(f'\n[{i}]:', json.dumps(kongzhi_frags[i]['head'], ensure_ascii=False)[:100])
