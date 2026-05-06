"""校验目标 zip 相对母本 zip 没有新增 block.next。

盘古3D 实证规范：所有连续积木在 `sections[*].children` 数组里平铺排列，
不使用 `block.next` 链接。一旦 next 被使用，编辑器只会渲染链头，其余积木全丢。
这是 2026-04 "15-2 关卡3-v1" 事故的根因，靠 verify_blocks.py 的参数槽校验检测不出。

用法：
    python scripts/verify_no_new_next.py <target_zip>
    python scripts/verify_no_new_next.py --baseline <baseline_zip> <target_zip>

- 无 baseline 时：列出 target 里所有 next 出现位置，仅作信息输出（退出码 0）。
- 有 baseline 时：对比两个 zip 的 next 集合，若 target 比 baseline 多出 next 则 FAIL（退出码 2）。
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path


def collect_next_paths(ws_data: dict) -> list[str]:
    """遍历 .ws 的 scene 树，收集所有 block.next is not None 的"路径"字符串。

    路径格式示例：scene/control.frag5.c3.c0 define=WhenGameStarts
    """
    out: list[str] = []

    def walk_block(b, path: str):
        if not isinstance(b, dict):
            return
        if b.get("next") is not None:
            out.append(f"{path} define={b.get('define')}")
        for si, s in enumerate(b.get("sections", []) or []):
            for pi, p in enumerate(s.get("params", []) or []):
                if isinstance(p, dict) and p.get("type") == "block" and isinstance(p.get("val"), dict):
                    walk_block(p["val"], f"{path}.sec{si}.param{pi}")
            for ci, c in enumerate(s.get("children", []) or []):
                walk_block(c, f"{path}.sec{si}.child{ci}")

    def walk_node(node, path: str):
        if isinstance(node, dict):
            name = node.get("props", {}).get("Name", "?")
            for ch in node.get("children", []) or []:
                if isinstance(ch, dict) and ch.get("type") == "BlockScript":
                    for fi, f in enumerate(ch.get("fragments", []) or []):
                        walk_block(f.get("head", {}), f"{path}/{name}.frag{fi}")
                else:
                    walk_node(ch, f"{path}/{name}")

    scene = ws_data.get("scene", {})
    walk_node(scene, "scene")
    return out


def load_ws_from_zip(zip_path: Path) -> dict:
    with zipfile.ZipFile(zip_path, "r") as z:
        ws_names = [n for n in z.namelist() if n.endswith(".ws")]
        if not ws_names:
            raise RuntimeError(f"{zip_path} 里没有 .ws 文件")
        return json.loads(z.read(ws_names[0]).decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="目标 zip（被校验对象）")
    parser.add_argument(
        "--baseline",
        type=Path,
        default=None,
        help="母本 zip（可选，用于对比；不传时只做信息输出）",
    )
    args = parser.parse_args()

    if not args.target.exists():
        print(f"[ERR] 找不到目标 zip: {args.target}")
        return 2

    target_ws = load_ws_from_zip(args.target)
    target_nexts = collect_next_paths(target_ws)

    print(f"=== 目标 zip: {args.target}  (next 出现 {len(target_nexts)} 处) ===")
    for p in target_nexts:
        print(f"  {p}")

    if args.baseline is None:
        if target_nexts:
            print(
                "\n[INFO] 未提供 --baseline，无法判定是否新增；"
                "若本 zip 由修改流程产生，请补上 --baseline <原 zip> 再跑一次。"
            )
        return 0

    if not args.baseline.exists():
        print(f"[ERR] 找不到母本 zip: {args.baseline}")
        return 2

    base_ws = load_ws_from_zip(args.baseline)
    base_nexts = collect_next_paths(base_ws)
    print(f"\n=== 母本 zip: {args.baseline}  (next 出现 {len(base_nexts)} 处) ===")
    for p in base_nexts:
        print(f"  {p}")

    base_set = set(base_nexts)
    new_only = [p for p in target_nexts if p not in base_set]

    print(f"\n=== 新增 next 对比结果 ===")
    print(f"母本 next 数: {len(base_nexts)}")
    print(f"目标 next 数: {len(target_nexts)}")
    print(f"新增 next 数: {len(new_only)}")

    if new_only:
        print("\n[FAIL] 目标相对母本新增了以下 next 链接（违反 children 平铺规范）：")
        for p in new_only:
            print(f"  + {p}")
        print(
            "\n修复方式：把 block.next 的引用展开成 sections[0].children 数组的平铺元素，"
            "参见 level-common/SKILL.md『积木 children 平铺（禁用 next）』规则。"
        )
        return 2

    print("\n[PASS] 目标未引入任何新的 next 链接。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
