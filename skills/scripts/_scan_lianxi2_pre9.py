import sys, json
sys.stdout.reconfigure(encoding='utf-8')

ws_path = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1_workdir\55457a4f-886a-4f76-b0ce-fbed8c682ea1.ws'
with open(ws_path, encoding='utf-8') as f:
    ws = json.load(f)

scene = ws['scene']
kongzhi_frags = scene['children'][6]['children'][0]['fragments']
fazhen_frags = scene['children'][12]['children'][0]['fragments']

def fmt_block(block, depth=0):
    if not isinstance(block, dict) or depth > 6:
        return '...'
    d = block.get('define', '')
    secs = block.get('sections', [])
    params = secs[0].get('params', []) if secs else []
    pstrs = []
    for p in params:
        if isinstance(p, dict):
            if p.get('type') == 'block':
                pstrs.append(fmt_block(p.get('val', {}), depth+1))
            else:
                pstrs.append(p.get('val', ''))
        else:
            pstrs.append(str(p))
    result = f'{d}({"|".join(pstrs)})'
    children = secs[0].get('children', []) if secs else []
    if children:
        result += ' {'
        for c in children[:3]:
            result += '\n' + '  '*(depth+1) + fmt_block(c, depth+1)
        result += '\n' + '  '*depth + '}'
    return result

print('=== 控制台 orphan fragments [7-12] full ===')
for i in range(7, 13):
    print(f'\n[{i}]:', fmt_block(kongzhi_frags[i]['head']))

print('\n\n=== 法阵的星星 2 all frags ===')
for i, frag in enumerate(fazhen_frags):
    print(f'\n[{i}]:', fmt_block(frag['head']))

print('\n\n=== 将军令牌 frag[0] ===')
lingpai = scene['children'][13]['children'][0]['fragments']
for i, frag in enumerate(lingpai):
    print(f'\n[{i}]:', fmt_block(frag['head']))

print('\n\n=== 空挂点 frag[0] ===')
kgd = scene['children'][14]['children'][0]['fragments']
for i, frag in enumerate(kgd):
    print(f'\n[{i}]:', fmt_block(frag['head']))

# Also check 分割数据 frags more carefully
print('\n\n=== 分割数据 all frags ===')
fengge_frags = scene['children'][5]['children'][0]['fragments']
for i, frag in enumerate(fengge_frags):
    print(f'\n[{i}]:', fmt_block(frag['head']))

# Find where z = [block] (z set to computed value)
print('\n\n=== Searching for SetVar(z, block) ===')
def search_setvar_z_block(block, path=''):
    if not isinstance(block, dict):
        return
    d = block.get('define', '')
    secs = block.get('sections', [])
    params = secs[0].get('params', []) if secs else []
    if d == 'SetVar' and len(params) >= 2:
        p0 = params[0]
        p1 = params[1]
        if isinstance(p0, dict) and p0.get('val') == 'z':
            if isinstance(p1, dict) and p1.get('type') == 'block':
                print(f'  Found at {path}: SetVar(z, {fmt_block(p1.get("val", {}))})')
    for c in secs[0].get('children', []) if secs else []:
        search_setvar_z_block(c, path+'/')
    for sec in secs[1:]:
        for c in sec.get('children', []):
            search_setvar_z_block(c, path+'/sec/')

def search_all_frags(node, path=''):
    frags = node.get('fragments', [])
    for i, frag in enumerate(frags):
        search_setvar_z_block(frag['head'], f'{path}[{i}]')
    for child in node.get('children', []):
        cname = child.get('props', {}).get('Name', '?')
        search_all_frags(child, f'{path}/{cname}')

search_all_frags(scene)
