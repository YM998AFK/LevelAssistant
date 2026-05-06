"""从多个参考包提取角色坐标，验证 ws×30 + 轴互换规则"""
import sys, json, os, zipfile, shutil
sys.stdout.reconfigure(encoding='utf-8')

PACKAGES = [
    r"c:\Users\Hetao\Desktop\公司\参考\视角参考\基础角色包.zip",          # 已知 editor=(444,366,600)
    r"c:\Users\Hetao\Desktop\公司\参考\低L14-2 题组3\隐藏练习.zip",       # 普通关卡
    r"c:\Users\Hetao\Desktop\公司\参考\低L14-3-题组3\低L14-3练习12.zip",  # 普通关卡
    r"c:\Users\Hetao\Desktop\公司\参考\S高L13-3-1-练习5.zip",             # 另一关卡
    r"c:\Users\Hetao\Desktop\公司\关卡输出\字符串变换练习-教师端.zip",     # 关卡输出
]

TMPDIR = r"c:\Users\Hetao\Desktop\公司\output\new\_multi_verify2"
if os.path.exists(TMPDIR): shutil.rmtree(TMPDIR)
os.makedirs(TMPDIR)

def find_chars(node, results):
    t = node.get('type','')
    name = node.get('props',{}).get('Name','')
    if t == 'Character':
        pos = node.get('props',{}).get('Position', None)
        if pos:
            results.append((name, pos))
    for c in node.get('children', []):
        find_chars(c, results)

print("=" * 60)
for pkg_path in PACKAGES:
    if not os.path.exists(pkg_path):
        print(f"[跳过] {os.path.basename(pkg_path)}")
        continue
    pkg_name = os.path.basename(pkg_path)
    subdir = os.path.join(TMPDIR, pkg_name[:30])
    os.makedirs(subdir, exist_ok=True)
    try:
        with zipfile.ZipFile(pkg_path) as z:
            z.extractall(subdir)
        ws_files = [f for f in os.listdir(subdir) if f.endswith('.ws')]
        if not ws_files:
            print(f"[{pkg_name}] 无 .ws")
            continue
        ws = json.load(open(os.path.join(subdir, ws_files[0]), encoding='utf-8'))
        chars = []
        find_chars(ws.get('scene', ws), chars)

        print(f"\n【{pkg_name}】")
        for cname, pos in chars:
            try:
                px, py, pz = float(pos[0]), float(pos[1]), float(pos[2])
                # 规则：ws×30, 轴: ws[0]→edX, ws[1]→edZ(高度), ws[2]→edY
                edX = round(px * 30)
                edY = round(pz * 30)
                edZ = round(py * 30)
                print(f"  {cname}: ws=({px:.3f},{py:.3f},{pz:.3f}) → editor X={edX}, Y={edY}, Z={edZ}(高)")
            except Exception as e:
                print(f"  解析失败: {e}, pos={pos}")
    except Exception as e:
        print(f"[{pkg_name}] 错误: {e}")

print("\n基础角色包已知答案：editor X=444, Y=366, Z=600(高)")
