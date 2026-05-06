"""分析参考包 OJ 判题逻辑差异，对题型进行分类。"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(r"c:\Users\Administrator\Desktop\公司\参考-extracted")


def find_ws_file(directory: Path) -> Path | None:
    for f in directory.iterdir():
        if f.suffix == ".ws":
            return f
    return None


def flatten_block(node: dict, depth: int = 0) -> str:
    """将嵌套的 block 结构递归展平为可读的伪代码字符串。"""
    if not isinstance(node, dict):
        return str(node)

    define = node.get("define", "")
    sections = node.get("sections", [])
    next_node = node.get("next")

    parts = [" " * depth + define]

    for sec in sections:
        params = sec.get("params", [])
        param_strs = []
        for p in params:
            if isinstance(p, dict):
                if p.get("type") == "var":
                    param_strs.append(p["val"])
                elif p.get("type") == "block":
                    param_strs.append(flatten_block(p["val"], 0))
                else:
                    param_strs.append(str(p))
            else:
                param_strs.append(str(p))
        if param_strs:
            parts[0] += f"({', '.join(param_strs)})"

        children = sec.get("children", [])
        for child in children:
            parts.append(flatten_block(child, depth + 2))

    if next_node:
        parts.append(flatten_block(next_node, depth))

    return "\n".join(parts)


def find_objects_recursive(node: dict, results: list, name_filter=None):
    """在 scene 树中递归查找物件。"""
    name = node.get("props", {}).get("Name", "")
    if name_filter is None or name_filter(name):
        results.append(node)
    for child in node.get("children", []):
        find_objects_recursive(child, results, name_filter)


def extract_message_handler(fragments: list[dict], message_name: str) -> list[str]:
    """从 fragments 中提取指定消息处理器的伪代码。"""
    handlers = []
    for frag in fragments:
        head = frag.get("head", {})
        code = _search_message_in_block(head, message_name)
        if code:
            handlers.append(code)
    return handlers


def _search_message_in_block(node: dict, message_name: str, depth: int = 0) -> str | None:
    """在 block 树中查找 WhenReceiveMessage 并匹配消息名。"""
    if not isinstance(node, dict):
        return None

    define = node.get("define", "")
    sections = node.get("sections", [])
    next_node = node.get("next")

    if define == "WhenReceiveMessage":
        for sec in sections:
            params = sec.get("params", [])
            for p in params:
                if isinstance(p, dict) and p.get("type") == "var" and p.get("val") == message_name:
                    return flatten_block(node)

    for sec in sections:
        for child in sec.get("children", []):
            result = _search_message_in_block(child, message_name, depth + 1)
            if result:
                return result

    if next_node:
        result = _search_message_in_block(next_node, message_name, depth)
        if result:
            return result

    return None


def extract_all_fragments_code(fragments: list[dict]) -> list[str]:
    """将所有 fragments 转为伪代码列表。"""
    codes = []
    for frag in fragments:
        head = frag.get("head", {})
        codes.append(flatten_block(head))
    return codes


def extract_variables(scene_props2: dict) -> dict[str, Any]:
    """提取 scene 级别的变量定义。"""
    variables = {}
    for key, val in scene_props2.items():
        if key.startswith("#") or key.startswith("@"):
            continue
        variables[key] = val
    return variables


def extract_events(scene_props2: dict) -> list[str]:
    """提取事件列表。"""
    evt = scene_props2.get("#EVENT", {})
    return evt.get("value", [])


def analyze_cin_logic(code: str) -> dict:
    """分析 cin判断 逻辑，提取关键检查项。"""
    info = {
        "input_count_check": None,
        "range_check": None,
        "decimal_check": False,
        "char_check": False,
        "error_messages": [],
        "raw_code": code,
    }

    count_match = re.search(r'ListGetLength.*?cin_cut.*?(\d+)', code)
    if count_match:
        info["input_count_check"] = int(count_match.group(1))

    count_matches = re.findall(r'ListGetLength\(cin_cut\).*?(\d+)', code)
    if count_matches:
        info["input_count_check"] = int(count_matches[0])

    range_patterns = []
    greater_matches = re.findall(r'IsGreator\(.*?,\s*(-?\d+\.?\d*)\)', code)
    less_matches = re.findall(r'IsLess\(.*?,\s*(-?\d+\.?\d*)\)', code)
    if greater_matches or less_matches:
        for g in greater_matches:
            range_patterns.append(f">{g}")
        for l in less_matches:
            range_patterns.append(f"<{l}")
        info["range_check"] = ", ".join(range_patterns)

    if "StrContains" in code and '"."' in code or "." in code:
        if "StrContains" in code:
            info["decimal_check"] = True

    err_matches = re.findall(r'SetVar\(err_msg,\s*(.+?)\)', code)
    info["error_messages"] = err_matches

    if any("字符" in m or "char" in m.lower() or "字母" in m for m in info["error_messages"]):
        info["char_check"] = True
    if any("一个字符" in m or "单个字符" in m for m in info["error_messages"]):
        info["char_check"] = True

    return info


def analyze_cout_logic(code: str) -> dict:
    """分析 cout判断 逻辑。"""
    info = {
        "has_handler": bool(code and code.strip()),
        "checks_output": False,
        "error_messages": [],
        "raw_code": code,
    }

    if not code:
        return info

    if "ListGetLength" in code or "IsEqual" in code or "cout_cut" in code:
        info["checks_output"] = True

    err_matches = re.findall(r'SetVar\(err_msg,\s*(.+?)\)', code)
    info["error_messages"] = err_matches

    return info


def analyze_effect_logic(code: str) -> dict:
    """分析展示关卡效果逻辑。"""
    info = {
        "has_handler": bool(code and code.strip()),
        "uses_cin_cut": "cin_cut" in (code or ""),
        "uses_cout_cut": "cout_cut" in (code or ""),
        "broadcasts": [],
        "raw_code": code,
    }

    if code:
        bc_matches = re.findall(r'BroadcastMessage(?:AndWait)?\((.+?)\)', code)
        info["broadcasts"] = bc_matches

    return info


def classify_type(cin_info: dict, variables: dict, events: list, all_code: str) -> tuple[str, str]:
    """根据 cin 逻辑和变量推断题型。返回 (类型, 原因)。"""
    err_msgs = " ".join(cin_info.get("error_messages", []))
    raw = cin_info.get("raw_code", "")

    if "字符" in err_msgs or "char" in err_msgs.lower() or "字母" in err_msgs:
        return "char", "cin判断错误消息提到字符/字母"

    if cin_info.get("char_check"):
        return "char", "cin判断包含字符类型检查"

    if "StrLength" in raw and "1" in raw and "ListGetLength" not in raw:
        if "IsEqual" in raw:
            return "char", "检查输入长度为1（单字符）"

    input_count = cin_info.get("input_count_check")
    if input_count is not None and input_count > 1:
        return "数组", f"要求输入{input_count}个数据"

    if "答案列表" in str(variables) or "答案个数" in str(variables):
        if input_count is None or input_count != 1:
            return "数组", "使用了答案列表/答案个数变量"

    list_vars = [k for k in variables if "列表" in k or "list" in k.lower()]
    if list_vars and input_count != 1:
        pass

    if cin_info.get("decimal_check"):
        return "int", "检查小数点（要求整数）"

    if cin_info.get("range_check"):
        return "int", f"有范围检查: {cin_info['range_check']}"

    if "整数" in err_msgs:
        return "int", "错误消息提到整数"

    if "数字" in err_msgs:
        return "int", "错误消息提到数字"

    if input_count == 1:
        return "int", "只要求输入1个值（默认归类为int）"

    return "其他", "无法确定输入类型"


def analyze_package(pkg_dir: Path) -> dict:
    """分析单个参考包。"""
    ws_file = find_ws_file(pkg_dir)
    if not ws_file:
        return {"name": pkg_dir.name, "error": "未找到 .ws 文件"}

    with open(ws_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    scene = data.get("scene", {})
    scene_props2 = scene.get("props2", {})

    variables = extract_variables(scene_props2)
    events = extract_events(scene_props2)

    control_objects = []
    find_objects_recursive(scene, control_objects, lambda n: "control" in n.lower())

    all_objects = []
    find_objects_recursive(scene, all_objects)

    data_objects = []
    find_objects_recursive(scene, data_objects, lambda n: "分割数据" in n)

    result = {
        "name": pkg_dir.name,
        "ws_name": data.get("name", ""),
        "variables": list(variables.keys()),
        "events": events,
        "control_count": len(control_objects),
        "cin_handlers": [],
        "cout_handlers": [],
        "effect_handlers": [],
        "cin_analysis": {},
        "cout_analysis": {},
        "effect_analysis": {},
        "type": "未知",
        "type_reason": "",
        "all_control_code": "",
    }

    all_cin_code = []
    all_cout_code = []
    all_effect_code = []
    all_control_code_parts = []

    search_objects = control_objects + data_objects + all_objects

    for obj in search_objects:
        for child in obj.get("children", []):
            if child.get("type") != "BlockScript":
                continue
            fragments = child.get("fragments", [])
            for msg in ["cin判断"]:
                handlers = extract_message_handler(fragments, msg)
                all_cin_code.extend(handlers)
            for msg in ["cout判断"]:
                handlers = extract_message_handler(fragments, msg)
                all_cout_code.extend(handlers)
            for msg in ["展示关卡效果"]:
                handlers = extract_message_handler(fragments, msg)
                all_effect_code.extend(handlers)

    for obj in control_objects:
        for child in obj.get("children", []):
            if child.get("type") != "BlockScript":
                continue
            fragments = child.get("fragments", [])
            codes = extract_all_fragments_code(fragments)
            all_control_code_parts.extend(codes)

    cin_combined = "\n---\n".join(all_cin_code) if all_cin_code else ""
    cout_combined = "\n---\n".join(all_cout_code) if all_cout_code else ""
    effect_combined = "\n---\n".join(all_effect_code) if all_effect_code else ""

    result["cin_handlers"] = all_cin_code
    result["cout_handlers"] = all_cout_code
    result["effect_handlers"] = all_effect_code

    result["cin_analysis"] = analyze_cin_logic(cin_combined)
    result["cout_analysis"] = analyze_cout_logic(cout_combined)
    result["effect_analysis"] = analyze_effect_logic(effect_combined)
    result["all_control_code"] = "\n===\n".join(all_control_code_parts)

    pkg_type, reason = classify_type(
        result["cin_analysis"], variables, events, result["all_control_code"]
    )
    result["type"] = pkg_type
    result["type_reason"] = reason

    return result


def print_separator(char="=", width=80):
    print(char * width)


def print_analysis(results: list[dict]):
    print_separator()
    print("盘古3D OJ 参考包判题逻辑分析报告")
    print_separator()
    print()

    type_groups: dict[str, list] = {}
    for r in results:
        t = r["type"]
        type_groups.setdefault(t, []).append(r)

    print("【题型分类总览】")
    print_separator("-", 60)
    for t, pkgs in sorted(type_groups.items()):
        names = [p["name"] for p in pkgs]
        print(f"  {t} ({len(pkgs)}个): {', '.join(names)}")
    print()

    for r in results:
        print_separator("=")
        print(f"包名: {r['name']}")
        print(f"场景名: {r.get('ws_name', 'N/A')}")
        print(f"题型: {r['type']} (原因: {r['type_reason']})")
        print_separator("-", 60)

        if r.get("error"):
            print(f"  错误: {r['error']}")
            continue

        print(f"  control 物件数: {r['control_count']}")
        print(f"  事件列表: {r['events']}")

        var_list = r["variables"]
        print(f"  变量 ({len(var_list)}个):")
        for v in var_list:
            print(f"    - {v}")

        print()
        cin = r["cin_analysis"]
        print("  【cin判断分析】")
        print(f"    输入个数检查: {cin.get('input_count_check', '无')}")
        print(f"    范围检查: {cin.get('range_check', '无')}")
        print(f"    小数点检查: {'是' if cin.get('decimal_check') else '否'}")
        print(f"    字符检查: {'是' if cin.get('char_check') else '否'}")
        print(f"    错误提示: {cin.get('error_messages', [])}")
        if cin.get("raw_code"):
            print("    --- cin判断伪代码 ---")
            for line in cin["raw_code"].split("\n"):
                print(f"    {line}")

        print()
        cout = r["cout_analysis"]
        print("  【cout判断分析】")
        print(f"    有处理器: {'是' if cout.get('has_handler') else '否'}")
        print(f"    检查输出: {'是' if cout.get('checks_output') else '否'}")
        print(f"    错误提示: {cout.get('error_messages', [])}")
        if cout.get("raw_code"):
            print("    --- cout判断伪代码 ---")
            for line in cout["raw_code"].split("\n"):
                print(f"    {line}")

        print()
        eff = r["effect_analysis"]
        print("  【展示关卡效果分析】")
        print(f"    有处理器: {'是' if eff.get('has_handler') else '否'}")
        print(f"    使用cin_cut: {'是' if eff.get('uses_cin_cut') else '否'}")
        print(f"    使用cout_cut: {'是' if eff.get('uses_cout_cut') else '否'}")
        print(f"    广播消息: {eff.get('broadcasts', [])}")
        if eff.get("raw_code"):
            print("    --- 展示关卡效果伪代码 ---")
            for line in eff["raw_code"].split("\n"):
                print(f"    {line}")

        print()

    print_separator("=")
    print()
    print("【关键差异对比】")
    print_separator("-", 60)

    headers = ["包名", "题型", "输入个数", "范围", "小数检查", "字符检查", "cout检查", "效果用cin"]
    col_widths = [max(len(h), 10) for h in headers]

    for r in results:
        col_widths[0] = max(col_widths[0], len(r["name"]) + 2)

    print("  " + " | ".join(h.ljust(w) for h, w in zip(headers, col_widths)))
    print("  " + "-+-".join("-" * w for w in col_widths))

    for r in results:
        cin = r.get("cin_analysis", {})
        cout = r.get("cout_analysis", {})
        eff = r.get("effect_analysis", {})
        row = [
            r["name"],
            r["type"],
            str(cin.get("input_count_check", "-")),
            str(cin.get("range_check", "-"))[:10],
            "Y" if cin.get("decimal_check") else "N",
            "Y" if cin.get("char_check") else "N",
            "Y" if cout.get("checks_output") else "N",
            "Y" if eff.get("uses_cin_cut") else "N",
        ]
        print("  " + " | ".join(str(v).ljust(w) for v, w in zip(row, col_widths)))

    print()


def main():
    import io

    if not BASE_DIR.exists():
        print(f"错误: 目录不存在 - {BASE_DIR}")
        sys.exit(1)

    pkg_dirs = sorted([d for d in BASE_DIR.iterdir() if d.is_dir()])
    if not pkg_dirs:
        print(f"错误: 未找到子目录 - {BASE_DIR}")
        sys.exit(1)

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print(f"找到 {len(pkg_dirs)} 个参考包，开始分析...\n")

    results = []
    for pkg_dir in pkg_dirs:
        try:
            result = analyze_package(pkg_dir)
            results.append(result)
        except Exception as e:
            results.append({"name": pkg_dir.name, "type": "错误", "type_reason": str(e), "error": str(e)})

    print_analysis(results)

    output_file = BASE_DIR.parent / "scripts" / "analysis_report.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        old_stdout = sys.stdout
        sys.stdout = f
        print_analysis(results)
        sys.stdout = old_stdout
    print(f"\n报告已保存到: {output_file}")


if __name__ == "__main__":
    main()
