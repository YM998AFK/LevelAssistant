"""把 15-2 关卡3 从图1循环版改成图2单次x判断5倍数版。

用户确认：
- intent=A：改成图2（单次 x 判断）
- range=r3：严格 1<=x<=50，超出报错
- legacy=L1：最小化改动，遗留不修
- 后续面板=成长树那套；不通过直接收尾
- 计数机器人保留出现+升级特效
- 不做转身/开大门/机器人开门
- +1 金币动画保留

输出：output/modify/15-2 关卡3-v1.zip
"""
from __future__ import annotations
import copy
import io
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

SRC_ZIP = Path(r"input/15-2 关卡3.zip")
SRC_DIR = Path(r"参考-extracted/15-2 关卡3")
OUT_DIR = Path(r"output/modify")
OUT_ZIP = OUT_DIR / "15-2 关卡3-v2.zip"


# ---------- 积木 JSON 构造工具 ----------
def var(v):
    """字面量参数"""
    return {"type": "var", "val": str(v)}


def block(define, params=None, children=None, nxt=None):
    """构造一个积木 dict。params 是 list（已经 wrap 好的）。children 只接 list。"""
    b = {
        "define": define,
        "sections": [{"params": params or [], "children": children or []}],
    }
    if nxt is not None:
        b["next"] = nxt
    return b


def block_wrap(b):
    """把一个 block 包装成 params 里的 sub-block 槽"""
    return {"type": "block", "val": b}


# 常用嵌套
def Variable(name):
    return block("Variable", [var(name)])


def ListGetItemAt(index, listname):
    # n=2, [index, listname]，无中间 {}
    return block("ListGetItemAt", [var(str(index)), var(listname)])


def Mod(a, b):
    # n=2, [a, b]，无中间 {}
    return block("Mod", [a if isinstance(a, dict) else var(a),
                         b if isinstance(b, dict) else var(b)])


def IsEqual(a, b):
    # n=3, [a, {}, b]
    return block("IsEqual", [
        a if isinstance(a, dict) and "type" in a else block_wrap(a) if isinstance(a, dict) else var(a),
        {},
        b if isinstance(b, dict) and "type" in b else block_wrap(b) if isinstance(b, dict) else var(b),
    ])


def IsGreator(a, b):
    return block("IsGreator", [
        a if (isinstance(a, dict) and a.get("type")) else block_wrap(a) if isinstance(a, dict) else var(a),
        {},
        b if (isinstance(b, dict) and b.get("type")) else block_wrap(b) if isinstance(b, dict) else var(b),
    ])


def IsLess(a, b):
    return block("IsLess", [
        a if (isinstance(a, dict) and a.get("type")) else block_wrap(a) if isinstance(a, dict) else var(a),
        {},
        b if (isinstance(b, dict) and b.get("type")) else block_wrap(b) if isinstance(b, dict) else var(b),
    ])


def Not(x):
    # n=1, [ x ] (LogicalOperator 块)
    return block("Not", [block_wrap(x) if isinstance(x, dict) and x.get("define") else var(x)])


def StrJoin(a, b):
    # n=2
    def wrap(x):
        if isinstance(x, dict) and x.get("define"):
            return block_wrap(x)
        return var(x)
    return block("StrJoin", [wrap(a), wrap(b)])


# 顶层积木
def SetVar(name, value_block):
    # n=2, [name(固), value(值)]
    if isinstance(value_block, dict) and value_block.get("define"):
        return block("SetVar", [var(name), block_wrap(value_block)])
    return block("SetVar", [var(name), var(value_block)])


def BroadcastMessageAndWait(msg):
    return block("BroadcastMessageAndWait", [var(msg)])


def WaitSeconds(sec):
    return block("WaitSeconds", [var(str(sec))])


def ListAdd(item_block, listname):
    # n=2, [item(值), listname(固)]
    if isinstance(item_block, dict) and item_block.get("define"):
        return block("ListAdd", [block_wrap(item_block), var(listname)])
    return block("ListAdd", [var(item_block), var(listname)])


def If(cond_block, body):
    # n=1, [ cond(LogicalOperator block) ]; body -> sections[0].children
    return {
        "define": "If",
        "sections": [{"params": [block_wrap(cond_block)], "children": body}],
    }


def IfElse(cond_block, then_body, else_body):
    # 2 个 sections: [0] 条件+then, [1] 空 params + else
    return {
        "define": "IfElse",
        "sections": [
            {"params": [block_wrap(cond_block)], "children": then_body},
            {"params": [], "children": else_body},
        ],
    }


def chain(blocks):
    """把一串顶层 block 串成 next 链，返回第一块。"""
    if not blocks:
        return None
    head = blocks[0]
    cur = head
    for b in blocks[1:]:
        cur["next"] = b
        cur = b
    return head


