import sys, json
sys.stdout.reconfigure(encoding='utf-8')

ws_path = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1_workdir\55457a4f-886a-4f76-b0ce-fbed8c682ea1.ws'
with open(ws_path, encoding='utf-8') as f:
    ws = json.load(f)

scene = ws['scene']

# scene.children structure:
# [1] = top BlockScript (9 frags)
# [5] = 分割数据/BlockScript (4 frags)
# [6] = 控制台/BlockScript (14 frags)
# [11] = 神笔/BlockScript (4 frags)
# [12] = 法阵的星星 2/BlockScript (6 frags)
# [13] = 将军令牌/BlockScript (1 frag)
# [14] = 空挂点/BlockScript (1 frag)

kongzhi_frags = scene['children'][6]['children'][0]['fragments']
fazhen_frags = scene['children'][12]['children'][0]['fragments']

print('=== 控制台 frags ===')
for i, frag in enumerate(kongzhi_frags):
    h = frag['head']
    d = h.get('define','')
    secs = h.get('sections', [])
    msg = ''
    if d == 'WhenReceiveMessage' and secs and secs[0].get('params'):
        p = secs[0]['params'][0]
        msg = p.get('val', '') if isinstance(p, dict) else ''
    print(f'  [{i}] {d}({msg})')

print('\n=== 控制台 frag[2] 运行 - cmd=cin block raw JSON ===')
# Get the 运行 handler (frag[2])
frag2 = kongzhi_frags[2]
# Get body children of the head
body = frag2['head']['sections'][0]['children']
# Find If(cmd==cin)
for block in body:
    if block.get('define') == 'If':
        secs = block.get('sections', [])
        if secs:
            # check condition
            cond = secs[0].get('params', [])
            # Try to find cmd==cin
            cond_str = json.dumps(cond, ensure_ascii=False)
            if 'cin' in cond_str and 'IsEqual' in cond_str:
                print(json.dumps(block, ensure_ascii=False, indent=2))
                break

print('\n=== 法阵的星星 2 frags ===')
for i, frag in enumerate(fazhen_frags):
    h = frag['head']
    d = h.get('define','')
    secs = h.get('sections', [])
    msg = ''
    if d == 'WhenReceiveMessage' and secs and secs[0].get('params'):
        p = secs[0]['params'][0]
        msg = p.get('val', '') if isinstance(p, dict) else ''
    print(f'  [{i}] {d}({msg})')

print('\n=== 法阵的星星 2 frag[3] 计算速度 raw JSON ===')
print(json.dumps(fazhen_frags[3], ensure_ascii=False, indent=2))
