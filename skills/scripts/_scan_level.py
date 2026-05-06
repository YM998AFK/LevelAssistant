"""
全量关卡诊断脚本 · 单次运行输出所有扫描结果
用途：S1/S2/S3 扫包，定位 OJ 关键逻辑
"""
import json, sys, zipfile, os

sys.stdout.reconfigure(encoding='utf-8')

ZIP_PATH = r'c:\Users\Hetao\Desktop\低16-2 练习2-v1.zip'
WORKDIR   = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1_workdir'

# ── 工具函数 ──────────────────────────────────────────────
def node_name(node):
    n = (node.get('props') or {}).get('Name', {})
    return n.get('value', n) if isinstance(n, dict) else str(n)

def frag_msg(frag):
    s = (frag.get('head') or {}).get('sections', [{}])
    p = (s[0] if s else {}).get('params', [])
    return (p[0] if p else {}).get('val', '') if p else ''

def top_defines(frag):
    s = (frag.get('head') or {}).get('sections', [{}])
    ch = (s[0] if s else {}).get('children', [])
    return [c.get('define','?') for c in ch if isinstance(c, dict)]

def frag_label(frag, idx):
    define = (frag.get('head') or {}).get('define', '?')
    msg = frag_msg(frag)
    return f'[{idx}] {define}({msg!r})'

# ── 读取 WS ──────────────────────────────────────────────
ws_file = os.path.join(WORKDIR, '55457a4f-886a-4f76-b0ce-fbed8c682ea1.ws')
with open(ws_file, encoding='utf-8') as f:
    ws = json.load(f)

children = ws['scene'].get('children', [])

# ══════════════════════════════════════════════════════════
print("=" * 60)
print("§1  包元数据")
print("=" * 60)
sol_file = os.path.join(WORKDIR, 'solution.json')
with open(sol_file, encoding='utf-8') as f:
    sol = json.load(f)
exp_file = os.path.join(WORKDIR, 'export_info.json')
with open(exp_file, encoding='utf-8') as f:
    exp = json.load(f)

print(f"name        : {sol.get('name')}")
print(f"init        : {sol.get('init')}")
print(f"solutionUid : {exp.get('solutionUid')}")
print(f"init==uid?  : {sol.get('init') == exp.get('solutionUid')}")

# ══════════════════════════════════════════════════════════
print()
print("=" * 60)
print("§2  场景树（顶层）")
print("=" * 60)
for i, ch in enumerate(children):
    if not isinstance(ch, dict): continue
    nm = node_name(ch)
    tp = ch.get('type','?')
    sub = ch.get('children', [])
    frags_count = sum(len(s.get('fragments',[])) for s in sub if isinstance(s,dict))
    print(f"  [{i:2d}] {tp:<14} {nm:<30} children={len(sub)} child_frags={frags_count}")

# ══════════════════════════════════════════════════════════
print()
print("=" * 60)
print("§3  OJ 关键变量（props2）")
print("=" * 60)
props2 = ws['scene'].get('props2', {})
KEY_VARS = ['*OJ-输入信息','*OJ-执行结果','*OJ-Judge','cin_cut','cout_cut','n','z','x','y']
for k in KEY_VARS:
    v = props2.get(k, '——')
    if isinstance(v, dict):
        v = f"type={v.get('type')} value={v.get('value')!r}"
    print(f"  {k:<20}: {v}")

# ══════════════════════════════════════════════════════════
print()
print("=" * 60)
print("§4  WhenGameStarts 初始化变量（SetVar 扫描）")
print("=" * 60)
# 找所有 WhenGameStarts fragment 里的 SetVar
def scan_setvars_in_gamestarts(node, label):
    bs_list = [c for c in node.get('children',[]) if isinstance(c,dict) and c.get('type')=='BlockScript']
    for bs in bs_list:
        for frag in bs.get('fragments',[]):
            define = (frag.get('head') or {}).get('define','')
            if define not in ('WhenGameStarts','WhenStartup'): continue
            sects = (frag.get('head') or {}).get('sections',[{}])
            ch = (sects[0] if sects else {}).get('children',[])
            for blk in ch:
                if isinstance(blk,dict) and blk.get('define')=='SetVar':
                    p = blk.get('sections',[{}])[0].get('params',[])
                    vname = p[0].get('val','?') if len(p)>0 else '?'
                    vval  = p[1].get('val','?') if len(p)>1 else '?'
                    print(f"  [{label}] {define}: SetVar({vname!r}, {vval!r})")

