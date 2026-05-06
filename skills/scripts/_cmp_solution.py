import sys, json, zipfile, glob, pathlib
sys.stdout.reconfigure(encoding='utf-8')

print("=== 我们的 solution.json 字段 ===")
sol = json.loads(pathlib.Path('output/new/汉诺塔挑战_workdir/solution.json').read_bytes().decode('utf-8'))
print("顶层 keys:", list(sol.keys()))
if 'projects' in sol:
    print("projects[0] keys:", list(sol['projects'][0].keys()))

print("\n=== 参考包 solution.json 字段（对比）===")
for zpath in glob.glob('参考/*.zip')[:3]:
    try:
        with zipfile.ZipFile(zpath) as zf:
            names = zf.namelist()
            sol_names = [n for n in names if n.endswith('solution.json')]
            if sol_names:
                ref = json.loads(zf.read(sol_names[0]))
                print(f"{zpath}:")
                print("  顶层 keys:", list(ref.keys()))
                if 'projects' in ref:
                    print("  projects[0] keys:", list(ref['projects'][0].keys()))
    except Exception as e:
        print(f"  {zpath}: {e}")
