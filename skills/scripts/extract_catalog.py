"""
从参考包中提取资源信息和积木块信息，生成：
  1. asset_catalog.md  — 资源 AssetId 总表
  2. blocks_reference.md — 积木块 define 清单 + 参数格式

用法：
  python scripts/extract_catalog.py

会扫描 参考-extracted/ 下所有 .ws 文件，输出到 .cursor/skills/level-generator/
"""
import json, os, re
from collections import defaultdict, Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF_DIR = os.path.join(BASE_DIR, "参考-extracted")
SKILL_DIR = os.path.join(BASE_DIR, ".cursor", "skills", "level-generator")

os.makedirs(SKILL_DIR, exist_ok=True)


def load_all_ws():
    """Load all .ws files from REF_DIR."""
    ws_data = []
    for d in sorted(os.listdir(REF_DIR)):
        fulldir = os.path.join(REF_DIR, d)
        if not os.path.isdir(fulldir):
            continue
        for f in os.listdir(fulldir):
            if f.endswith(".ws"):
                path = os.path.join(fulldir, f)
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                ws_data.append((d, data))
    return ws_data


# ──────────────────────────────────────────────
# Part 1: Asset Catalog
# ──────────────────────────────────────────────

def extract_assets(ws_list):
    """Walk all nodes, collect assets grouped by type."""
    assets = {
        "Scene": {},
        "Character": {},
        "MeshPart": {},
        "Music": {},
        "Sound": {},
        "Effect": {},
        "UIPackageObject": {},
    }

    def walk(node):
        if not isinstance(node, dict):
            return
        ntype = node.get("type", "")
        props = node.get("props", {})
        asset_id = props.get("AssetId")
        name = props.get("Name", "")

        if ntype in assets and asset_id is not None:
            key = asset_id
            if key not in assets[ntype]:
                info = {"Name": name, "AssetId": asset_id}
                if ntype == "Character":
                    info["Scale"] = props.get("Scale", "1")
                if ntype == "MeshPart":
                    info["Visible"] = props.get("Visible", True)
                if ntype in ("Music", "Sound"):
                    info["Loop"] = props.get("Loop", False)
                    info["Is3D"] = props.get("Is3D", False)
                if ntype == "Effect":
                    info["Loop"] = props.get("Loop", False)
                    info["FullScreen"] = props.get("FullScreenBeforeUI", False)
                assets[ntype][key] = info
            else:
                existing = assets[ntype][key]
                if not existing["Name"] and name:
                    existing["Name"] = name

        for child in node.get("children", []):
            walk(child)

    for pkg_name, data in ws_list:
        scene = data.get("scene", {})
        walk(scene)
        walk(data.get("assets", {}))

    return assets


