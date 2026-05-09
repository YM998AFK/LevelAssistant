"""
全量关卡诊断脚本 · 单次运行输出所有扫描结果
用途：扫描员子 agent 调用，输出 §1~§8 + 表A + 表B

用法：
  python _scan_level.py <WORKDIR> [WS_FILE] [--sections 1,2,3,4]

  WORKDIR     : 已解压的工作目录（含 solution.json / export_info.json / *.ws）
  WS_FILE     : ws 文件绝对路径（可选，不填则自动搜索 WORKDIR 内第一个 .ws 文件）
  --sections  : 逗号分隔的区段号，只输出指定区段（默认输出全部）
                可选值：1 2 3 4 5 6 7 8 A B
                示例：--sections 1,2,3,4   → 只输出元数据 + 演示值（语义转换用）
                      --sections 5,6,7,8,A,B → 只输出 handler 序列 + 路径（生成改动清单用）
"""
import json, sys, os, re, collections

sys.stdout.reconfigure(encoding='utf-8')

# ── 参数解析 ──────────────────────────────────────────────
args = sys.argv[1:]
_sections_arg = None
filtered_args = []
i = 0
while i < len(args):
    if args[i] == '--sections' and i + 1 < len(args):
        _sections_arg = set(args[i + 1].split(','))
        i += 2
    else:
        filtered_args.append(args[i])
        i += 1

def show(sec):
    """返回 True 表示该区段应输出（未指定 --sections 时全部输出）"""
    return _sections_arg is None or str(sec) in _sections_arg

if len(filtered_args) < 1:
    print("用法: python _scan_level.py <WORKDIR> [WS_FILE] [--sections 1,2,3,4]", file=sys.stderr)
    sys.exit(1)

WORKDIR = filtered_args[0]
if len(filtered_args) >= 2:
    ws_file = filtered_args[1]
else:
    ws_files = [f for f in os.listdir(WORKDIR) if f.endswith('.ws')]
    if not ws_files:
        print(f"ERROR: {WORKDIR} 内未找到 .ws 文件", file=sys.stderr)
        sys.exit(1)
    ws_file = os.path.join(WORKDIR, ws_files[0])

# ── 读取 WS ──────────────────────────────────────────────
with open(ws_file, encoding='utf-8') as f:
    ws = json.load(f)

children = ws['scene'].get('children', [])

# ── 工具函数 ──────────────────────────────────────────────
def node_name(node):
    n = (node.get('props') or {}).get('Name', {})
    return n.get('value', n) if isinstance(n, dict) else str(n)

def frag_msg(frag):
    s = (frag.get('head') or {}).get('sections', [{}])
    p = (s[0] if s else {}).get('params', [])
    return (p[0] if p else {}).get('val', '') if p else ''

def frag_define(frag):
    return (frag.get('head') or {}).get('define', '?')

def top_block_defines(frag):
    s = (frag.get('head') or {}).get('sections', [{}])
    ch = (s[0] if s else {}).get('children', [])
    return [c.get('define', '?') for c in ch if isinstance(c, dict)]

def all_frags_in_scene(scene):
    """已被 _scan_all 取代；仅保留供外部脚本单独调用。"""
    result = []
    def _walk(obj, path):
        if not isinstance(obj, dict):
            return
        frags = obj.get('fragments', [])
        if frags:
            result.append((path, obj, frags))
        for k, v in obj.items():
            if k in ('fragments',):
                continue
            if isinstance(v, dict):
                _walk(v, path + '.' + k)
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    _walk(item, path + f'[{i}]')
    _walk(scene, 'scene')
    return result

