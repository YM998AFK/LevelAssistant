import sys, json
sys.stdout.reconfigure(encoding='utf-8')

ws_path = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1_workdir\55457a4f-886a-4f76-b0ce-fbed8c682ea1.ws'
with open(ws_path, encoding='utf-8') as f:
    ws = json.load(f)

scene = ws['scene']

def find_node(node, name):
    n = node.get('props', {}).get('Name', '')
    if n == name:
        return node
    for child in node.get('children', []):
        r = find_node(child, name)
        if r:
            return r
    return None

# Find 控制台 and 法阵的星星 2
kongzhi = find_node(scene, '控制台')
fazhen = find_node(scene, '法阵的星星 2')

# Get cmd=cin block from 控制台
print('=== 控制台 fragment[2] 运行 handler - cmd=cin section (raw) ===')
if kongzhi:
    frag2 = kongzhi['fragments'][2]
    head = frag2['head']
    # Find the If(cmd==cin) block
    body = head.get('sections', [{}])[0].get('children', [])
    for block in body:
        d = block.get('define', '')
        secs = block.get('sections', [])
        if d == 'If' and secs:
            # Check if this is cmd==cin
            cond_params = secs[0].get('params', [])
            if cond_params:
                # Print raw JSON of this block
                print(json.dumps(block, ensure_ascii=False, indent=2)[:2000])
                print()

# Get 计算速度 handler raw
print('\n=== 法阵的星星 2 计算速度 handler (raw) ===')
if fazhen:
    for i, frag in enumerate(fazhen['fragments']):
        head = frag.get('head', {})
        define = head.get('define', '')
        if define == 'WhenReceiveMessage':
            secs = head.get('sections', [])
            if secs and secs[0].get('params', []):
                msg = secs[0]['params'][0]
                if isinstance(msg, dict) and msg.get('val') == '计算速度':
                    print(json.dumps(head, ensure_ascii=False, indent=2)[:5000])