for i, ch in enumerate(children):
    if not isinstance(ch,dict): continue
    nm = node_name(ch)
    scan_setvars_in_gamestarts(ch, f"{i}:{nm}")
    # 顶层 BlockScript
    if ch.get('type') == 'BlockScript':
        for frag in ch.get('fragments',[]):
            define = (frag.get('head') or {}).get('define','')
            if define not in ('WhenGameStarts','WhenStartup'): continue
            sects = (frag.get('head') or {}).get('sections',[{}])
            chblks = (sects[0] if sects else {}).get('children',[])
            for blk in chblks:
                if isinstance(blk,dict) and blk.get('define')=='SetVar':
                    p = blk.get('sections',[{}])[0].get('params',[])
                    vn = p[0].get('val','?') if len(p)>0 else '?'
                    vv = p[1].get('val','?') if len(p)>1 else '?'
                    print(f"  [{i}:Scene-BS] {define}: SetVar({vn!r}, {vv!r})")

# ══════════════════════════════════════════════════════════
print()
print("=" * 60)
print("§5  cmd=cin 处理器（关键：z初始值 / cin_cut替换）")
print("=" * 60)

def find_cmd_cin(node, label):
    for sub in node.get('children',[]):
        if not isinstance(sub, dict): continue
        if sub.get('type') != 'BlockScript': continue
        for frag in sub.get('fragments',[]):
            define = (frag.get('head') or {}).get('define','')
            msg = frag_msg(frag)
            if define != 'WhenReceiveMessage' or msg != '运行': continue
            # 在运行 handler 里找 cmd=="cin" 分支
            sects = (frag.get('head') or {}).get('sections',[{}])
            run_children = (sects[0] if sects else {}).get('children',[])
            for blk in run_children:
                if not isinstance(blk, dict): continue
                # 找 If (cmd=="cin")
                if blk.get('define') != 'If': continue
                param_str = json.dumps(blk, ensure_ascii=False)
                if '"cin"' not in param_str: continue
                # 找内部 children
                blk_sects = blk.get('sections',[{}])
                blk_ch = (blk_sects[0] if blk_sects else {}).get('children',[])
                print(f"  [{label}] cmd=cin 分支 found，内部积木：")
                for bi, b in enumerate(blk_ch):
                    if not isinstance(b, dict): continue
                    d = b.get('define','?')
                    ps = b.get('sections',[{}])[0].get('params',[])
                    pvals = [p.get('val','?') for p in ps if isinstance(p,dict)]
                    print(f"    [{bi}] {d}  params={pvals}")

for i, ch in enumerate(children):
    if isinstance(ch, dict):
        find_cmd_cin(ch, f"{i}:{node_name(ch)}")

# ══════════════════════════════════════════════════════════
print()
print("=" * 60)
print("§6  计算速度 handler（关键：外/内层 Repeat 参数）")
print("=" * 60)

