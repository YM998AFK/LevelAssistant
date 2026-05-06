import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')

ws_path = 'output/new/极限求生-题组1剧情_workdir/855642ec-d0f6-4f5c-9408-9bfa9bfaf05c.ws'
with open(ws_path, 'r', encoding='utf-8') as f:
    ws = json.load(f)

fixed = []

def fix_asset_ids(node, path=''):
    props = node.get('props', {})
    aid = props.get('AssetId')
    name = props.get('Name', '?')
    ntype = node.get('type', '?')
    if isinstance(aid, str) and aid.lstrip('-').isdigit():
        props['AssetId'] = int(aid)
        fixed.append(f'{ntype}[{name}] {repr(aid)} -> {int(aid)}')
    for ch in node.get('children', []):
        fix_asset_ids(ch, path + '.' + name)

fix_asset_ids(ws.get('scene', {}))
print('fixed:')
for f in fixed:
    print(' ', f)
print('total fixed:', len(fixed))

with open(ws_path, 'w', encoding='utf-8') as f:
    json.dump(ws, f, ensure_ascii=False, separators=(',', ':'))
print('saved, size:', os.path.getsize(ws_path))