def collect_broadcast_targets(scene):
    """收集所有 BroadcastMessage 的目标消息名（由 _scan_all 顺带收集，此函数保留接口兼容）"""
    # 实际已在 _scan_all 中收集，不再重复遍历；若单独调用则走轻量树遍历
    targets = set()
    def _walk(obj, depth=0):
        if not isinstance(obj, dict) or depth > 15:
            return
        if obj.get('define') == 'BroadcastMessage':
            ps = obj.get('sections', [{}])[0].get('params', [])
            if ps and isinstance(ps[0], dict):
                val = ps[0].get('val', '')
                if isinstance(val, str) and val:
                    targets.add(val)
        for v in obj.values():
            if isinstance(v, dict):
                _walk(v, depth + 1)
            elif isinstance(v, list):
                for item in v:
                    _walk(item, depth + 1)
    _walk(scene)
    return targets


WRITE_DEFINES = {'SetVar', 'IncVar', 'ListReplaceItemAt', 'ListInsertItemAt',
                 'ListDeleteItemAt', 'ListAdd', 'ListClear', 'ListDeleteItem'}


def _scan_all(scene):
    """单次深度遍历，同时收集：
    - frags_list   : (path, node, frag_list)  用于 §4/§5/§8/表A
    - repeats      : (path, pvals, ch_defines) 用于 §6
    - conditions   : (path, define, pvals, then_count) 用于 §7
    - writes       : (path, define, pvals)     用于 表B
    - broadcasts   : set(str)                  用于 表A
    替代原先 all_frags_in_scene×4 + find_repeats + find_conditions + find_writes
    + json.dumps+regex 共 ~8 次遍历，压缩到 1 次。
    """
    frags_list = []
    repeats    = []
    conditions = []
    writes     = []
    broadcasts = set()

    def _pvals(blk):
        ps = blk.get('sections', [{}])[0].get('params', [])
        out = []
        for p in ps:
            if isinstance(p, dict):
                v = p.get('val', '?')
                out.append(f"[block:{v.get('define','?')}]" if isinstance(v, dict) else repr(v))
        return out

    def _walk_node(obj, path, depth):
        """遍历场景节点树（浅层，不进 fragments 内部）"""
        if not isinstance(obj, dict):
            return
        frags = obj.get('fragments', [])
        if frags:
            frags_list.append((path, obj, frags))
            # 进入每个 fragment 的 block 树做深层收集
            for fi, frag in enumerate(frags):
                _walk_blocks(frag, f"{path}.fragments[{fi}]", depth + 1)
        for k, v in obj.items():
            if k == 'fragments':
                continue
            if isinstance(v, dict):
                _walk_node(v, f"{path}.{k}", depth + 1)
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    _walk_node(item, f"{path}[{i}]", depth + 1)

    def _walk_blocks(obj, path, depth):
        """深度遍历 block 树，收集控制流积木"""
        if not isinstance(obj, dict) or depth > 20:
            return
        d = obj.get('define', '')
        if d:
            if d == 'Repeat':
                ch = obj.get('sections', [{}])[0].get('children', [])
                repeats.append((path, _pvals(obj), [c.get('define', '?') for c in ch if isinstance(c, dict)]))
            elif d in ('If', 'IfElse'):
                ch = obj.get('sections', [{}])[0].get('children', [])
                conditions.append((path, d, _pvals(obj), len(ch)))
            elif d in WRITE_DEFINES:
                writes.append((path, d, _pvals(obj)))
            elif d == 'BroadcastMessage':
                ps = obj.get('sections', [{}])[0].get('params', [])
                if ps and isinstance(ps[0], dict):
                    val = ps[0].get('val', '')
                    if isinstance(val, str) and val:
                        broadcasts.add(val)
        for v in obj.values():
            if isinstance(v, dict):
                _walk_blocks(v, path, depth + 1)
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    _walk_blocks(item, f"{path}[{i}]", depth + 1)

    _walk_node(scene, 'scene', 0)
    return frags_list, repeats, conditions, writes, broadcasts

# ══════════════════════════════════════════════════════════
sol_file = os.path.join(WORKDIR, 'solution.json')
exp_file = os.path.join(WORKDIR, 'export_info.json')
sol, exp = {}, {}
if os.path.exists(sol_file):
    with open(sol_file, encoding='utf-8') as f:
        sol = json.load(f)
