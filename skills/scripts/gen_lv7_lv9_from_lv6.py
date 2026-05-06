"""基于练习6 母本（参考-未发布版本.zip / 测试-未发布版本目录）生成练习7 和 练习9 的关卡包。

母本真相（看完 36 个 BlockScript fragments 后确认）：
  - control 物件是总控制器，用 cid 变量决定走哪条分支
    cid=1 → 压缩饼干（通用 i 位置） → 对应练习6
    cid=2 → 矿泉水（手写 i=2/3/4 位置） → 对应练习9
    cid=3 → 医药包（通用 i 位置） → 对应练习7
  - 主循环在 control.fragments[2] WhenReceiveMessage('展示关卡效果')
      SetVar cid / SetVar i / Repeat N
  - WhenGameStarts 里 control.fragments[0] 先 SetVar cid，得同步改
  - 小核桃台词里已经写好 cid=1 说 "0~9 号"、else 说 "2~5 号"，不需要改

改动点：
  练习7 (医药包 cid=3，检查 2-5)：
    WhenGameStarts: SetVar('cid','1') → '3'
    展示关卡效果:
      SetVar('cid','1') → '3'
      SetVar('i','0')   → '2'
      Repeat('2')       → '4'
  练习9 (矿泉水 cid=2，检查 2-5)：
    同上，cid 改 '2'，i 改 '2'，Repeat 改 '4'
    额外补 矿泉水.fragments[1] 里 i=5 的分支（1997 + 30*(5-2) = 2087 的位置）
  solution.json 的 name + project uuid 也要更新

输出：
  output/检查物资箱-练习7-v2.zip
  output/检查物资箱-练习9-v2.zip
"""
from __future__ import annotations

import copy
import json
import shutil
import uuid
import zipfile
from pathlib import Path

ROOT = Path(r"c:\Users\Hetao\Desktop\公司")
MOTHER_DIR = ROOT / "参考-extracted" / "测试-未发布版本"
# 按 SKILL.md Path Conventions：修改关卡 → output/modify/{原包名}-v{N}.zip
OUTPUT_DIR = ROOT / "output" / "modify"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
# 打包时的临时工作目录放到 参考-extracted/，不污染 output/
TMP_DIR = ROOT / "参考-extracted" / "_build_tmp"


# -------- 积木查找/修改工具 --------

def walk_all_nodes(node):
    """递归 yield 所有节点。"""
    if not isinstance(node, dict):
        return
    yield node
    for c in node.get("children", []) or []:
        yield from walk_all_nodes(c)


def find_by_type_and_name(scene, node_type: str, name: str):
    for n in walk_all_nodes(scene):
        if n.get("type") == node_type and n.get("props", {}).get("Name") == name:
            return n
    return None


def is_setvar(block, var_name: str) -> bool:
    """判断积木是 SetVar(var_name, ...) 吗。"""
    if not isinstance(block, dict):
        return False
    if block.get("define") != "SetVar":
        return False
    params = block.get("sections", [{}])[0].get("params", [])
    if not params:
        return False
    p0 = params[0]
    return isinstance(p0, dict) and p0.get("val") == var_name


def get_setvar_value(block) -> str | None:
    params = block.get("sections", [{}])[0].get("params", [])
    if len(params) < 2:
        return None
    p1 = params[1]
    if isinstance(p1, dict):
        return p1.get("val")
    return None


def set_setvar_value(block, new_val: str):
    params = block.get("sections", [{}])[0].get("params", [])
    params[1]["val"] = new_val


def is_repeat(block) -> bool:
    return isinstance(block, dict) and block.get("define") == "Repeat"


def set_repeat_count(block, new_val: str):
    params = block.get("sections", [{}])[0].get("params", [])
    params[0]["val"] = new_val


def walk_block_tree(block):
    """递归 yield 积木树里所有节点（一个 fragment head 往下）"""
    if not isinstance(block, dict):
        return
    yield block
    for sec in block.get("sections", []) or []:
        for p in sec.get("params", []) or []:
            if isinstance(p, dict) and p.get("type") == "block":
                val = p.get("val")
                if val:
                    yield from walk_block_tree(val)
        for c in sec.get("children", []) or []:
            yield from walk_block_tree(c)


