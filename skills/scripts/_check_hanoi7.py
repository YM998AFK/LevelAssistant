import json

ws_path = "output/new/汉诺塔挑战_workdir/b8212e928dc647cfb659bc74e0cff402.ws"
data = json.load(open(ws_path, encoding='utf-8'))

scene = data.get('scene', {})
children = scene.get('children', [])

def get_frag_children(frag):
    head = frag.get('head', {})
    secs = head.get('sections', [])
    if secs:
        return secs[0].get('children', [])
    return []

# 检查每个盘子的 do_anim IfElse 条件
print("=== 各盘子 do_anim 检查 ===")
for idx in range(9, 15):
    node = children[idx]
    pos = node.get('props', {}).get('Position', [])
    scale = node.get('props', {}).get('Scale', node.get('props', {}).get('Size', []))
    node_inner = node.get('children', [])
    if not node_inner:
        print(f"  index={idx} pos={pos} NO BlockScript!")
        continue
    frags = node_inner[0].get('fragments', [])
    if not frags:
        print(f"  index={idx} pos={pos} NO fragments!")
        continue
    frag = frags[0]
    ch = get_frag_children(frag)
    if not ch:
        print(f"  index={idx} pos={pos} NO children!")
        continue
    first = ch[0]
    if first.get('define') != 'IfElse':
        print(f"  index={idx} pos={pos} first block is {first.get('define')}, expected IfElse!")
        continue
    secs = first.get('sections', [])
    cond_params = secs[0].get('params', []) if secs else []
    # Find the literal param in cond
    cond = cond_params[0] if cond_params else {}
    cond_block = cond.get('val', {}) if cond.get('type') == 'block' else cond
    if isinstance(cond_block, dict):
        cond_secs = cond_block.get('sections', [{}])
        cond_inner_params = cond_secs[0].get('params', [])
        vals = [p.get('val', '?') for p in cond_inner_params]
        then_ch = secs[0].get('children', []) if secs else []
        print(f"  index={idx} pos[1]={pos[1]} IsEqual({vals}) then={len(then_ch)}blocks scale={scale}")
    
# 检查 do_click 的 else-else 分支里的 IfElse[4] (验证积木)
print("\n=== do_click else-else 最后一个IfElse(验证) ===")
ctrl_game = children[2]
bs = ctrl_game.get('children', [])
frags = bs[0].get('fragments', [])
do_click_frag = None
for f in frags:
    head = f.get('head', {})
    secs = head.get('sections', [])
    if secs and secs[0].get('params') and secs[0]['params'][0].get('val') == 'do_click':
        do_click_frag = f
        break

if do_click_frag:
    top_ch = get_frag_children(do_click_frag)
    outer_ifelse = top_ch[0]  # IfElse(sel=="")
    outer_secs = outer_ifelse.get('sections', [])
    else_ch = outer_secs[1].get('children', []) if len(outer_secs) > 1 else []
    inner_ifelse = else_ch[0]  # IfElse(clicked==sel)
    inner_secs = inner_ifelse.get('sections', [])
    else_else_ch = inner_secs[1].get('children', []) if len(inner_secs) > 1 else []
    
    print(f"else-else blocks: {len(else_else_ch)}")
    for i, block in enumerate(else_else_ch):
        print(f"  [{i}] {block.get('define','?')}")
    
    # Find the last IfElse (validation)
    last_ifelse = None
    for block in else_else_ch:
        if block.get('define') == 'IfElse':
            last_ifelse = block
    
    if last_ifelse:
        secs2 = last_ifelse.get('sections', [])
        cond2 = secs2[0].get('params', [{}])[0] if secs2 else {}
        cond2_block = cond2.get('val', {}) if cond2.get('type') == 'block' else cond2
        print(f"\nValidation IfElse condition: {cond2_block.get('define','?')}")
        cond2_secs = cond2_block.get('sections', [{}])
        cond2_params = cond2_secs[0].get('params', []) if cond2_secs else []
        for p in cond2_params:
            if p.get('type') == 'block':
                inner = p.get('val', {})
                if isinstance(inner, dict):
                    inner_secs = inner.get('sections', [{}])
                    inner_params = inner_secs[0].get('params', [])
                    varname = inner_params[0].get('val', '?') if inner_params else '?'
                    print(f"  Variable({varname})")
            elif p == {}:
                print(f"  {{placeholder}}")
            else:
                print(f"  lit({p.get('val','?')})")
        then2 = secs2[0].get('children', []) if secs2 else []
        else2 = secs2[1].get('children', []) if len(secs2) > 1 else []
        print(f"then: {len(then2)} blocks")
        for t in then2[:6]:
            print(f"  then[?] {t.get('define','?')}")
        print(f"else: {len(else2)} blocks")
        for e in else2:
            print(f"  else[?] {e.get('define','?')}")

# 检查 dest_slot 是如何计算的（在valid move序列里）
print("\n=== valid_move_seq: dest_slot 计算 ===")
if do_click_frag and last_ifelse:
    secs2 = last_ifelse.get('sections', [])
    then2 = secs2[0].get('children', []) if secs2 else []
    for i, t in enumerate(then2[:10]):
        define = t.get('define','?')
        params = t.get('sections', [{}])[0].get('params', [])
        info = []
        for p in params:
            if p.get('type') == 'var':
                info.append(f"lit({p.get('val')})")
            elif p.get('type') == 'block':
                v = p.get('val', {})
                if isinstance(v, dict):
                    inner_d = v.get('define', '?')
                    inner_ps = v.get('sections', [{}])[0].get('params', [])
                    inner_vals = [ip.get('val','?') for ip in inner_ps]
                    info.append(f"{inner_d}({inner_vals})")
            elif p == {}:
                info.append('{ph}')
        print(f"  [{i}] {define}({', '.join(info)})")
