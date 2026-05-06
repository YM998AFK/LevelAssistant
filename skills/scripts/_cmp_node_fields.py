"""对比我们的 scene 节点 props 字段与参考包，找缺失的必填字段"""
import sys, json, zipfile, pathlib
sys.stdout.reconfigure(encoding='utf-8')

WORKDIR = pathlib.Path('output/new/汉诺塔挑战_workdir')
WS_PATH = WORKDIR / 'b8212e928dc647cfb659bc74e0cff402.ws'
REF_ZIP = pathlib.Path('参考/14-1 低 练习14.zip')

ws = json.loads(WS_PATH.read_bytes().decode('utf-8'))
with zipfile.ZipFile(REF_ZIP) as zf:
    ref_ws_name = [n for n in zf.namelist() if n.endswith('.ws')][0]
    ref_ws = json.loads(zf.read(ref_ws_name))

def collect_props_keys_by_type(scene):
    by_type = {}
    for node in scene.get('children', []):
        t = node.get('type', 'unknown')
        keys = set(node.get('props', {}).keys())
        by_type.setdefault(t, set()).update(keys)
    return by_type

our_types = collect_props_keys_by_type(ws['scene'])
ref_types = collect_props_keys_by_type(ref_ws['scene'])

print("=== 按 type 对比 props 字段 ===")
all_types = set(our_types) | set(ref_types)
for t in sorted(all_types):
    our_k = our_types.get(t, set())
    ref_k = ref_types.get(t, set())
    missing = ref_k - our_k
    extra = our_k - ref_k
    if missing:
        print(f"[{t}] 我们缺少: {sorted(missing)}")
    if extra:
        print(f"[{t}] 我们多出: {sorted(extra)}")
    if not missing and not extra:
        print(f"[{t}] ✅ 字段一致")

# 也检查 scene.props 字段
our_sp = set(ws['scene'].get('props', {}).keys())
ref_sp = set(ref_ws['scene'].get('props', {}).keys())
missing_sp = ref_sp - our_sp
if missing_sp:
    print(f"\n[scene.props] 缺少: {sorted(missing_sp)}")
    print(f"  参考值: { {k: ref_ws['scene']['props'][k] for k in missing_sp} }")