def fragments_of(block_script):
    return block_script.get("fragments", []) or []


# -------- 核心改造 --------

def modify_control(control_script, target_cid: str, start_i: str, repeat_n: str):
    """修改 control 物件的 BlockScript：
    - WhenGameStarts 分支 SetVar('cid', ...) 改成 target_cid
    - WhenReceiveMessage('展示关卡效果') 分支 SetVar('cid',...)/SetVar('i',...)/Repeat(...) 改掉
    """
    for frag in fragments_of(control_script):
        head = frag.get("head")
        if not head:
            continue

        if head.get("define") == "WhenGameStarts":
            # 其 children 里会包含 SetVar('cid', '1')
            for blk in walk_block_tree(head):
                if is_setvar(blk, "cid") and get_setvar_value(blk) == "1":
                    set_setvar_value(blk, target_cid)
                    break

        elif head.get("define") == "WhenReceiveMessage":
            # 要匹配 WhenReceiveMessage('展示关卡效果')
            params = head.get("sections", [{}])[0].get("params", [])
            if not params:
                continue
            p0 = params[0]
            if not (isinstance(p0, dict) and p0.get("val") == "展示关卡效果"):
                continue
            for blk in walk_block_tree(head):
                if is_setvar(blk, "cid"):
                    set_setvar_value(blk, target_cid)
                elif is_setvar(blk, "i"):
                    set_setvar_value(blk, start_i)
                elif is_repeat(blk):
                    set_repeat_count(blk, repeat_n)


def patch_box6_animation(scene):
    """修复母本遗留 bug：物资箱带动画 6 的"关闭物资箱"是空事件，
    "打开物资"事件缺失，且存在一个孤立的 `If i==6 PlayAnimation('bihe_idle')`
    片段没挂到任何事件。

    策略：以物资箱带动画 5 的 `打开物资`/`关闭物资箱` 两个 fragment 为
    模板克隆过来，把里面的 i 值 +1（5→6, 4→5），替换掉物资箱6 的
    空"关闭物资箱" fragment 并新增"打开物资" fragment。孤立的 If 片段
    删除（避免重复）。

    返回 True 表示确实改动了。
    """
    box5 = find_by_type_and_name(scene, "MeshPart", "物资箱带动画 5")
    box6 = find_by_type_and_name(scene, "MeshPart", "物资箱带动画 6")
    if not box5 or not box6:
        return False

    box5_bs = next((c for c in box5.get("children", []) or []
                    if c.get("type") == "BlockScript"), None)
    box6_bs = next((c for c in box6.get("children", []) or []
                    if c.get("type") == "BlockScript"), None)
    if not box5_bs or not box6_bs:
        return False

    # 从 box5 找两个模板 fragment
    tpl_close = None   # 关闭物资箱 / If i==5
    tpl_open = None    # 打开物资 / If i==4
    for frag in fragments_of(box5_bs):
        head = frag.get("head")
        if not head or head.get("define") != "WhenReceiveMessage":
            continue
        p0 = head.get("sections", [{}])[0].get("params", [{}])[0]
        msg = p0.get("val") if isinstance(p0, dict) else None
        if msg == "关闭物资箱":
            tpl_close = frag
        elif msg == "打开物资":
            tpl_open = frag
    if not tpl_close or not tpl_open:
        return False

    def clone_and_bump_i(frag, new_i_val: str, new_pos: list[str]):
        new_frag = copy.deepcopy(frag)
        new_frag["pos"] = list(new_pos)
        # head -> sections[0].children -> [If ...]
        children = new_frag["head"]["sections"][0]["children"]
        for if_blk in children:
            if if_blk.get("define") != "If":
                continue
            cond = if_blk["sections"][0]["params"][0]
            if not (isinstance(cond, dict) and cond.get("type") == "block"):
                continue
            is_equal = cond["val"]
            if is_equal.get("define") != "IsEqual":
                continue
            rhs = is_equal["sections"][0]["params"][2]
            if isinstance(rhs, dict):
                rhs["val"] = new_i_val
        return new_frag

    # 构造 box6 的两个新 fragment
    new_close = clone_and_bump_i(tpl_close, "6", ["1367.111", "345.6667"])
    new_open = clone_and_bump_i(tpl_open, "5", ["970.1111", "360.6667"])

    # 重建 box6 的 fragments：保留初始化，替换/新增打开关闭，丢弃孤立 If
    new_fragments = []
    has_init = False
    for frag in fragments_of(box6_bs):
        head = frag.get("head")
        if not head:
            continue
        define = head.get("define")
        if define == "WhenReceiveMessage":
            p0 = head.get("sections", [{}])[0].get("params", [{}])[0]
            msg = p0.get("val") if isinstance(p0, dict) else None
            if msg == "初始化":
                new_fragments.append(frag)
                has_init = True
            # 丢弃原来空壳的"关闭物资箱"事件
            continue
        if define == "If":
            # 丢弃孤立的 If i==6 片段
            continue
        new_fragments.append(frag)

    new_fragments.append(new_open)
    new_fragments.append(new_close)
    box6_bs["fragments"] = new_fragments
    return has_init  # 只要原初始化还在就算成功


