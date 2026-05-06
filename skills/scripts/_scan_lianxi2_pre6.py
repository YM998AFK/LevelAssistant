import sys, json
sys.stdout.reconfigure(encoding='utf-8')

ws_path = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1_workdir\55457a4f-886a-4f76-b0ce-fbed8c682ea1.ws'
with open(ws_path, encoding='utf-8') as f:
    ws = json.load(f)

scene = ws['scene']

def find_node_by_name(node, name):
    n = node.get('props', {}).get('Name', '')
    if n == name:
        return node
    for child in node.get('children', []):
        r = find_node_by_name(child, name)
        if r:
            return r
    return None

def get_fragments_from_node(node):
    """Get the BlockScript child that has fragments"""
    # Check direct fragments
    if 'fragments' in node:
        return node['fragments']
    # Check children
    for child in node.get('children', []):
        if 'fragments' in child:
            return child['fragments']
    return []

# Find 控制台 node and its BlockScript with fragments
kongzhi = find_node_by_name(scene, '控制台')
if kongzhi:
    print(f'Found 控制台, children count: {len(kongzhi.get("children", []))}')
    for c in kongzhi.get('children', []):
        name = c.get('props', {}).get('Name', '?')
        print(f'  child: {name}, has fragments: {"fragments" in c}, keys: {list(c.keys())}')

# Actually, from pre4 output, /控制台/BlockScript means:
# scene.children[i].name='控制台' has a child with name='BlockScript' that has fragments
kongzhi_bs = None
if kongzhi:
    for c in kongzhi.get('children', []):
        name = c.get('props', {}).get('Name', '')
        if name == 'BlockScript' or 'fragments' in c:
            kongzhi_bs = c
            print(f'Found BlockScript child: {name}, fragments: {len(c.get("fragments", []))}')
            break

# Or maybe fragments are directly on 控制台's children
print('\n=== Direct exploration of /控制台 ===')
if kongzhi:
    print(f'控制台 keys: {list(kongzhi.keys())}')
    if 'fragments' in kongzhi:
        print(f'Direct fragments: {len(kongzhi["fragments"])}')

# Let me also print the scene.children[6] full structure (shallowly)
print('\n=== scene.children structure ===')
for i, c in enumerate(scene.get('children', [])):
    name = c.get('props', {}).get('Name', '?')
    ctype = c.get('type', '?')
    nfrags = len(c.get('fragments', []))
    nchildren = len(c.get('children', []))
    print(f'  [{i}] type={ctype} name={name} fragments={nfrags} children={nchildren}')
    for j, cc in enumerate(c.get('children', [])):
        cname = cc.get('props', {}).get('Name', '?')
        cctype = cc.get('type', '?')
        nfrags2 = len(cc.get('fragments', []))
        print(f'      [{j}] type={cctype} name={cname} fragments={nfrags2}')