def generate_asset_catalog(assets):
    lines = []
    lines.append("# 盘古3D平台 — 资源 AssetId 总表")
    lines.append("")
    lines.append("> 自动生成，勿手动编辑。运行 `python scripts/extract_catalog.py` 更新。")
    lines.append("")

    # Scene
    lines.append("## 场景 (Scene)")
    lines.append("")
    lines.append("| AssetId | 名称 |")
    lines.append("|---------|------|")
    for aid, info in sorted(assets["Scene"].items()):
        lines.append(f"| {aid} | {info['Name']} |")
    lines.append("")

    # Character
    lines.append("## 角色 (Character)")
    lines.append("")
    lines.append("| AssetId | 名称 | 默认缩放 |")
    lines.append("|---------|------|---------|")
    for aid, info in sorted(assets["Character"].items()):
        lines.append(f"| {aid} | {info['Name']} | {info['Scale']} |")
    lines.append("")

    # MeshPart
    lines.append("## 物件 (MeshPart)")
    lines.append("")
    lines.append("| AssetId | 名称 | 默认可见 |")
    lines.append("|---------|------|---------|")
    for aid, info in sorted(assets["MeshPart"].items()):
        vis = "是" if info["Visible"] else "否"
        lines.append(f"| {aid} | {info['Name']} | {vis} |")
    lines.append("")

    # Music
    lines.append("## 背景音乐 (Music)")
    lines.append("")
    lines.append("| AssetId | 名称 | 循环 |")
    lines.append("|---------|------|------|")
    for aid, info in sorted(assets["Music"].items()):
        loop = "是" if info["Loop"] else "否"
        lines.append(f"| {aid} | {info['Name']} | {loop} |")
    lines.append("")

    # Sound
    lines.append("## 音效 (Sound)")
    lines.append("")
    lines.append("| AssetId | 名称 | 循环 | 3D音效 |")
    lines.append("|---------|------|------|--------|")
    for aid, info in sorted(assets["Sound"].items()):
        loop = "是" if info["Loop"] else "否"
        is3d = "是" if info["Is3D"] else "否"
        lines.append(f"| {aid} | {info['Name']} | {loop} | {is3d} |")
    lines.append("")

    # Effect
    lines.append("## 动画特效 (Effect)")
    lines.append("")
    lines.append("| AssetId | 名称 | 循环 | 全屏 |")
    lines.append("|---------|------|------|------|")
    for aid, info in sorted(assets["Effect"].items()):
        loop = "是" if info["Loop"] else "否"
        fs = "是" if info["FullScreen"] else "否"
        lines.append(f"| {aid} | {info['Name']} | {loop} | {fs} |")
    lines.append("")

    # UI
    lines.append("## UI 包 (UIPackageObject)")
    lines.append("")
    lines.append("| AssetId | 名称 |")
    lines.append("|---------|------|")
    for aid, info in sorted(assets["UIPackageObject"].items()):
        lines.append(f"| {aid} | {info['Name']} |")
    lines.append("")

    return "\n".join(lines)


# ──────────────────────────────────────────────
# Part 2: Blocks Reference
# ──────────────────────────────────────────────