def patch_mineral_water_i5(mineral_script):
    """给矿泉水脚本的 '打开物资' 事件里补一个 i=5 的分支，
    防止练习9 第4轮循环时矿泉水卡在 4 号箱位置。
    """
    for frag in fragments_of(mineral_script):
        head = frag.get("head")
        if not head:
            continue
        if head.get("define") != "WhenReceiveMessage":
            continue
        params = head.get("sections", [{}])[0].get("params", [])
        if not (params and isinstance(params[0], dict) and params[0].get("val") == "打开物资"):
            continue
        # 找到 If cid==2 的块，在它的 children 里找 If i==4 那一项，clone 一份改成 i=5
        # head > sections[0].children = [ If(cid==2) > sections[0].children = [If i==2, If i==3, If i==4, Show] ]
        outer_children = head.get("sections", [{}])[0].get("children", [])
        for outer_blk in outer_children:
            if not isinstance(outer_blk, dict) or outer_blk.get("define") != "If":
                continue
            # 确认 If 条件是 IsEqual(cid, 2)
            if_params = outer_blk.get("sections", [{}])[0].get("params", [])
            if not if_params:
                continue
            cond = if_params[0]
            if not (isinstance(cond, dict) and cond.get("type") == "block"):
                continue
            cond_blk = cond.get("val", {})
            if cond_blk.get("define") != "IsEqual":
                continue
            cond_params = cond_blk.get("sections", [{}])[0].get("params", [])
            if len(cond_params) < 3:
                continue
            val_side = cond_params[2]
            if not (isinstance(val_side, dict) and val_side.get("val") == "2"):
                continue
            # 确认内部有 If i==4
            inner_children = outer_blk.get("sections", [{}])[0].get("children", [])
            target = None
            target_idx = None
            already_has_5 = False
            for idx, ic in enumerate(inner_children):
                if not isinstance(ic, dict) or ic.get("define") != "If":
                    continue
                ic_params = ic.get("sections", [{}])[0].get("params", [])
                if not ic_params:
                    continue
                ic_cond = ic_params[0]
                if not (isinstance(ic_cond, dict) and ic_cond.get("type") == "block"):
                    continue
                ic_cond_blk = ic_cond.get("val", {})
                if ic_cond_blk.get("define") != "IsEqual":
                    continue
                ic_cond_params = ic_cond_blk.get("sections", [{}])[0].get("params", [])
                if len(ic_cond_params) < 3:
                    continue
                i_side = ic_cond_params[2]
                if isinstance(i_side, dict):
                    if i_side.get("val") == "4":
                        target = ic
                        target_idx = idx
                    elif i_side.get("val") == "5":
                        already_has_5 = True
            if target and not already_has_5:
                # 克隆 i=4 的块，改成 i=5，Goto 的 Y 轴加 30
                new_blk = copy.deepcopy(target)
                # 改条件值
                new_cond_params = new_blk["sections"][0]["params"][0]["val"]["sections"][0]["params"]
                new_cond_params[2]["val"] = "5"
                # 改内部的 GotoPosition3D
                for sub in new_blk["sections"][0].get("children", []) or []:
                    if sub.get("define") == "GotoPosition3D":
                        g_params = sub["sections"][0]["params"]
                        # g_params[1] 是 Y，原来 2055，加 30 → 2085
                        if len(g_params) >= 2 and isinstance(g_params[1], dict):
                            try:
                                cur = float(g_params[1].get("val", "0"))
                                g_params[1]["val"] = str(cur + 30)
                            except ValueError:
                                pass
                    elif sub.get("define") == "SetSize":
                        # 保持和 i=4 一样的 120
                        pass
                # 插在 i=4 后面
                inner_children.insert(target_idx + 1, new_blk)
                return True
    return False


