import json

ws_path = "output/new/汉诺塔挑战_workdir/b8212e928dc647cfb659bc74e0cff402.ws"
data = json.load(open(ws_path, encoding='utf-8'))

scene = data.get('scene', {})
children = scene.get('children', [])

print("=== 各节点 props 完整内容（柱子+底座+盘子）===")
for idx in range(3, 15):
    node = children[idx]
    props = node.get('props', {})
    print(f"\n  index={idx}: {json.dumps(props, ensure_ascii=False)}")

print("\n=== CameraService BlockScript fragments ===")
# Find CameraService
folder = children[0]
folder_inner = folder.get('children', [])
for node in folder_inner:
    if node.get('type') == 'CameraService':
        cam_inner = node.get('children', [])
        for ci in cam_inner:
            if 'fragments' in ci:
                frags = ci.get('fragments', [])
                print(f"CameraService has {len(frags)} fragments")
                for f in frags:
                    head = f.get('head', {})
                    define = head.get('define', '?')
                    secs = head.get('sections', [])
                    ch = secs[0].get('children', []) if secs else []
                    print(f"  {define}: {len(ch)} blocks")
                    for c in ch[:6]:
                        d = c.get('define', '?')
                        params = c.get('sections', [{}])[0].get('params', [])
                        vals = [p.get('val','?') for p in params if p.get('type') == 'var']
                        print(f"    {d}({vals})")