BLOCK_DESCRIPTIONS = {
    "WhenGameStarts": ("事件", "游戏开始时触发"),
    "WhenStartup": ("事件", "场景初始化时触发（早于 WhenGameStarts）"),
    "WhenReceiveMessage": ("事件", "收到广播消息时触发"),
    "WhenIStartAsAClone": ("事件", "作为克隆体启动时触发"),
    "BroadcastMessage": ("事件", "广播消息（不等待）"),
    "BroadcastMessageAndWait": ("事件", "广播消息并等待所有处理器完成"),
    "SetVar": ("变量", "设置变量值"),
    "IncVar": ("变量", "变量递增指定值"),
    "Variable": ("变量", "读取变量值（表达式块）"),
    "ListAdd": ("变量", "向列表添加元素"),
    "ListDeleteALl": ("变量", "清空列表"),
    "ListGetItemAt": ("变量", "获取列表指定位置的元素"),
    "ListGetLength": ("变量", "获取列表长度"),
    "If": ("控制", "条件判断"),
    "IfElse": ("控制", "条件判断（含否则分支）"),
    "Repeat": ("控制", "重复执行 N 次"),
    "Forever": ("控制", "永远循环执行"),
    "WaitSeconds": ("控制", "等待指定秒数"),
    "WaitUntil": ("控制", "等待直到条件为真"),
    "StopScript": ("控制", "停止脚本（'all' / 'other scripts in sprite'）"),
    "CreateCloneOf": ("控制", "创建克隆体"),
    "DeleteThisClone": ("控制", "删除当前克隆体"),
    "GotoPosition3D": ("运动", "瞬移到3D坐标（仅用于初始化）"),
    "GotoPosition2D": ("运动", "瞬移到2D坐标"),
    "GotoTarget": ("运动", "瞬移到目标物件位置"),
    "GotoFrontBack": ("运动", "瞬移到物件前方/后方（'front'/'back'）"),
    "RunToTargetAndWait": ("运动", "跑向目标物件并等待到达（有跑步动画）"),
    "GlideSecsToPosition3D": ("运动", "在N秒内滑动到3D坐标"),
    "GlideSecsToPosition2D": ("运动", "在N秒内滑动到2D坐标"),
    "GlideSecsToPosition3DAndSetRotation": ("运动", "滑动到3D坐标并设置旋转"),
    "PointInDirection": ("运动", "设置水平朝向角度（0=Y+, 90=X+, -90=X-, 180=Y-）"),
    "PointInPitch": ("运动", "设置俯仰角度"),
    "SetSpeedMul": ("运动", "设置移动速度倍率"),
    "SetPosX": ("运动", "设置 X 坐标"),
    "SetPosY": ("运动", "设置 Y 坐标"),
    "SetPosZ": ("运动", "设置 Z 坐标"),
    "ChangePosX": ("运动", "改变 X 坐标（增量）"),
    "ChangePosY": ("运动", "改变 Y 坐标（增量）"),
    "ChangePosZ": ("运动", "改变 Z 坐标（增量）"),
    "GetPosX": ("运动", "获取 X 坐标（表达式块）"),
    "GetPosY": ("运动", "获取 Y 坐标（表达式块）"),
    "GetPosZ": ("运动", "获取 Z 坐标（表达式块）"),
    "SetSize": ("外观", "设置大小"),
    "ChangeSize": ("外观", "改变大小（增量）"),
    "Show": ("外观", "显示"),
    "Hide": ("外观", "隐藏"),
    "SwitchCostume": ("外观", "切换造型"),
    "SetTitle": ("外观", "设置 UI 标签文字"),
    "ShowLabel": ("外观", "显示标签"),
    "HideLabel": ("外观", "隐藏标签"),
    "SaySeconds": ("外观", "说话气泡持续N秒"),
    "SetSaySkin": ("外观", "设置说话气泡皮肤"),
    "PlayAnimation": ("动画", "播放动画（不等待结束）"),
    "PlayAnimationUntil": ("动画", "播放动画并等待结束"),
    "StopAnimation": ("动画", "停止动画"),
    "SetAnimationSpeed": ("动画", "设置动画播放速度"),
    "FollowNode": ("动画", "跟随骨骼节点"),
    "PlayBGM": ("声音", "播放背景音乐"),
    "PlaySound": ("声音", "播放音效"),
    "PlaySoundUntil": ("声音", "播放音效并等待结束"),
    "StopAllSound": ("声音", "停止所有声音"),
    "SetVolumeTo": ("声音", "设置音量"),
    "SetCameraFOV": ("摄像机", "设置摄像机视野角度"),
    "CameraFollow": ("摄像机", "摄像机跟随目标"),
    "TransitToCameraPreset": ("摄像机", "切换到摄像机预设视角"),
    "SetControllerState": ("场景", "设置控制器状态"),
    "EndRun": ("场景", "结束运行（OJ结果提交）"),
    "IsEqual": ("运算", "等于判断"),
    "IsGreator": ("运算", "大于判断"),
    "IsLess": ("运算", "小于判断"),
    "And": ("运算", "逻辑与"),
    "Or": ("运算", "逻辑或"),
    "Not": ("运算", "逻辑非"),
    "Add": ("运算", "加法"),
    "Subtract": ("运算", "减法"),
    "Multiply": ("运算", "乘法"),
    "Divide": ("运算", "除法"),
    "Mod": ("运算", "取余"),
    "Round": ("运算", "四舍五入"),
    "MathFunc": ("运算", "数学函数"),
    "PickRandom": ("运算", "随机数"),
    "StrJoin": ("字符串", "字符串拼接"),
    "StrLength": ("字符串", "字符串长度"),
    "StrLetterOf": ("字符串", "获取第N个字符"),
    "StrContains": ("字符串", "字符串包含判断"),
}