if os.path.exists(exp_file):
    with open(exp_file, encoding='utf-8') as f:
        exp = json.load(f)

if show(1):
    print("=" * 60)
    print("§1  包元数据")
    print("=" * 60)
    print(f"  name        : {sol.get('name', '——')}")
    print(f"  init        : {sol.get('init', '——')}")
    print(f"  solutionUid : {exp.get('solutionUid', '——')}")
    print(f"  init==uid?  : {sol.get('init') == exp.get('solutionUid')}")
    print(f"  ws文件      : {os.path.basename(ws_file)}")

# ══════════════════════════════════════════════════════════
if show(2):
    print()
    print("=" * 60)
    print("§2  场景树（顶层节点）")
    print("=" * 60)
    for i, ch in enumerate(children):
        if not isinstance(ch, dict):
            continue
        nm = node_name(ch)
        tp = ch.get('type', '?')
        sub = ch.get('children', [])
        frags_count = sum(len(s.get('fragments', [])) for s in sub if isinstance(s, dict))
        direct_frags = len(ch.get('fragments', []))
        print(f"  [{i:2d}] {tp:<16} {nm:<32} children={len(sub)} child_frags={frags_count} direct_frags={direct_frags}")

# ══════════════════════════════════════════════════════════
props2 = ws['scene'].get('props2', {})
KEY_VARS = ['*OJ-输入信息', '*OJ-执行结果', '*OJ-Judge', 'cin_cut', 'cout_cut',
            'n', 'z', 'x', 'y', 'state', 'variable', '#EVENT', 'cmd', 'err_msg']
if show(3):
    print()
    print("=" * 60)
    print("§3  OJ 关键变量（props2）")
    print("=" * 60)
    for k in KEY_VARS:
        v = props2.get(k, '——')
        if isinstance(v, dict):
            v = f"type={v.get('type')} value={v.get('value')!r}"
        print(f"  {k:<22}: {v}")

# ── 单次全量遍历（§4~§8 + 表A + 表B 共用缓存） ──────────────
_frags, _repeats, _conditions, _writes, _broadcasts = _scan_all(ws['scene'])

# ══════════════════════════════════════════════════════════
if show(4):
    print()
    print("=" * 60)
    print("§4  WhenGameStarts / WhenStartup 初始化汇总")
    print("=" * 60)
    for path, node, frags in _frags:
        for fi, frag in enumerate(frags):
            define = frag_define(frag)
            if define not in ('WhenGameStarts', 'WhenStartup'):
                continue
            sects = (frag.get('head') or {}).get('sections', [{}])
            ch = (sects[0] if sects else {}).get('children', [])
            print(f"  {path}.fragments[{fi}] [{define}]  顶层积木数={len(ch)}")
            for bi, blk in enumerate(ch):
                if not isinstance(blk, dict):
                    continue
                d = blk.get('define', '?')
                ps = blk.get('sections', [{}])[0].get('params', [])
                pvals = [repr(p.get('val', '?')) for p in ps if isinstance(p, dict)]
                inner_ch = blk.get('sections', [{}])[0].get('children', [])
                print(f"    [{bi}] {d}  params={pvals}  inner_count={len(inner_ch)}")

# ══════════════════════════════════════════════════════════
def dump_block(blk, indent=6):
    if not isinstance(blk, dict):
        return
    d = blk.get('define', '?')
    ps = blk.get('sections', [{}])[0].get('params', [])
    pvals = []
    for p in ps:
        if isinstance(p, dict):
            t = p.get('type', '')
            v = p.get('val', '?')
            if t == 'block' and isinstance(v, dict):
                pvals.append(f"[block:{v.get('define','?')}]")
            else:
                pvals.append(repr(v))
    ch = blk.get('sections', [{}])[0].get('children', [])
    print(' ' * indent + f"{d}  params={pvals}  children={len(ch)}")
    for c in ch[:8]:  # 最多展开8个子积木
        dump_block(c, indent + 2)

