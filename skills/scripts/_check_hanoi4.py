import json

ws_path = "output/new/汉诺塔挑战_workdir/b8212e928dc647cfb659bc74e0cff402.ws"
data = json.load(open(ws_path, encoding='utf-8'))

scene = data.get('scene', {})
children = scene.get('children', [])

# 打印第一个 MeshPart 节点的全部顶层 keys 和 props
print("=== 第2个子节点(index=1, ctrl_cam或ctrl_game) 结构 ===")
node1 = children[1]
print(f"top-level keys: {list(node1.keys())}")
print(f"props keys: {list(node1.get('props', {}).keys())}")
print(f"props: {json.dumps(node1.get('props', {}), ensure_ascii=False)}")

print("\n=== 第3个子节点(index=2) 结构 ===")
node2 = children[2]
print(f"top-level keys: {list(node2.keys())}")
print(f"props keys: {list(node2.get('props', {}).keys())}")
print(f"props: {json.dumps(node2.get('props', {}), ensure_ascii=False)}")
inner = node2.get('children', [])
if inner:
    bs = inner[0]
    print(f"  inner[0] keys: {list(bs.keys())}")
    frags = bs.get('fragments', [])
    print(f"  fragments count: {len(frags)}")
    if frags:
        hat = frags[0].get('hat', {})
        print(f"  frag[0] hat: {json.dumps(hat, ensure_ascii=False)}")
        frag_children = frags[0].get('children', [])
        print(f"  frag[0] children count: {len(frag_children)}")
        for i, c in enumerate(frag_children[:5]):
            print(f"    child[{i}] define={c.get('define','?')}")

print("\n=== 找底座A (AssetId=17955, 有BlockScript, z=-2.5) ===")
for i, c in enumerate(children):
    props = c.get('props', {})
    asset = props.get('AssetId', 0)
    pos = props.get('Position', [])
    inner_bs = [ic for ic in c.get('children', []) if ic.get('type') == 'BlockScript' or 'fragments' in ic]
    if asset == 17955 and inner_bs:
        print(f"  index={i} pos={pos} has BlockScript={len(inner_bs[0].get('fragments',[]))} frags")
        frags = inner_bs[0].get('fragments', [])
        if frags:
            hat = frags[0].get('hat', {})
            print(f"    hat: {json.dumps(hat, ensure_ascii=False)[:100]}")
            frag_ch = frags[0].get('children', [])
            for j, ch in enumerate(frag_ch[:3]):
                define = ch.get('define', '?')
                secs = ch.get('sections', [])
                val = ''
                if secs and secs[0].get('params'):
                    val = secs[0]['params'][0].get('val', '')
                print(f"    child[{j}] {define} val={val}")
