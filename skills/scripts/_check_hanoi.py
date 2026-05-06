import json, sys

ws_path = "output/new/汉诺塔挑战_workdir/b8212e928dc647cfb659bc74e0cff402.ws"
data = json.load(open(ws_path, encoding='utf-8'))

def find_blocks(node, target_define, results=None):
    if results is None:
        results = []
    if isinstance(node, dict):
        if node.get('define') == target_define:
            params = node.get('sections', [{}])[0].get('params', [])
            results.append({'define': target_define, 'param_count': len(params), 'params': params})
        for v in node.values():
            find_blocks(v, target_define, results)
    elif isinstance(node, list):
        for item in node:
            find_blocks(item, target_define, results)
    return results

print("=== 关键积木参数检查 ===")
for target in ['IsGreator', 'EqualTo', 'IsEqual', 'GlideSecsToPosition3D', 'ListDeleteALl', 'ListAdd', 'SetVar']:
    found = find_blocks(data, target)
    print(f"\n{target}: {len(found)} 个")
    if found and target in ['IsGreator', 'EqualTo', 'IsEqual']:
        for i, f in enumerate(found[:5]):
            print(f"  [{i}] params count={f['param_count']}: {json.dumps(f['params'], ensure_ascii=False)[:120]}")

print("\n=== GlideSecsToPosition3D 前3个 ===")
found = find_blocks(data, 'GlideSecsToPosition3D')
for i, f in enumerate(found[:3]):
    print(f"  [{i}] params({f['param_count']}): {json.dumps(f['params'], ensure_ascii=False)[:200]}")

print("\n=== IfElse sections 结构（前2个）===")
def find_ifelse(node, results=None):
    if results is None:
        results = []
    if isinstance(node, dict):
        if node.get('define') == 'IfElse':
            results.append(node)
        for v in node.values():
            find_ifelse(v, results)
    elif isinstance(node, list):
        for item in node:
            find_ifelse(item, results)
    return results

ifelses = find_ifelse(data)
print(f"IfElse 总数: {len(ifelses)}")
for i, ie in enumerate(ifelses[:2]):
    secs = ie.get('sections', [])
    print(f"  [{i}] sections={len(secs)}, s[0].params count={len(secs[0].get('params', []))}, cond={json.dumps(secs[0].get('params', [{}])[0], ensure_ascii=False)[:100]}")
