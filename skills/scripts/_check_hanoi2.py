import json

ws_path = "output/new/汉诺塔挑战_workdir/b8212e928dc647cfb659bc74e0cff402.ws"
data = json.load(open(ws_path, encoding='utf-8'))

def find_node(node, name):
    if isinstance(node, dict):
        if node.get('name') == name:
            return node
        for v in node.values():
            r = find_node(v, name)
            if r: return r
    elif isinstance(node, list):
        for item in node:
            r = find_node(item, name)
            if r: return r
    return None

# 检查 ctrl_game 的 fragment 结构
ctrl = find_node(data, 'ctrl_game')
if ctrl:
    bs = find_node(ctrl, 'BlockScript')
    if bs:
        frags = bs.get('fragments', [])
        print(f'ctrl_game: {len(frags)} fragments')
        for i, f in enumerate(frags):
            hat = f.get('hat', {})
            hat_define = hat.get('define', '?')
            children_count = len(f.get('children', []))
            secs = hat.get('sections', [])
            msg = ''
            if secs and secs[0].get('params'):
                msg = secs[0]['params'][0].get('val', '')
            print(f'  [{i}] {hat_define}({msg}) children={children_count}')

# 检查底座
for bname in ['底座A', '底座B', '底座C']:
    node = find_node(data, bname)
    if node:
        bs = find_node(node, 'BlockScript')
        if bs:
            frags = bs.get('fragments', [])
            print(f'{bname}: {len(frags)} fragments, hat={frags[0].get("hat",{}).get("define","?")}')
            # 检查 children 里的 SetVar 值
            for child in frags[0].get('children', []):
                if child.get('define') == 'SetVar':
                    params = child.get('sections', [{}])[0].get('params', [])
                    print(f'  SetVar: {[p.get("val") for p in params]}')

# 检查盘1的 do_anim fragment
disc1 = find_node(data, '盘1')
if disc1:
    bs = find_node(disc1, 'BlockScript')
    if bs:
        frags = bs.get('fragments', [])
        print(f'盘1: {len(frags)} fragments')
        for f in frags:
            hat = f.get('hat', {})
            print(f'  hat={hat.get("define")}')
            children = f.get('children', [])
            print(f'  children count={len(children)}')
            if children:
                first = children[0]
                print(f'  first child define={first.get("define")}')
                secs = first.get('sections', [])
                if secs:
                    cond = secs[0].get('params', [{}])[0]
                    cond_inner = cond.get('val', {}) if cond.get('type') == 'block' else cond
                    if isinstance(cond_inner, dict):
                        cond_params = cond_inner.get('sections', [{}])[0].get('params', [])
                        print(f'  IfElse cond params: {[p.get("val","?") for p in cond_params]}')
                    then_children = secs[0].get('children', [])
                    print(f'  then-children count={len(then_children)}')

# 检查 do_click fragment 的顶层 IfElse 结构深度
print("\n=== do_click 逻辑结构 ===")
ctrl_game = find_node(data, 'ctrl_game')
if ctrl_game:
    bs = find_node(ctrl_game, 'BlockScript')
    if bs:
        frags = bs.get('fragments', [])
        for f in frags:
            hat = f.get('hat', {})
            secs = hat.get('sections', [])
            if secs and secs[0].get('params'):
                msg = secs[0]['params'][0].get('val', '')
                if msg == 'do_click':
                    children = f.get('children', [])
                    print(f'do_click: {len(children)} top-level children')
                    for c in children:
                        define = c.get('define', '?')
                        secs2 = c.get('sections', [])
                        print(f'  {define}: {len(secs2)} sections')
                        if define == 'IfElse' and secs2:
                            then_ch = secs2[0].get('children', [])
                            else_ch = secs2[1].get('children', []) if len(secs2) > 1 else []
                            print(f'    then: {len(then_ch)} children, else: {len(else_ch)} children')
