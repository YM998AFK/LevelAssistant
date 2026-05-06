"""补齐所有 scene 节点缺失的必填字段（从参考包取默认值）"""
import sys, json, zipfile, pathlib, copy
sys.stdout.reconfigure(encoding='utf-8')

WORKDIR = pathlib.Path('output/new/汉诺塔挑战_workdir')
WS_PATH = WORKDIR / 'b8212e928dc647cfb659bc74e0cff402.ws'
OUT_ZIP = pathlib.Path('output/new/汉诺塔挑战.zip')
REF_ZIP = pathlib.Path('参考/14-1 低 练习14.zip')

sys.path.insert(0, 'scripts')
from pkg_utils import clean_backups, pack_zip_clean

# 从参考包收集各 type 的默认 props
with zipfile.ZipFile(REF_ZIP) as zf:
    ref_ws_name = [n for n in zf.namelist() if n.endswith('.ws')][0]
    ref_ws = json.loads(zf.read(ref_ws_name))

ref_defaults = {}  # type -> props dict (代表性节点)
def collect_ref(nodes):
    for node in nodes:
        t = node.get('type')
        if t and t not in ref_defaults:
            ref_defaults[t] = copy.deepcopy(node.get('props', {}))
        collect_ref(node.get('children', []))

collect_ref(ref_ws['scene'].get('children', []))

# 也从 globals 里收集
for g in ref_ws.get('globals', []):
    obj = g.get('obj', {})
    t = obj.get('type')
    if t and t not in ref_defaults:
        ref_defaults[t] = copy.deepcopy(obj.get('props', {}))
    collect_ref(obj.get('children', []))

print("参考包 type->默认props 已加载:", list(ref_defaults.keys()))

# BlockScript 的默认 props
BLOCKSCRIPT_DEFAULT = {'Name': 'BlockScript', 'EditMode': 0}

fixed_count = 0

def fix_node(node, path=''):
    global fixed_count
    t = node.get('type', '')
    props = node.setdefault('props', {})

    if t == 'BlockScript':
        for k, v in BLOCKSCRIPT_DEFAULT.items():
            if k not in props:
                props[k] = v
                fixed_count += 1
                print(f"  [add] {path}.props.{k} = {v!r}")

    elif t in ref_defaults:
        ref_p = ref_defaults[t]
        for k, v in ref_p.items():
            if k not in props:
                # 跳过会覆盖我们本来值的字段
                if k in ('Name', 'AssetId', 'Position', 'Size', 'Visible', 'Anchor'):
                    continue
                props[k] = copy.deepcopy(v)
                fixed_count += 1
                print(f"  [add] {path}.props.{k} = {json.dumps(v, ensure_ascii=False)[:60]}")

    for child in node.get('children', []):
        fix_node(child, path + f"/{child.get('props',{}).get('Name', child.get('type','?'))}")

ws = json.loads(WS_PATH.read_bytes().decode('utf-8'))

print("\n=== 补全 scene 节点字段 ===")
fix_node(ws['scene'], 'scene')

# 也修 globals
for g in ws.get('globals', []):
    fix_node(g.get('obj', {}), 'globals')

print(f"\n共补全 {fixed_count} 个字段")

WS_PATH.write_bytes(json.dumps(ws, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
print("[fix] ws 已保存")

clean_backups(WORKDIR)
pack_zip_clean(WORKDIR, OUT_ZIP)
print(f"[done] {OUT_ZIP}  ({OUT_ZIP.stat().st_size // 1024} KB)")
