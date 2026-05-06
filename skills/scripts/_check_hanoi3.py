import json

ws_path = "output/new/汉诺塔挑战_workdir/b8212e928dc647cfb659bc74e0cff402.ws"
data = json.load(open(ws_path, encoding='utf-8'))

# 打印顶层 scene children 的名字和类型
scene = data.get('scene', {})
children = scene.get('children', [])
print(f"scene children count: {len(children)}")
for c in children:
    print(f"  name={c.get('name','?')} type={c.get('type','?')}")
    inner = c.get('children', [])
    for ic in inner:
        print(f"    inner: name={ic.get('name','?')} type={ic.get('type','?')}")
        bs_frags = ic.get('fragments', [])
        if ic.get('type') == 'BlockScript':
            print(f"      fragments count: {len(bs_frags)}")

# 找 ctrl_game 在哪
print("\n=== 寻找 ctrl_game ===")
def find_node_path(node, name, path=""):
    if isinstance(node, dict):
        n = node.get('name', '')
        t = node.get('type', '')
        cur_path = path + f"/{n}({t})"
        if n == name:
            print(f"  FOUND: {cur_path}")
            return node
        for k, v in node.items():
            r = find_node_path(v, name, cur_path)
            if r: return r
    elif isinstance(node, list):
        for item in node:
            r = find_node_path(item, name, path)
            if r: return r
    return None

ctrl = find_node_path(data, 'ctrl_game')
print("\n=== 寻找 底座A ===")
base_a = find_node_path(data, '底座A')

# 检查 scene.props2
print("\n=== scene props2 keys ===")
props2 = scene.get('props2', {})
print(f"props2 keys: {list(props2.keys())[:20]}")

# 检查 BlockScript 在哪
print("\n=== 寻找所有 BlockScript 节点 ===")
def find_blockscripts(node, path=""):
    if isinstance(node, dict):
        n = node.get('name', '')
        t = node.get('type', '')
        cur_path = path + f"/{n}({t})"
        if t == 'BlockScript':
            frags = node.get('fragments', [])
            print(f"  BlockScript at {cur_path}: {len(frags)} fragments")
        for k, v in node.items():
            find_blockscripts(v, cur_path)
    elif isinstance(node, list):
        for item in node:
            find_blockscripts(item, path)

find_blockscripts(data)
