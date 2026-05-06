import json

ws_path = "output/new/汉诺塔挑战_workdir/b8212e928dc647cfb659bc74e0cff402.ws"
data = json.load(open(ws_path, encoding='utf-8'))

scene = data.get('scene', {})
children = scene.get('children', [])

# ctrl_game is index 2
ctrl_game = children[2]
inner = ctrl_game.get('children', [])
bs = inner[0]  # BlockScript
frags = bs.get('fragments', [])

print(f"ctrl_game BlockScript fragments count: {len(frags)}")
print(f"\n=== Fragment 0 raw (first 2000 chars) ===")
print(json.dumps(frags[0], ensure_ascii=False)[:2000])

print(f"\n=== Fragment 0 top-level keys ===")
print(list(frags[0].keys()))

# Check bottom-base A (index=6)
base_a = children[6]
base_bs = base_a.get('children', [])
if base_bs:
    base_frags = base_bs[0].get('fragments', [])
    print(f"\n=== 底座A Fragment 0 top-level keys ===")
    print(list(base_frags[0].keys()))
    print(f"=== 底座A Fragment 0 raw ===")
    print(json.dumps(base_frags[0], ensure_ascii=False)[:1000])