def find_jisuan_su(node, label):
    for sub in node.get('children',[]):
        if not isinstance(sub, dict): continue
        if sub.get('type') != 'BlockScript': continue
        for frag in sub.get('fragments',[]):
            if frag_msg(frag) != '计算速度': continue
            print(f"  [{label}] 计算速度 handler:")
            sects = (frag.get('head') or {}).get('sections',[{}])
            ch = (sects[0] if sects else {}).get('children',[])
            for bi, b in enumerate(ch):
                if not isinstance(b, dict): continue
                d = b.get('define','?')
                bsects = b.get('sections',[{}])
                ps = (bsects[0] if bsects else {}).get('params',[])
                pvals = []
                for p in ps:
                    if isinstance(p, dict):
                        if p.get('type') == 'var':
                            pvals.append(repr(p.get('val','')))
                        elif p.get('type') == 'block':
                            inner = p.get('val',{})
                            pvals.append(f"[block:{inner.get('define','?')}]")
                inner_ch = (bsects[0] if bsects else {}).get('children',[])
                inner_defines = [c.get('define','?') for c in inner_ch if isinstance(c,dict)]
                print(f"    [{bi}] {d}  params={pvals}  inner_ch={inner_defines}")
                # 如果是 Repeat，进一步看内层
                if d == 'Repeat' and inner_ch:
                    for ii, ic in enumerate(inner_ch):
                        if not isinstance(ic, dict): continue
                        id2 = ic.get('define','?')
                        is2 = ic.get('sections',[{}])
                        ip = (is2[0] if is2 else {}).get('params',[])
                        ipvals = []
                        for p in ip:
                            if isinstance(p, dict):
                                if p.get('type') == 'var': ipvals.append(repr(p.get('val','')))
                                elif p.get('type') == 'block': ipvals.append(f"[block:{p.get('val',{}).get('define','?')}]")
                        ic2 = (is2[0] if is2 else {}).get('children',[])
                        ic2_def = [c.get('define','?') for c in ic2 if isinstance(c,dict)]
                        print(f"      inner[{ii}] {id2}  params={ipvals}  children={ic2_def}")

for i, ch in enumerate(children):
    if isinstance(ch, dict):
        find_jisuan_su(ch, f"{i}:{node_name(ch)}")

# ══════════════════════════════════════════════════════════
print()
print("=" * 60)
print("§7  换行 handler（关键：位置逻辑，n==1/2/3/4/5 分支）")
print("=" * 60)

def find_huanhang(node, label):
    for sub in node.get('children',[]):
        if not isinstance(sub, dict): continue
        if sub.get('type') != 'BlockScript': continue
        for frag in sub.get('fragments',[]):
            if frag_msg(frag) != '换行': continue
            sects = (frag.get('head') or {}).get('sections',[{}])
            ch = (sects[0] if sects else {}).get('children',[])
            print(f"  [{label}] 换行 handler，顶层 {len(ch)} 个积木：")
            for bi, b in enumerate(ch):
                if not isinstance(b, dict): continue
                d = b.get('define','?')
                bs2 = b.get('sections',[{}])
                ps = (bs2[0] if bs2 else {}).get('params',[])
                # 提取条件里的比较值
                cond_str = json.dumps(ps, ensure_ascii=False)
                import re
                vals = re.findall(r'"val"\s*:\s*"([^"]+)"', cond_str)
                print(f"    [{bi}] {d}  condition_vals={vals[:6]}")

for i, ch in enumerate(children):
    if isinstance(ch, dict):
        find_huanhang(ch, f"{i}:{node_name(ch)}")
        for sub in ch.get('children',[]):
            if isinstance(sub, dict):
                find_huanhang(sub, f"{i}.sub:{node_name(sub)}")

# ══════════════════════════════════════════════════════════
print()
print("=" * 60)
print("§8  fragment 路径索引（所有含 fragments 的节点）")
print("=" * 60)

def list_all_frags(obj, path=''):
    if isinstance(obj, dict):
        frags = obj.get('fragments',[])
        if frags:
            nm = node_name(obj)
            tp = obj.get('type','?')
            print(f"  {path}  [{tp}:{nm}]  frags={len(frags)}")
            for fi, frag in enumerate(frags):
                define = (frag.get('head') or {}).get('define','?')
                msg = frag_msg(frag)
                td = top_defines(frag)
                print(f"    [{fi}] {define}({msg!r})  top={td}")
        for k, v in obj.items():
            list_all_frags(v, path+'.'+k)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            list_all_frags(item, path+f'[{i}]')

list_all_frags(ws['scene'])

print()
print("=" * 60)
print("扫描完成")
print("=" * 60)
