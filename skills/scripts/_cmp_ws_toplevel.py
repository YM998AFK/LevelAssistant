import sys, json, zipfile, glob, pathlib
sys.stdout.reconfigure(encoding='utf-8')

print("=== 我们的 ws 顶层字段 ===")
ws = json.loads(pathlib.Path('output/new/汉诺塔挑战_workdir/b8212e928dc647cfb659bc74e0cff402.ws').read_bytes().decode('utf-8'))
print("ws 顶层 keys:", list(ws.keys()))
if 'scene' in ws:
    print("scene 顶层 keys:", list(ws['scene'].keys()))

print("\n=== 参考包 ws 顶层字段 ===")
for zpath in glob.glob('参考/*.zip')[:3]:
    try:
        with zipfile.ZipFile(zpath) as zf:
            ws_names = [n for n in zf.namelist() if n.endswith('.ws')]
            if ws_names:
                ref_ws = json.loads(zf.read(ws_names[0]))
                print(f"{zpath}:")
                print("  ws 顶层 keys:", list(ref_ws.keys()))
                if 'scene' in ref_ws:
                    print("  scene 顶层 keys:", list(ref_ws['scene'].keys()))
    except Exception as e:
        print(f"  {zpath}: {e}")
