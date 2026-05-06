"""从参考包取缺失的 ws 顶层字段，补入我们的 ws，然后重新打包"""
import sys, json, zipfile, pathlib
sys.stdout.reconfigure(encoding='utf-8')

WORKDIR  = pathlib.Path('output/new/汉诺塔挑战_workdir')
WS_PATH  = WORKDIR / 'b8212e928dc647cfb659bc74e0cff402.ws'
OUT_ZIP  = pathlib.Path('output/new/汉诺塔挑战.zip')
REF_ZIP  = pathlib.Path('参考/14-1 低 练习14.zip')

sys.path.insert(0, 'scripts')
from pkg_utils import clean_backups, pack_zip_clean

# 取参考包的缺失字段默认值
with zipfile.ZipFile(REF_ZIP) as zf:
    ref_ws_name = [n for n in zf.namelist() if n.endswith('.ws')][0]
    ref_ws = json.loads(zf.read(ref_ws_name))

REQUIRED_KEYS = ['agents', 'assets', 'res', 'showmyblock', 'dialogues', 'editorScene', 'projectMode']

# 加载我们的 ws
ws = json.loads(WS_PATH.read_bytes().decode('utf-8'))
print("修复前顶层 keys:", list(ws.keys()))

for key in REQUIRED_KEYS:
    if key not in ws:
        ws[key] = ref_ws.get(key)
        print(f"  [add] {key!r} = {json.dumps(ws[key], ensure_ascii=False)[:80]}")
    else:
        print(f"  [ok]  {key!r} 已存在")

print("修复后顶层 keys:", list(ws.keys()))

WS_PATH.write_bytes(json.dumps(ws, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
print("[fix] ws 已保存")

clean_backups(WORKDIR)
pack_zip_clean(WORKDIR, OUT_ZIP)
print(f"[done] 重新打包 -> {OUT_ZIP}  ({OUT_ZIP.stat().st_size // 1024} KB)")
