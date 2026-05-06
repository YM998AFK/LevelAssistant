import sys, json
sys.stdout.reconfigure(encoding='utf-8')

ws = json.load(open('output/new/汉诺塔挑战_workdir/b8212e928dc647cfb659bc74e0cff402.ws', encoding='utf-8'))

print("=== scene.props2 格式（前8条）===")
props2 = ws.get('scene', {}).get('props2', {})
for i, (k, v) in enumerate(props2.items()):
    print(f"  {k!r}: {v}")
    if i >= 7:
        print(f"  ... ({len(props2)} 条合计)")
        break

# 检查参考包 props2 格式
import zipfile, glob
refs = glob.glob('参考/*.zip')[:1]
if refs:
    print(f"\n=== 参考包 {refs[0]} 的 props2 格式 ===")
    with zipfile.ZipFile(refs[0]) as zf:
        ws_names = [n for n in zf.namelist() if n.endswith('.ws')]
        if ws_names:
            ref_ws = json.loads(zf.read(ws_names[0]))
            ref_p2 = ref_ws.get('scene', {}).get('props2', {})
            for i, (k, v) in enumerate(ref_p2.items()):
                print(f"  {k!r}: {v}")
                if i >= 7:
                    print(f"  ... ({len(ref_p2)} 条合计)")
                    break
