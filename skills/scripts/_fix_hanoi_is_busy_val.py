"""修复 props2.is_busy 的 val -> value，并重新打包"""
import sys, json, pathlib
sys.stdout.reconfigure(encoding='utf-8')

WORKDIR = pathlib.Path('output/new/汉诺塔挑战_workdir')
WS_PATH = WORKDIR / 'b8212e928dc647cfb659bc74e0cff402.ws'
OUT_ZIP  = pathlib.Path('output/new/汉诺塔挑战.zip')

sys.path.insert(0, 'scripts')
from pkg_utils import clean_backups, pack_zip_clean

ws = json.loads(WS_PATH.read_bytes().decode('utf-8'))

props2 = ws['scene']['props2']
entry = props2.get('is_busy', {})
print(f"修复前: is_busy = {entry}")

if 'val' in entry and 'value' not in entry:
    entry['value'] = entry.pop('val')
    print(f"修复后: is_busy = {entry}")
    WS_PATH.write_bytes(json.dumps(ws, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
    print("[fix] ws 已保存")
else:
    print("[skip] 格式已正确，无需修复")

clean_backups(WORKDIR)
pack_zip_clean(WORKDIR, OUT_ZIP)
print(f"[done] 重新打包 -> {OUT_ZIP}  ({OUT_ZIP.stat().st_size // 1024} KB)")