# -------- 关卡级别改造流程 --------

def build_level(target_cid: str, level_name: str, zip_name: str, patch_mineral: bool = False):
    """从母本目录拷贝一份，做 ws + solution.json 改造，重新打包成 zip。"""
    work_dir = TMP_DIR / zip_name
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    # 1. 拷贝全部母本文件
    for f in MOTHER_DIR.iterdir():
        shutil.copy2(f, work_dir / f.name)

    # 2. 读 ws（是母本 .ws 文件名）
    ws_file = next(work_dir.glob("*.ws"))
    data = json.loads(ws_file.read_text(encoding="utf-8"))
    scene = data["scene"]

    # 3. 找 control 物件的 BlockScript，修改主控逻辑
    control_node = find_by_type_and_name(scene, "MeshPart", "control")
    if not control_node:
        raise RuntimeError("找不到 control MeshPart")
    control_scripts = [c for c in control_node.get("children", []) or []
                       if c.get("type") == "BlockScript"]
    if not control_scripts:
        raise RuntimeError("control 下没有 BlockScript 子节点")
    modify_control(control_scripts[0], target_cid=target_cid,
                   start_i="2", repeat_n="4")

    # 4. 修复物资箱 6（5 号箱）的打开/关闭动画（母本遗留 bug）
    box6_patched = patch_box6_animation(scene)
    print(f"  物资箱6 动画补丁: {'已应用' if box6_patched else '未应用'}")

    # 5. 可选：补矿泉水 i=5 分支
    if patch_mineral:
        mineral_node = find_by_type_and_name(scene, "MeshPart", "矿泉水")
        if mineral_node:
            for c in mineral_node.get("children", []) or []:
                if c.get("type") == "BlockScript":
                    patched = patch_mineral_water_i5(c)
                    print(f"  矿泉水 i=5 补丁: {'已应用' if patched else '未应用'}")
                    break

    # 5. 写回 ws
    ws_file.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    # 6. 改 solution.json 的 name + uuid
    sol_file = work_dir / "solution.json"
    sol = json.loads(sol_file.read_text(encoding="utf-8"))
    sol["name"] = level_name
    if sol.get("projects"):
        sol["projects"][0]["uuid"] = str(uuid.uuid4())
    sol_file.write_text(
        json.dumps(sol, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    # 7. 打包 zip
    zip_path = OUTPUT_DIR / f"{zip_name}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in work_dir.iterdir():
            zf.write(f, arcname=f.name)
    print(f"  已输出: {zip_path}  ({zip_path.stat().st_size} 字节)")

    return zip_path


def main():
    print("== 生成 练习7（医药包，cid=3，检查 2-5）==")
    build_level(
        target_cid="3",
        level_name="检查物资箱-练习7",
        zip_name="检查物资箱-练习7-v2",
    )
    print()
    print("== 生成 练习9（矿泉水，cid=2，检查 2-5）==")
    build_level(
        target_cid="2",
        level_name="检查物资箱-练习9",
        zip_name="检查物资箱-练习9-v2",
        patch_mineral=True,
    )
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)


if __name__ == "__main__":
    main()
