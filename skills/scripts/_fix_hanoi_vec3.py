"""
扫描 ws 中所有 Position/Size/EulerAngles/Scale 字段，
找数组元素不是字符串的条目并修复为字符串。
"""
import sys, json, pathlib
sys.stdout.reconfigure(encoding='utf-8')

WORKDIR = pathlib.Path('output/new/汉诺塔挑战_workdir')
WS_PATH = WORKDIR / 'b8212e928dc647cfb659bc74e0cff402.ws'
OUT_ZIP  = pathlib.Path('output/new/汉诺塔挑战.zip')

sys.path.insert(0, 'scripts')
from pkg_utils import clean_backups, pack_zip_clean

ws = json.loads(WS_PATH.read_bytes().decode('utf-8'))

VEC3_KEYS = {'Position', 'Size', 'EulerAngles', 'Scale', 'BoundsCenter', 'BoundsSize'}
fixes = []

def fix_vec3(obj, path=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in VEC3_KEYS and isinstance(v, list):
                for i, elem in enumerate(v):
                    if not isinstance(elem, str):
                        fixes.append((f'{path}.{k}[{i}]', elem))
                        v[i] = str(elem)
            fix_vec3(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            fix_vec3(v, f'{path}[{i}]')

fix_vec3(ws)

print(f"找到并修复 {len(fixes)} 处非字符串 Vector3 元素：")
for path, val in fixes:
    print(f"  {path} = {val!r}  -> {str(val)!r}")

if fixes:
    WS_PATH.write_bytes(json.dumps(ws, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
    print("[fix] ws 已保存")
    clean_backups(WORKDIR)
    pack_zip_clean(WORKDIR, OUT_ZIP)
    print(f"[done] 重新打包 -> {OUT_ZIP}  ({OUT_ZIP.stat().st_size // 1024} KB)")
else:
    print("[ok] 无需修复")
