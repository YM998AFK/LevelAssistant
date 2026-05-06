"""
_fix_hanoi_busy.py - 为汉诺塔关卡添加 is_busy 忙标志，防止动画期间并发点击覆盖游戏状态。

问题：BroadcastMessageAndWait("do_anim") 等待 1.2 秒期间，玩家若再次点击底座，
      会启动第二个并发 do_click 处理器，覆盖 moving_disc/src_z/dest_z/final_h 等
      共享变量，导致当前动画错乱（"会覆盖失败"）。

修复：
  1. props2 添加 is_busy 变量（初始 "0"）
  2. WhenGameStarts 末尾添加 SetVar("is_busy","0")
  3. do_click 最外层加 IfElse(is_busy=="0") 守卫
  4. 有效移动序列的 BroadcastMessageAndWait("do_anim") 前后分别
     插入 SetVar("is_busy","1") 和 SetVar("is_busy","0")
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scripts.pkg_utils import pack_zip_clean, clean_backups

WS_PATH = "output/new/汉诺塔挑战_workdir/b8212e928dc647cfb659bc74e0cff402.ws"
OUT_ZIP = "output/new/汉诺塔挑战.zip"
WORKDIR = "output/new/汉诺塔挑战_workdir"

# ── 积木辅助 ──────────────────────────────────────────────────────────────
def lit(val):
    return {"type": "var", "val": str(val)}

def var_ref(name):
    return {"type": "block", "val": {
        "define": "Variable",
        "sections": [{"params": [{"type": "var", "val": name, "name": name}]}]
    }}

def setvar(name, val_param):
    return {"define": "SetVar", "sections": [{"params": [
        {"type": "var", "val": name, "name": name}, val_param
    ]}]}

def isEqual_block(a, b):
    """IsEqual [O] 需要 3 个参数：[a, {}, b]"""
    return {"define": "IsEqual", "sections": [{"params": [a, {}, b]}]}

def ifelse(cond, then_list, else_list=None):
    return {"define": "IfElse", "sections": [
        {"params": [cond], "children": then_list},
        {"params": [], "children": else_list or []}
    ]}

# ── 加载 ws ───────────────────────────────────────────────────────────────
print(f"[fix] 加载 {WS_PATH}")
with open(WS_PATH, encoding='utf-8') as f:
    data = json.load(f)

scene = data["scene"]
children = scene["children"]

# ── 1. props2 添加 is_busy ──────────────────────────────────────────────
props2 = scene.get("props2", {})
if "is_busy" not in props2:
    props2["is_busy"] = {"val": "0", "type": "string"}
    scene["props2"] = props2
    print("[fix] props2 已添加 is_busy")
else:
    print("[fix] props2 is_busy 已存在，跳过")

# ── 定位 ctrl_game 节点 ──────────────────────────────────────────────────
ctrl_game = None
for c in children:
    if c.get("props", {}).get("Name") == "ctrl_game":
        ctrl_game = c
        break
assert ctrl_game, "ctrl_game 节点未找到"

bs = ctrl_game["children"][0]  # BlockScript
frags = bs["fragments"]

def get_frag_children(frag):
    """获取 fragment 的实际 block 列表（在 head.sections[0].children 中）"""
    return frag["head"]["sections"][0]["children"]

def get_frag_msg(frag):
    secs = frag["head"].get("sections", [])
    if secs and secs[0].get("params"):
        return secs[0]["params"][0].get("val", "")
    return ""

# ── 2. WhenGameStarts 末尾加 SetVar("is_busy","0") ──────────────────────
game_start_frag = None
for f in frags:
    if f["head"].get("define") == "WhenGameStarts":
        game_start_frag = f
        break
assert game_start_frag, "WhenGameStarts fragment 未找到"

gs_children = get_frag_children(game_start_frag)
# 检查是否已有 is_busy 初始化
already_init = any(
    c.get("define") == "SetVar" and
    c.get("sections", [{}])[0].get("params", [{}])[0].get("val") == "is_busy"
    for c in gs_children
)
if not already_init:
    gs_children.append(setvar("is_busy", lit("0")))
    print("[fix] WhenGameStarts 已添加 SetVar(is_busy,0)")
else:
    print("[fix] WhenGameStarts 已有 is_busy 初始化，跳过")

# ── 3. do_click fragment：加 is_busy 守卫 ───────────────────────────────
do_click_frag = None
for f in frags:
    if f["head"].get("define") == "WhenReceiveMessage" and get_frag_msg(f) == "do_click":
        do_click_frag = f
        break
assert do_click_frag, "do_click fragment 未找到"

dc_children = get_frag_children(do_click_frag)

# 检查最外层是否已经是 is_busy 守卫
outermost = dc_children[0] if dc_children else {}
is_already_guarded = (
    outermost.get("define") == "IfElse" and
    outermost.get("sections", [{}])[0].get("params", [{}])[0]
              .get("val", {}) if isinstance(outermost.get("sections", [{}])[0]
              .get("params", [{}])[0].get("val", {}), dict) else False
)
# 用更稳定的方式判断：看条件是否包含 is_busy
def has_is_busy_guard(frag_children):
    if not frag_children:
        return False
    outer = frag_children[0]
    if outer.get("define") != "IfElse":
        return False
    cond_params = outer.get("sections", [{}])[0].get("params", [])
    if not cond_params:
        return False
    cond = cond_params[0]
    cond_block = cond.get("val", {}) if cond.get("type") == "block" else {}
    if isinstance(cond_block, dict) and cond_block.get("define") == "IsEqual":
        inner_ps = cond_block.get("sections", [{}])[0].get("params", [])
        for p in inner_ps:
            if p.get("type") == "block":
                vps = p.get("val", {}).get("sections", [{}])[0].get("params", [])
                if vps and vps[0].get("val") == "is_busy":
                    return True
    return False

if has_is_busy_guard(dc_children):
    print("[fix] do_click 已有 is_busy 守卫，跳过外层守卫添加")
    # 需要找到内部的 valid_move_seq 加 is_busy=1/0
    guard_ifelse = dc_children[0]
    inner_logic = guard_ifelse["sections"][0]["children"]
else:
    print("[fix] 为 do_click 添加 is_busy 守卫")
    old_children = list(dc_children)  # copy
    guard_block = ifelse(
        isEqual_block(var_ref("is_busy"), lit("0")),
        old_children,
        []
    )
    dc_children.clear()
    dc_children.append(guard_block)
    inner_logic = guard_block["sections"][0]["children"]

# ── 4. 在 valid_move_seq 里找 BroadcastMessageAndWait("do_anim") ─────────
# 路径: inner_logic[0]=IfElse(sel=="")
#        .sections[1].children[0]=IfElse(clicked==sel)
#          .sections[1].children[4]=IfElse(validate)
#            .sections[0].children = valid_move_seq
def find_valid_move_seq(inner_logic):
    """递归找包含 BroadcastMessageAndWait(do_anim) 的那个 children 列表"""
    for block in inner_logic:
        if not isinstance(block, dict):
            continue
        if block.get("define") == "BroadcastMessageAndWait":
            secs = block.get("sections", [{}])
            if secs and secs[0].get("params", [{}])[0].get("val") == "do_anim":
                return None  # 这个 block 本身就是目标，但我们需要它的 parent list
        for sec in block.get("sections", []):
            ch = sec.get("children", [])
            for i, c in enumerate(ch):
                if (isinstance(c, dict) and
                        c.get("define") == "BroadcastMessageAndWait" and
                        c.get("sections", [{}])[0].get("params", [{}])[0].get("val") == "do_anim"):
                    return ch, i  # (parent list, index of BroadcastMessageAndWait)
            result = find_valid_move_seq(ch)
            if result:
                return result
    return None

result = find_valid_move_seq(inner_logic)
if result is None:
    print("[fix] 未找到 BroadcastMessageAndWait(do_anim)，跳过 is_busy 插入")
else:
    valid_seq, anim_idx = result
    # 检查前一个是否已经是 SetVar(is_busy,1)
    already_before = (anim_idx > 0 and
                      valid_seq[anim_idx - 1].get("define") == "SetVar" and
                      valid_seq[anim_idx - 1].get("sections", [{}])[0].get("params", [{}])[0].get("val") == "is_busy")
    already_after = (anim_idx + 1 < len(valid_seq) and
                     valid_seq[anim_idx + 1].get("define") == "SetVar" and
                     valid_seq[anim_idx + 1].get("sections", [{}])[0].get("params", [{}])[0].get("val") == "is_busy")

    if not already_before:
        valid_seq.insert(anim_idx, setvar("is_busy", lit("1")))
        anim_idx += 1  # index shifted
        print("[fix] 在 do_anim 广播前插入 SetVar(is_busy,1)")
    else:
        print("[fix] is_busy=1 已存在，跳过")

    if not already_after:
        valid_seq.insert(anim_idx + 1, setvar("is_busy", lit("0")))
        print("[fix] 在 do_anim 广播后插入 SetVar(is_busy,0)")
    else:
        print("[fix] is_busy=0 已存在，跳过")

# ── 保存 ws ───────────────────────────────────────────────────────────────
print(f"[fix] 保存 {WS_PATH}")
with open(WS_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

# ── 重新打包 ──────────────────────────────────────────────────────────────
clean_backups(WORKDIR)
pack_zip_clean(WORKDIR, OUT_ZIP)
print(f"[fix] 完成，输出: {OUT_ZIP}")
