import json

ws_path = "output/new/汉诺塔挑战_workdir/b8212e928dc647cfb659bc74e0cff402.ws"
data = json.load(open(ws_path, encoding='utf-8'))

scene = data.get('scene', {})
children = scene.get('children', [])

# ctrl_game is index 2
ctrl_game = children[2]
inner = ctrl_game.get('children', [])
bs = inner[0]  # BlockScript
frags = bs.get('fragments', [])

def get_frag_children(frag):
    """获取fragment的实际block children"""
    head = frag.get('head', {})
    secs = head.get('sections', [])
    if secs:
        return secs[0].get('children', [])
    return []

def get_block_define(block):
    return block.get('define', '?')

def get_block_children(block, section_idx=0):
    """获取block的子块（IfElse的then/else分支）"""
    secs = block.get('sections', [])
    if len(secs) > section_idx:
        return secs[section_idx].get('children', [])
    return []

print(f"ctrl_game has {len(frags)} fragments")
for i, f in enumerate(frags):
    head = f.get('head', {})
    define = head.get('define', '?')
    secs = head.get('sections', [])
    msg = ''
    if secs and secs[0].get('params'):
        msg = secs[0]['params'][0].get('val', '') if secs[0]['params'] else ''
    ch = get_frag_children(f)
    print(f"  [{i}] {define}({msg}) -> {len(ch)} blocks")

# 找 do_click fragment
do_click_frag = None
for f in frags:
    head = f.get('head', {})
    secs = head.get('sections', [])
    if secs and secs[0].get('params'):
        params = secs[0]['params']
        if params and params[0].get('val') == 'do_click':
            do_click_frag = f
            break

if do_click_frag:
    print("\n=== do_click 顶层 blocks ===")
    ch = get_frag_children(do_click_frag)
    for i, block in enumerate(ch):
        define = get_block_define(block)
        print(f"  [{i}] {define}")
        if define == 'IfElse':
            secs = block.get('sections', [])
            cond_params = secs[0].get('params', []) if secs else []
            then_ch = secs[0].get('children', []) if secs else []
            else_ch = secs[1].get('children', []) if len(secs) > 1 else []
            cond = cond_params[0] if cond_params else {}
            cond_val = cond.get('val', {}) if cond.get('type') == 'block' else cond
            if isinstance(cond_val, dict):
                print(f"    cond: {cond_val.get('define', '?')}")
                inner_params = cond_val.get('sections', [{}])[0].get('params', [])
                for p in inner_params:
                    if p.get('type') == 'block':
                        inner_block = p.get('val', {})
                        if isinstance(inner_block, dict):
                            var_secs = inner_block.get('sections', [{}])[0].get('params', [])
                            if var_secs:
                                print(f"      arg: Variable({var_secs[0].get('val', '?')})")
                    elif p.get('type') == 'var':
                        print(f"      arg: lit({p.get('val', '?')})")
                    else:
                        print(f"      arg: {p}")
            print(f"    then: {len(then_ch)} blocks, else: {len(else_ch)} blocks")
            # 深入 else 分支
            if else_ch:
                for j, el_block in enumerate(else_ch):
                    el_define = get_block_define(el_block)
                    el_then = get_block_children(el_block, 0)
                    el_else = get_block_children(el_block, 1)
                    print(f"      else[{j}] {el_define}: then={len(el_then)}, else={len(el_else)}")
                    if el_define == 'IfElse':
                        # 深入 else-else (尝试移动)
                        for k, ee_block in enumerate(el_else):
                            ee_define = get_block_define(ee_block)
                            print(f"        else-else[{k}] {ee_define}")
else:
    print("WARNING: do_click fragment NOT FOUND!")

# 检查 do_anim (disc 1, index=9)
disc1 = children[9]
disc1_pos = disc1.get('props', {}).get('Position', [])
print(f"\n=== disc at index=9, pos={disc1_pos} ===")
disc1_inner = disc1.get('children', [])
if disc1_inner:
    disc1_frags = disc1_inner[0].get('fragments', [])
    print(f"  fragments: {len(disc1_frags)}")
    for f in disc1_frags:
        head = f.get('head', {})
        define = head.get('define', '?')
        secs = head.get('sections', [])
        msg = ''
        if secs and secs[0].get('params'):
            msg = secs[0]['params'][0].get('val', '') if secs[0]['params'] else ''
        ch = get_frag_children(f)
        print(f"  {define}({msg}) -> {len(ch)} blocks")
        if ch:
            first = ch[0]
            print(f"    first block: {get_block_define(first)}")
            if get_block_define(first) == 'IfElse':
                then_ch2 = get_block_children(first, 0)
                print(f"    IfElse then: {len(then_ch2)} blocks")
                for gi in then_ch2[:4]:
                    print(f"      {get_block_define(gi)}")
