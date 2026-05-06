"""更新 ws.res 为本包实际使用的 AssetId 列表"""
import sys, json, pathlib
sys.stdout.reconfigure(encoding='utf-8')

WORKDIR = pathlib.Path('output/new/汉诺塔挑战_workdir')
WS_PATH = WORKDIR / 'b8212e928dc647cfb659bc74e0cff402.ws'
OUT_ZIP = pathlib.Path('output/new/汉诺塔挑战.zip')

sys.path.insert(0, 'scripts')
from pkg_utils import clean_backups, pack_zip_clean

ws = json.loads(WS_PATH.read_bytes().decode('utf-8'))

# 扫描所有节点的 AssetId
asset_ids = set()
def scan(obj):
    if isinstance(obj, dict):
        aid = obj.get('props', {}).get('AssetId')
        if aid is not None:
            asset_ids.add(int(aid))
        for v in obj.values():
            scan(v)
    elif isinstance(obj, list):
        for v in obj:
            scan(v)

scan(ws.get('scene', {}))
scan(ws.get('agents', {}))

# 场景模板 AssetId（从 stageType 推断，默认 28746）
scene_type = ws.get('stageType')
if scene_type:
    try:
        asset_ids.add(int(scene_type))
    except:
        pass

res_list = sorted(asset_ids)
print(f"本包实际 AssetId: {res_list}")
ws['res'] = res_list

WS_PATH.write_bytes(json.dumps(ws, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
print("[fix] ws.res 已更新")

clean_backups(WORKDIR)
pack_zip_clean(WORKDIR, OUT_ZIP)
print(f"[done] {OUT_ZIP}  ({OUT_ZIP.stat().st_size // 1024} KB)")