def extract_blocks(ws_list):
    """Walk all fragments, collect block define names with param examples."""
    block_usage = Counter()
    block_params = defaultdict(list)

    def walk_frag(node):
        if not isinstance(node, dict):
            return
        define = node.get("define", "")
        if define and "myblockdefine" not in define:
            block_usage[define] += 1
            sections = node.get("sections", [])
            if sections:
                params = sections[0].get("params", [])
                param_summary = []
                for p in params:
                    if isinstance(p, dict):
                        if p.get("type") == "var":
                            param_summary.append(f'"{p.get("val", "")}"')
                        elif p.get("type") == "block":
                            param_summary.append("<表达式>")
                        else:
                            param_summary.append("_")
                    else:
                        param_summary.append("_")
                if param_summary and len(block_params[define]) < 3:
                    block_params[define].append(param_summary)

            if "next" in node:
                walk_frag(node["next"])
            for s in sections:
                for c in s.get("children", []):
                    walk_frag(c)
                for p in s.get("params", []):
                    if isinstance(p, dict) and p.get("type") == "block":
                        walk_frag(p.get("val", {}))

    for pkg_name, data in ws_list:
        scene = data.get("scene", {})

        def walk_node(node):
            if not isinstance(node, dict):
                return
            for frag in node.get("fragments", []):
                walk_frag(frag.get("head", {}))
            for child in node.get("children", []):
                walk_node(child)

        walk_node(scene)

    return block_usage, block_params


def generate_blocks_reference(block_usage, block_params):
    lines = []
    lines.append("# 盘古3D平台 — 积木块 (Block) 参考手册")
    lines.append("")
    lines.append("> 自动生成，勿手动编辑。运行 `python scripts/extract_catalog.py` 更新。")
    lines.append("")

    categories = defaultdict(list)
    uncategorized = []

    for define in sorted(block_usage.keys()):
        if define in BLOCK_DESCRIPTIONS:
            cat, desc = BLOCK_DESCRIPTIONS[define]
            categories[cat].append((define, desc, block_usage[define]))
        else:
            uncategorized.append((define, block_usage[define]))

    cat_order = ["事件", "控制", "运动", "外观", "动画", "声音", "摄像机", "场景", "变量", "运算", "字符串"]

    for cat in cat_order:
        if cat not in categories:
            continue
        lines.append(f"## {cat}")
        lines.append("")
        lines.append("| 积木 (define) | 说明 | 使用次数 | 参数示例 |")
        lines.append("|--------------|------|---------|---------|")
        for define, desc, count in categories[cat]:
            examples = block_params.get(define, [])
            param_str = ""
            if examples:
                param_str = "(" + ", ".join(examples[0]) + ")"
            lines.append(f"| `{define}` | {desc} | {count} | {param_str} |")
        lines.append("")

    if uncategorized:
        lines.append("## 其他 / 自定义")
        lines.append("")
        lines.append("| 积木 (define) | 使用次数 |")
        lines.append("|--------------|---------|")
        for define, count in uncategorized:
            lines.append(f"| `{define}` | {count} |")
        lines.append("")

    return "\n".join(lines)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    print(f"扫描目录: {REF_DIR}")
    ws_list = load_all_ws()
    print(f"加载了 {len(ws_list)} 个 .ws 文件")

    # Asset Catalog
    assets = extract_assets(ws_list)
    total = sum(len(v) for v in assets.values())
    print(f"提取到 {total} 个唯一资源")
    catalog_md = generate_asset_catalog(assets)
    catalog_path = os.path.join(SKILL_DIR, "asset_catalog.md")
    with open(catalog_path, "w", encoding="utf-8") as f:
        f.write(catalog_md)
    print(f"已写入: {catalog_path}")

    # Blocks Reference
    block_usage, block_params = extract_blocks(ws_list)
    print(f"提取到 {len(block_usage)} 种积木块")
    blocks_md = generate_blocks_reference(block_usage, block_params)
    blocks_path = os.path.join(SKILL_DIR, "blocks_reference.md")
    with open(blocks_path, "w", encoding="utf-8") as f:
        f.write(blocks_md)
    print(f"已写入: {blocks_path}")

    print("\n完成！")


if __name__ == "__main__":
    main()
