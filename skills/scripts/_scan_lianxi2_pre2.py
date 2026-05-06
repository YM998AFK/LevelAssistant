import sys, json
sys.stdout.reconfigure(encoding='utf-8')

ws_path = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1_workdir\55457a4f-886a-4f76-b0ce-fbed8c682ea1.ws'
with open(ws_path, encoding='utf-8') as f:
    ws = json.load(f)

# Print top-level keys
print('=== ws top-level keys ===')
print(list(ws.keys())[:20])

# Look at scene structure
scene = ws
for key in ['scene', 'Scene', 'root']:
    if key in ws:
        scene = ws[key]
        print(f'Found scene under key: {key}')
        break

print(f'scene type: {type(scene)}')
if isinstance(scene, dict):
    print(f'scene keys: {list(scene.keys())[:20]}')

# Try to find all children recursively
def explore(node, path='', depth=0):
    if depth > 5:
        return
    if isinstance(node, dict):
        name = node.get('name', node.get('Name', ''))
        ntype = node.get('type', node.get('Type', ''))
        
        # Look for fragments
        if 'fragments' in node:
            print(f'{path} -> fragments count: {len(node["fragments"])}')
            for i, frag in enumerate(node['fragments'][:3]):
                print(f'  frag[{i}]: keys={list(frag.keys())}')
                if 'blocks' in frag:
                    print(f'    blocks[0]: {json.dumps(frag["blocks"][0])[:100] if frag["blocks"] else "empty"}')
        
        if 'BlockScript' in node:
            print(f'{path} -> has BlockScript, keys={list(node["BlockScript"].keys())}')
            bs = node['BlockScript']
            if 'fragments' in bs:
                print(f'  BlockScript.fragments count: {len(bs["fragments"])}')
        
        # Recurse into children
        for child in node.get('children', node.get('Children', [])):
            cname = child.get('name', child.get('Name', '?'))
            explore(child, path + '/' + cname, depth + 1)
        
        # Check for scripts
        if 'scripts' in node:
            print(f'{path} -> scripts keys: {list(node["scripts"].keys())[:5]}')

explore(scene)

# Also print the raw structure up to depth 2
print('\n=== Raw ws structure (depth 2) ===')
def print_struct(node, indent=0):
    if indent > 4:
        return
    if isinstance(node, dict):
        for k, v in list(node.items())[:10]:
            if isinstance(v, (dict, list)):
                print(' '*indent + f'{k}: [{type(v).__name__}]')
                if isinstance(v, list) and len(v) > 0:
                    print_struct(v[0], indent + 2)
                elif isinstance(v, dict):
                    print_struct(v, indent + 2)
            else:
                print(' '*indent + f'{k}: {str(v)[:50]}')
    elif isinstance(node, list):
        print(' '*indent + f'[{len(node)} items]')

print_struct(ws)
