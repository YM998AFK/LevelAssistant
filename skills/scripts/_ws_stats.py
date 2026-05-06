import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open('output/new/_ws_data_only.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== scene children ===')
for c in data['scene']['children']:
    name = c.get('props', {}).get('Name', '?')
    ctype = c.get('type', '?')
    print(f'  [{ctype}] {name}')
    for ch in c.get('children', []):
        if ch.get('type') == 'BlockScript':
            frags = ch.get('fragments', [])
            if frags:
                block_count = sum(
                    len(f.get('head', {}).get('sections', [{}])[0].get('children', []))
                    for f in frags
                )
                print(f'    BlockScript: {len(frags)} fragments, {block_count} blocks')
        elif ch.get('type') == 'Effect':
            eid = ch.get('props', {}).get('AssetId')
            ename = ch.get('props', {}).get('Name')
            print(f'    Effect: {ename} (AssetId={eid}, type={type(eid).__name__})')

print()
print('=== res array ===')
print(data['res'])
