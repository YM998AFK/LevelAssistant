"""从多个参考包提取角色坐标，验证 ws×30 + 轴互换规则"""
import sys, json, os, zipfile, shutil
sys.stdout.reconfigure(encoding='utf-8')

# 选几个有角色的包
PACKAGES = [
    r"c:\Users\Hetao\Desktop\公司\关卡库\字符转换练习-教师端.zip",
    r"c:\Users\Hetao\Desktop\公司\关卡库\战役9-教师端.zip",
    r"c:\Users\Hetao\Desktop\公司\参考\基础角色包.zip",   # 已知：editor=(444,366,600)
]

TMPDIR = r"c:\Users\Hetao\Desktop\公司\output\new\_multi_verify"
if os.path.exists(TMPDIR): shutil.rmtree(TMPDIR)
os.makedirs(TMPDIR)

def find_chars(node, results, path=""):
    t = node.get('type','')
    name = node.get('props',{}).get('Name','')
    if t == 'Character':
        pos = node.get('props',{}).get('Position', None)
        if pos:
            results.append((name, pos))
    for c in node.get('children', []):
        find_chars(c, results)

def find_camera_follow(node, results):
    """找 CameraFollow block 的参数"""
    if node.get('type') == 'BlockScript':
        for frag in node.get('fragments', []):
            def walk_block(b):
                define = b.get('head',{}).get('define','') if 'head' in b else b.get('define','')
                if define == 'CameraFollow':
                    secs = b.get('head',{}).get('sections', b.get('sections',[]))
                    if secs:
                        params = secs[0].get('params',[])
                        if len(params) >= 4:
                            results.append([p.get('val','?') for p in params])
                for s in (b.get('head',{}) if 'head' in b else b).get('sections',[]):
                    for ch in s.get('children',[]):
                        walk_block(ch)
            walk_block(frag)
    for c in node.get('children',[]):
        find_camera_follow(c, results)

print("=" * 60)
for pkg_path in PACKAGES:
    if not os.path.exists(pkg_path):
        print(f"[跳过] 文件不存在: {os.path.basename(pkg_path)}")
        continue
    pkg_name = os.path.basename(pkg_path)
    subdir = os.path.join(TMPDIR, pkg_name)
    os.makedirs(subdir, exist_ok=True)
    try:
        with zipfile.ZipFile(pkg_path) as z:
            z.extractall(subdir)
        ws_files = [f for f in os.listdir(subdir) if f.endswith('.ws')]
        if not ws_files:
            print(f"[{pkg_name}] 无 .ws 文件")
            continue
        ws = json.load(open(os.path.join(subdir, ws_files[0]), encoding='utf-8'))
        chars = []
        find_chars(ws.get('scene', ws), chars)
        cam_follows = []
        find_camera_follow(ws.get('scene', ws), cam_follows)

        print(f"\n【{pkg_name}】")
        for name, pos in chars:
            try:
                px, py, pz = float(pos[0]), float(pos[1]), float(pos[2])
                ex = round(px * 30)  # ws[0] → editor X
                ey = round(pz * 30)  # ws[2] → editor Y
                ez = round(py * 30)  # ws[1] → editor Z (vertical)
                print(f"  角色: {name}")
                print(f"    ws raw:    ({px:.4f}, {py:.4f}, {pz:.4f})")
                print(f"    →editor:   X={ex}, Y={ey}, Z={ez}  (×30, 轴: ws0→edX, ws1→edZ↑, ws2→edY)")
            except Exception as e:
                print(f"  解析失败: {e}")
        if cam_follows:
            print(f"  CameraFollow参数: {cam_follows}")
    except Exception as e:
        print(f"[{pkg_name}] 错误: {e}")

print("\n" + "=" * 60)
print("参考：基础角色包已知 editor=(444,366,600)")
print("ws=(14.80266,19.98423,12.20055) × 30 → 轴转换后应得 (444,366,600)")