_HANDLER_DEFINES = {'WhenReceiveMessage', 'WhenGameStarts', 'WhenStartup', 'WhenClick', 'WhenKeyPressed'}
if show(5):
    print()
    print("=" * 60)
    print("§5  所有 WhenReceiveMessage handler 完整积木序列")
    print("=" * 60)
    for path, node, frags in _frags:
        for fi, frag in enumerate(frags):
            define = frag_define(frag)
            msg = frag_msg(frag)
            if define not in _HANDLER_DEFINES:
                continue
            label = f"{msg!r}" if msg else ""
            sects = (frag.get('head') or {}).get('sections', [{}])
            ch = (sects[0] if sects else {}).get('children', [])
            print(f"\n  {path}.fragments[{fi}]  {define}({label})  顶层={len(ch)}个积木")
            for bi, blk in enumerate(ch):
                dump_block(blk, indent=4)

# ══════════════════════════════════════════════════════════
if show(6):
    print()
    print("=" * 60)
    print("§6  循环结构（Repeat 积木）")
    print("=" * 60)
    for path, pvals, ch_defines in _repeats:
        print(f"  {path}  Repeat params={pvals}  inner_children={ch_defines}")

# ══════════════════════════════════════════════════════════
if show(7):
    print()
    print("=" * 60)
    print("§7  条件分支（If / IfElse）")
    print("=" * 60)
    for path, define, pvals, then_count in _conditions:
        print(f"  {path}  {define} params={pvals}  then={then_count}个积木")

# ══════════════════════════════════════════════════════════
if show(8):
    print()
    print("=" * 60)
    print("§8  所有含 fragments 的节点路径索引")
    print("=" * 60)
    for path, node, frags in _frags:
        nm = node_name(node)
        tp = node.get('type', '?')
        print(f"\n  {path}  [{tp}:{nm}]  frags={len(frags)}")
        for fi, frag in enumerate(frags):
            define = frag_define(frag)
            msg = frag_msg(frag)
            td = top_block_defines(frag)
            print(f"    [{fi}] {define}({msg!r})  top_blocks={td}")

# ══════════════════════════════════════════════════════════
ROOT_DEFINES = {'WhenGameStarts', 'WhenStartup', 'WhenReceiveMessage',
                'WhenClick', 'WhenKeyPressed', 'Trigger', 'OnMessage', 'OnCollide'}

if show('A'):
    print()
    print("=" * 60)
    print("表A  Fragment 三栏分类")
    print("=" * 60)
    print(f"  BroadcastMessage 广播目标集合: {sorted(_broadcasts)}")
    print()
    print(f"  {'栏':<4} {'路径':<55} {'idx':<4} {'define(消息名)'}")
    print(f"  {'-'*4} {'-'*55} {'-'*4} {'-'*30}")
    for path, node, frags in _frags:
        for fi, frag in enumerate(frags):
            define = frag_define(frag)
            msg = frag_msg(frag)
            label = f"{define}({msg!r})"
            if define in ROOT_DEFINES:
                col = 'B1' if (define == 'WhenReceiveMessage' and msg == '参数注入') else 'A'
            else:
                col = 'B2'
            print(f"  {col:<4} {path:<55} [{fi}]  {label}")

# ══════════════════════════════════════════════════════════
if show('B'):
    print()
    print("=" * 60)
    print("表B  运行时变量覆盖影响表")
    print("=" * 60)
    print(f"  {'覆盖位置路径':<60} {'积木':<22} {'参数'}")
    print(f"  {'-'*60} {'-'*22} {'-'*30}")
    for path, define, pvals in _writes:
        print(f"  {path:<60} {define:<22} {pvals}")

print()
print("=" * 60)
requested = sorted(_sections_arg) if _sections_arg else ['1','2','3','4','5','6','7','8','A','B']
print(f"扫描完成 区段={','.join(requested)}")
print("=" * 60)