# ---------- 定位工具 ----------
def find_node_by_name(scene_children, name):
    for ch in scene_children:
        if isinstance(ch, dict) and ch.get("props", {}).get("Name") == name:
            return ch
    return None


def get_blockscript(node):
    for ch in node.get("children", []):
        if ch.get("type") == "BlockScript":
            return ch
    return None


# ---------- 主修改流程 ----------
def main():
    ws_path = next(SRC_DIR.glob("*.ws"))
    data = json.loads(ws_path.read_text(encoding="utf-8"))

    scene = data["scene"]

    # ========== 改动 1: control 的 "cin判断" handler - 新增 x > 50 校验 ==========
    control_node = find_node_by_name(scene["children"], "control")
    assert control_node, "找不到 control 节点"
    control_bs = get_blockscript(control_node)
    assert control_bs, "control 节点下没有 BlockScript"

    frags = control_bs["fragments"]
    # 找 cin判断 handler（按 define=WhenReceiveMessage 且 param=='cin判断'）
    cin_judge_idx = None
    for i, f in enumerate(frags):
        head = f.get("head", {})
        if head.get("define") == "WhenReceiveMessage":
            params = head.get("sections", [{}])[0].get("params", [])
            if params and isinstance(params[0], dict) and params[0].get("val") == "cin判断":
                cin_judge_idx = i
                break
    assert cin_judge_idx is not None, "找不到 cin判断 handler"

    # 构造新的 cin判断 body：母本规范 —— 所有连续积木都作为 children 平铺（绝不用 next 链）
    if_less_1 = If(
        IsLess(ListGetItemAt(1, "cin_cut"), "1"),
        [
            SetVar("err_msg", "输入的值需要大于等于1哦"),
            BroadcastMessageAndWait("传递失败"),
        ]
    )
    if_greater_50 = If(
        IsGreator(ListGetItemAt(1, "cin_cut"), "50"),
        [
            SetVar("err_msg", "输入的值需要小于等于50哦"),
            BroadcastMessageAndWait("传递失败"),
        ]
    )
    new_cin_judge_body = [if_less_1, if_greater_50]
    frags[cin_judge_idx]["head"]["sections"][0]["children"] = new_cin_judge_body

    # ========== 改动 2: control 的 WhenGameStarts 主演出 (frag 含 SetVar *OJ-Judge='1' 的那个) ==========
    whengame_idx = None
    for i, f in enumerate(frags):
        head = f.get("head", {})
        if head.get("define") != "WhenGameStarts":
            continue
        # 必须有 children
        children = head.get("sections", [{}])[0].get("children", [])
        if not children:
            continue
        # 检查第一块是不是 SetVar *OJ-Judge
        first = children[0]
        if first.get("define") == "SetVar":
            p0 = first.get("sections", [{}])[0].get("params", [])
            if p0 and isinstance(p0[0], dict) and p0[0].get("val") == "*OJ-Judge":
                whengame_idx = i
                break
    assert whengame_idx is not None, "找不到主演出 WhenGameStarts frag"

    # 构造新主演出
    # 开头保留: SetVar *OJ-Judge '1' + ListAdd '50' 'cin_cut' (兜底)
    # 然后 If *OJ-Judge==0 → 传递失败
    # 然后 If *OJ-Judge==1 → 单次演出（不用 IfElse 了，统一单次）
    cin1 = lambda: ListGetItemAt(1, "cin_cut")

    # 母本规范：所有连续积木都是 children 平铺，不能用 next
    single_show_body = [
        BroadcastMessageAndWait("初始化"),
        BroadcastMessageAndWait("机器人发射"),
        WaitSeconds("0.5"),
        SetVar("关卡i", cin1()),
        BroadcastMessageAndWait("屏幕显示"),
        BroadcastMessageAndWait("计算"),
        # 计算完毕后，对勾/叉 已经自行判定。
        # 分支：通过则展开后续面板，不通过直接收尾
        If(
            IsEqual(Mod(Variable("关卡i"), "5"), "0"),
            [
                BroadcastMessageAndWait("+1"),
                BroadcastMessageAndWait("收起"),
                BroadcastMessageAndWait("生成成长树"),
                WaitSeconds("2"),
                BroadcastMessageAndWait("收起成长树"),
            ]
        ),
        If(
            Not(IsEqual(Mod(Variable("关卡i"), "5"), "0")),
            [
                BroadcastMessageAndWait("收起"),
            ]
        ),
    ]

    new_whengame_children = [
        SetVar("*OJ-Judge", "1"),
        ListAdd("50", "cin_cut"),
        If(
            IsEqual(Variable("*OJ-Judge"), "0"),
            [
                SetVar("err_msg", "代码不正确，再试试吧"),
                BroadcastMessageAndWait("传递失败"),
            ]
        ),
        If(
            IsEqual(Variable("*OJ-Judge"), "1"),
            single_show_body
        ),
    ]
    frags[whengame_idx]["head"]["sections"][0]["children"] = new_whengame_children

    # ========== 改动 3: 对勾 的 '判断' handler 拍平 ==========
    duigou_node = find_node_by_name(scene["children"], "对勾")
    assert duigou_node, "找不到 对勾 节点"
    duigou_bs = get_blockscript(duigou_node)
    duigou_frags = duigou_bs["fragments"]
    judge_idx = None
    for i, f in enumerate(duigou_frags):
        head = f.get("head", {})
        if head.get("define") == "WhenReceiveMessage":
            params = head.get("sections", [{}])[0].get("params", [])
            if params and isinstance(params[0], dict) and params[0].get("val") == "判断":
                judge_idx = i
                break
    assert judge_idx is not None, "找不到 对勾 的 判断 handler"

    # 新 body：If Mod(关卡i, 5)==0 → Show/等/Hide/加列表/广播升级（children 平铺）
    new_duigou_body = [
        If(
            IsEqual(Mod(Variable("关卡i"), "5"), "0"),
            [
                block("Show", [{}]),
                WaitSeconds("0.5"),
                block("Hide", [{}]),
                ListAdd(Variable("关卡i"), "角色升级"),
                BroadcastMessageAndWait("角色升级"),
            ]
        )
    ]
    duigou_frags[judge_idx]["head"]["sections"][0]["children"] = new_duigou_body

    # 通用：遍历 children 所有顶层 + 每个顶层的 next 链
    def iter_all_blocks(children):
        for top in children:
            cur = top
            while cur is not None:
                yield cur
                cur = cur.get("next")

    # ========== 改动 4: LabelBubble(5).Basic 的 "初始化" 文案 ==========
    lb5_node = find_node_by_name(scene["children"], "LabelBubble(5).Basic")
    assert lb5_node
    lb5_bs = get_blockscript(lb5_node)
    for f in lb5_bs["fragments"]:
        head = f.get("head", {})
        if head.get("define") != "WhenReceiveMessage":
            continue
        params = head.get("sections", [{}])[0].get("params", [])
        if not (params and isinstance(params[0], dict) and params[0].get("val") == "初始化"):
            continue
        children = head["sections"][0]["children"]
        for b in iter_all_blocks(children):
            if b.get("define") == "SetTitle":
                b["sections"][0]["params"] = [block_wrap(
                    StrJoin("输入 x = ", Variable("关卡n"))
                )]
                break
        break

    # ========== 改动 5: Screen Text.Basic 的 "初始化" 和 "屏幕显示" 文案 ==========
    st_node = find_node_by_name(scene["children"], "Screen Text.Basic")
    assert st_node
    st_bs = get_blockscript(st_node)

    for f in st_bs["fragments"]:
        head = f.get("head", {})
        if head.get("define") != "WhenReceiveMessage":
            continue
        params = head.get("sections", [{}])[0].get("params", [])
        if not (params and isinstance(params[0], dict)):
            continue
        msg = params[0].get("val")
        if msg == "初始化":
            children = head["sections"][0]["children"]
            for b in iter_all_blocks(children):
                if b.get("define") == "SetVar":
                    pp = b["sections"][0]["params"]
                    if pp and isinstance(pp[0], dict) and pp[0].get("val") == "关卡i":
                        b["sections"][0]["params"] = [var("关卡i"), block_wrap(cin1())]
                if b.get("define") == "SetTitle":
                    b["sections"][0]["params"] = [block_wrap(
                        StrJoin("x：", Variable("关卡i"))
                    )]
        elif msg == "屏幕显示":
            children = head["sections"][0]["children"]
            for b in iter_all_blocks(children):
                if b.get("define") == "SetTitle":
                    b["sections"][0]["params"] = [block_wrap(
                        StrJoin("x：", Variable("关卡i"))
                    )]

    # ========== 写回 .ws ==========
    new_ws_text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    # ========== 打包 zip ==========
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if OUT_ZIP.exists():
        raise RuntimeError(f"目标 zip 已存在: {OUT_ZIP}（按 0.6 ③ 禁止覆盖，请递增 v 值）")

    # 从源 zip 复制所有文件，替换 .ws
    with zipfile.ZipFile(SRC_ZIP, "r") as zin, zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.namelist():
            b = zin.read(item)
            if item.endswith(".ws"):
                b = new_ws_text.encode("utf-8")
            zout.writestr(item, b)

    print(f"[OK] 生成: {OUT_ZIP}  size={OUT_ZIP.stat().st_size}")


if __name__ == "__main__":
    main()
