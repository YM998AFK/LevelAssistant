"""
低16-2 练习2 修改脚本：挑战2动画 → 挑战4动画
改动点：
  A. 控制台 BS frag[2] 的 cmd=="cin" 分支：
     A1. SetVar(z, ListGetItemAt(1,cin_cut)) → SetVar(z, "1")
     A2. ListReplaceItemAt(1, cin_cut, "1") → 改为 no-op（index→9999）
     A3. BroadcastMessageAndWait("换行") → 改为 no-op（消息→"_unused"）
  B. 法阵的星星2 BS frag[3] 的 计算速度 handler：
     B1. 在外层 Repeat 的 children[0]（内层 Repeat）之后插入
         BroadcastMessageAndWait("换行")
"""
import json, sys, copy

sys.stdout.reconfigure(encoding='utf-8')

WS_PATH = r'c:\Users\Hetao\Desktop\公司\output\modify\低16-2_练习2-v1_workdir\55457a4f-886a-4f76-b0ce-fbed8c682ea1.ws'

with open(WS_PATH, encoding='utf-8') as f:
    ws = json.load(f)

children = ws['scene']['children']

# ── 工具函数 ─────────────────────────────────────────
def get_sections_children(frag):
    """返回 fragment head 的 sections[0].children"""
    return frag['head']['sections'][0].get('children', [])

def find_if_block_by_cmd(run_children, cmd_val):
    """在 运行 handler 的顶层 If 块中，找条件含 cmd_val 的那个"""
    for blk in run_children:
        if blk.get('define') != 'If':
            continue
        blk_str = json.dumps(blk, ensure_ascii=False)
        if f'"{cmd_val}"' in blk_str:
            return blk
    return None

def get_if_body(if_block):
    """返回 If 块 sections[0].children（即 Then 分支积木列表）"""
    return if_block['sections'][0].get('children', [])

# ══════════════════════════════════════════════════════
# A. 控制台 BS (children[6].children[0]) frag[2]
# ══════════════════════════════════════════════════════
konsole_bs = children[6]['children'][0]
run_frag = konsole_bs['fragments'][2]
assert run_frag['head']['define'] == 'WhenReceiveMessage', "frag[2] 不是 WhenReceiveMessage！"
assert get_sections_children(run_frag)[0]['define'] == 'If', "children[0] 不是 If！"

run_top_children = get_sections_children(run_frag)

# 找 cmd=="cin" 的 If 块（传值不含引号，函数内搜 '"cin"'）
cin_if = find_if_block_by_cmd(run_top_children, 'cin')
assert cin_if is not None, "找不到 cmd=cin 的 If 块！"

cin_body = get_if_body(cin_if)  # [SetVar(z), ListReplaceItemAt, BcstWait(计算速度), BcstWait(换行), BcstWait(令牌出现)]

print("=== 改前 cmd=cin body ===")
for i, blk in enumerate(cin_body):
    ps = blk.get('sections', [{}])[0].get('params', [])
    pvals = [p.get('val', '?') for p in ps if isinstance(p, dict)]
    print(f"  [{i}] {blk['define']}  params_vals={pvals}")

# A1. SetVar(z, ...) → SetVar(z, "1")
setvar_z = cin_body[0]
assert setvar_z['define'] == 'SetVar', f"body[0] 应是 SetVar，实际是 {setvar_z['define']}"
assert setvar_z['sections'][0]['params'][0].get('val') == 'z', "SetVar 第一个参数不是 z"
setvar_z['sections'][0]['params'][1] = {"type": "var", "val": "1"}   # 改第二个参数
print("\n[A1] SetVar(z) 第二参数已改为 '1'")

# A2. ListReplaceItemAt → no-op（把 index 从 1 → 9999，等效空操作）
list_rep = cin_body[1]
assert list_rep['define'] == 'ListReplaceItemAt', f"body[1] 应是 ListReplaceItemAt，实际是 {list_rep['define']}"
list_rep['sections'][0]['params'][0] = {"type": "var", "val": "9999"}
print("[A2] ListReplaceItemAt index 改为 9999（no-op）")

# A3. BroadcastMessageAndWait("换行") → "_unused"
bcast_huanhang = cin_body[3]
assert bcast_huanhang['define'] == 'BroadcastMessageAndWait', f"body[3] 应是 BroadcastMessageAndWait，实际是 {bcast_huanhang['define']}"
assert bcast_huanhang['sections'][0]['params'][0].get('val') == '换行', "body[3] 消息不是 换行"
bcast_huanhang['sections'][0]['params'][0] = {"type": "var", "val": "_unused"}
print("[A3] BroadcastMessageAndWait '换行' → '_unused'")

print("\n=== 改后 cmd=cin body ===")
for i, blk in enumerate(cin_body):
    ps = blk.get('sections', [{}])[0].get('params', [])
    pvals = [p.get('val', '?') for p in ps if isinstance(p, dict)]
    print(f"  [{i}] {blk['define']}  params_vals={pvals}")

# ══════════════════════════════════════════════════════
# B. 法阵的星星2 BS (children[12].children[0]) frag[3]
# ══════════════════════════════════════════════════════
faxing_bs = children[12]['children'][0]
jisu_frag = faxing_bs['fragments'][3]
assert jisu_frag['head']['define'] == 'WhenReceiveMessage', "frag[3] 不是 WhenReceiveMessage！"
jisu_msg = jisu_frag['head']['sections'][0]['params'][0].get('val')
assert jisu_msg == '计算速度', f"frag[3] 消息不是 计算速度，是 {jisu_msg!r}"

jisu_top = get_sections_children(jisu_frag)
# top = [SetVar(x), SetVar(y), Repeat(outer)]
outer_repeat = jisu_top[2]
assert outer_repeat['define'] == 'Repeat', f"top[2] 不是 Repeat，是 {outer_repeat['define']}"

outer_children = outer_repeat['sections'][0]['children']
# outer_children = [inner_Repeat, IncVar(y,11z), IncVar(x,-11), IncVar(y,-0.2), IncVar(z,1)]

print("\n=== 改前 外层 Repeat.children ===")
for i, blk in enumerate(outer_children):
    ps = blk.get('sections', [{}])[0].get('params', [])
    pvals = [p.get('val', '?') for p in ps if isinstance(p, dict)]
    print(f"  [{i}] {blk['define']}  params_vals={pvals[:2]}")

# B1. 在 outer_children[0]（内层 Repeat）之后插入 BroadcastMessageAndWait("换行")
new_broadcast_huanhang = {
    "define": "BroadcastMessageAndWait",
    "sections": [
        {
            "params": [
                {"type": "var", "val": "换行"}
            ]
        }
    ]
}
outer_children.insert(1, new_broadcast_huanhang)
print("\n[B1] BroadcastMessageAndWait('换行') 插入到外层 Repeat.children[1]")

print("\n=== 改后 外层 Repeat.children ===")
for i, blk in enumerate(outer_children):
    ps = blk.get('sections', [{}])[0].get('params', [])
    pvals = [p.get('val', '?') for p in ps if isinstance(p, dict)]
    print(f"  [{i}] {blk['define']}  params_vals={pvals[:2]}")

# ══════════════════════════════════════════════════════
# 保存
# ══════════════════════════════════════════════════════
with open(WS_PATH, 'w', encoding='utf-8') as f:
    json.dump(ws, f, ensure_ascii=False, separators=(',', ':'))

print("\n✅ ws 文件已保存")
print(f"路径：{WS_PATH}")
