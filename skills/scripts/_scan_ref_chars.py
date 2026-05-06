"""扫描参考包，找有角色的包并预测 editor 坐标，供用户验证"""
import sys, json, os, zipfile, shutil
sys.stdout.reconfigure(encoding='utf-8')

import glob

# 扫描参考目录下所有 zip
BASE = r"c:\Users\Hetao\Desktop\公司\参考"
TMPDIR = r"c:\Users\Hetao\Desktop\公司\output\new\_ref_scan"
if os.path.exists(TMPDIR): shutil.rmtree(TMPDIR)
os.makedirs(TMPDIR)

def find_chars(node, results):
    if node.get('type') == 'Character':
        name = node.get('props',{}).get('Name','?')
        pos = node.get('props',{}).get('Position', None)
        if pos:
            results.append((name, pos))
    for c in node.get('children', []):
        find_chars(c, results)

found = []
for root, dirs, files in os.walk(BASE):
    for f in files:
        if not f.endswith('.zip'):
            continue
        pkg_path = os.path.join(root, f)
        subdir = os.path.join(TMPDIR, f[:40])
        try:
            os.makedirs(subdir, exist_ok=True)
            with zipfile.ZipFile(pkg_path) as z:
                z.extractall(subdir)
            ws_files = [x for x in os.listdir(subdir) if x.endswith('.ws')]
            if not ws_files:
                continue
            ws = json.load(open(os.path.join(subdir, ws_files[0]), encoding='utf-8'))
            chars = []
            find_chars(ws.get('scene', ws), chars)
            if chars:
                found.append((pkg_path, chars))
        except Exception:
            pass
        finally:
            shutil.rmtree(subdir, ignore_errors=True)

print(f"共找到 {len(found)} 个含角色的参考包：\n")
for pkg_path, chars in found[:10]:  # 只显示前10
    rel = os.path.relpath(pkg_path, r"c:\Users\Hetao\Desktop\公司")
    print(f"【{rel}】")
    for name, pos in chars:
        try:
            px, py, pz = float(pos[0]), float(pos[1]), float(pos[2])
            edX = round(px * 30)
            edY = round(pz * 30)
            edZ = round(py * 30)
            print(f"  {name}: 预测 editor X={edX}, Y={edY}, Z={edZ}(高)")
        except:
            print(f"  {name}: pos={pos} 解析失败")
    print()
