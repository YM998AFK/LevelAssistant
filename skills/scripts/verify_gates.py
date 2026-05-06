# -*- coding: utf-8 -*-
"""综合 gate 校验：一次 Shell 跑完 gate1 + gate2 + gate3。

背景：过往 subagent 为了验证一个关卡包，需要分别跑 verify_blocks.py、
verify_no_new_next.py、以及手写 MCP validate 脚本，总 20~30 次 Shell 调用。
本脚本把三个 gate 合并为单次调用 + 结构化输出，供主 agent / subagent 一次拿齐结果。

使用：
  python scripts/verify_gates.py <target_zip>
  python scripts/verify_gates.py <target_zip> --baseline <baseline_zip>
  python scripts/verify_gates.py <target_zip> --json          # 输出结构化 JSON
  python scripts/verify_gates.py <target_zip> --json --quiet  # 仅 JSON，无 human summary

Gate 覆盖：
  gate1  params-count    —— verify_blocks.py 的核心逻辑（积木参数槽）
  gate2  no-new-next     —— verify_no_new_next.py 的核心逻辑（禁用 block.next）
  gate3  mcp-validate    —— hetu_mcp.validation_operations.validate_workspace

退出码：
  0  全部 gate PASS
  2  任一 gate FAIL
  3  usage / IO / import 错误
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "mcp" / "hetu_mcp"))
sys.path.insert(0, str(ROOT / "scripts"))


# ---------------------------------------------------------------------------
# 复用现有脚本里的核心函数
# ---------------------------------------------------------------------------

from verify_blocks import (  # noqa: E402
    REGISTRY_PATH,
    iter_blocks,
    load_registry,
)
from verify_no_new_next import collect_next_paths  # noqa: E402

try:
    from handlers.validation_operations import validate_workspace  # type: ignore  # noqa: E402
except Exception as exc:  # pragma: no cover
    validate_workspace = None  # type: ignore
    _validate_import_error = exc
else:
    _validate_import_error = None


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def load_ws_from_zip(zip_path: Path) -> Dict[str, Any]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        ws_names = [n for n in zf.namelist() if n.lower().endswith(".ws")]
        if not ws_names:
            raise RuntimeError(f"no .ws inside {zip_path}")
        with zf.open(ws_names[0]) as f:
            return json.loads(f.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# Gate 1: params-count
# ---------------------------------------------------------------------------

def run_gate1(ws_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        registry = load_registry(REGISTRY_PATH)
    except SystemExit:
        return {
            "name": "gate1_params_count",
            "pass": False,
            "error_count": 1,
            "warning_count": 0,
            "errors": [f"registry missing: {REGISTRY_PATH}"],
            "warnings": [],
            "stats": {},
        }

    scene = ws_data.get("scene")
    if not scene:
        return {
            "name": "gate1_params_count",
            "pass": False,
            "error_count": 1,
            "warning_count": 0,
            "errors": ["ws has no 'scene'"],
            "warnings": [],
            "stats": {},
        }

    errors: List[str] = []
    warnings: List[str] = []
    count_by_define: Counter = Counter()

    for bpath, blk in iter_blocks(scene):
        define = blk.get("define")
        count_by_define[define] += 1
        sections = blk.get("sections", [])
        actual = len(sections[0].get("params", [])) if sections else 0

        entry = registry.get(define)
        if entry is None:
            warnings.append(
                f"{bpath} {define}: not in registry (actual params={actual})"
            )
            continue

        kind = entry.get("kind")
        expect = entry.get("expect")

        if kind == "strict" and actual != expect:
            errors.append(
                f"{bpath} {define}: expected {expect} params, got {actual}"
            )
        elif kind == "variable" and actual != expect:
            dist = entry.get("distribution", {})
            seen = ", ".join(f"{k}={v}" for k, v in sorted(dist.items()))
            warnings.append(
                f"{bpath} {define}: uncommon params-count {actual} "
                f"(dominant={expect}; seen: {seen})"
            )

    return {
        "name": "gate1_params_count",
        "pass": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "block_total": sum(count_by_define.values()),
            "block_distinct_defines": len(count_by_define),
            "top5": count_by_define.most_common(5),
        },
    }


# ---------------------------------------------------------------------------
# Gate 2: no-new-next
# ---------------------------------------------------------------------------

def run_gate2(
    target_ws: Dict[str, Any],
    baseline_ws: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    target_nexts = collect_next_paths(target_ws)

    if baseline_ws is None:
        return {
            "name": "gate2_no_new_next",
            "pass": True,
            "mode": "info-only",
            "error_count": 0,
            "warning_count": len(target_nexts),
            "errors": [],
            "warnings": target_nexts,
            "stats": {
                "target_next_count": len(target_nexts),
                "note": "no baseline provided; gate2 in info-only mode (always PASS)",
            },
        }

    baseline_nexts = collect_next_paths(baseline_ws)
    base_set = set(baseline_nexts)
    new_only = [p for p in target_nexts if p not in base_set]

    return {
        "name": "gate2_no_new_next",
        "pass": not new_only,
        "mode": "strict",
        "error_count": len(new_only),
        "warning_count": 0,
        "errors": [f"new next introduced: {p}" for p in new_only],
        "warnings": [],
        "stats": {
            "target_next_count": len(target_nexts),
            "baseline_next_count": len(baseline_nexts),
            "new_next_count": len(new_only),
        },
    }


# ---------------------------------------------------------------------------
# Gate 3: mcp validate_workspace
# ---------------------------------------------------------------------------

def run_gate3(ws_data: Dict[str, Any]) -> Dict[str, Any]:
    if validate_workspace is None:
        return {
            "name": "gate3_mcp_validate",
            "pass": False,
            "error_count": 1,
            "warning_count": 0,
            "errors": [
                f"cannot import hetu_mcp.validation_operations: {_validate_import_error}"
            ],
            "warnings": [],
            "stats": {},
        }

    try:
        r = validate_workspace(ws_data)
    except Exception as exc:  # pragma: no cover
        return {
            "name": "gate3_mcp_validate",
            "pass": False,
            "error_count": 1,
            "warning_count": 0,
            "errors": [f"validate_workspace threw: {exc!r}"],
            "warnings": [],
            "stats": {},
        }

    errors = r.get("errors", []) or []
    warnings = r.get("warnings", []) or []
    return {
        "name": "gate3_mcp_validate",
        "pass": bool(r.get("valid")) and not errors,
        "error_count": int(r.get("error_count", len(errors))),
        "warning_count": int(r.get("warning_count", len(warnings))),
        "errors": [str(e) for e in errors[:50]],
        "warnings": [str(w) for w in warnings[:50]],
        "stats": {
            "errors_truncated_if_gt": 50,
            "warnings_truncated_if_gt": 50,
        },
    }


# ---------------------------------------------------------------------------
# Gate 4: N11 zip completeness（N11 规则：export_info.json / icon / UUID 匹配）
# ---------------------------------------------------------------------------

def run_gate4_zip_completeness(zip_path: Path) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        has_ws  = any(n.endswith(".ws")  for n in names)
        has_png = any(n.endswith(".png") for n in names)
        has_sol = "solution.json" in names
        has_ei  = "export_info.json" in names
        if not has_ws:
            errors.append("缺 *.ws workspace 文件")
        if not has_png:
            errors.append("缺 icon *.png 文件（引擎需要 icon）")
        if not has_sol:
            errors.append("缺 solution.json")
        if not has_ei:
            errors.append("缺 export_info.json（引擎合法性校验必需）")
        if has_sol and has_ei:
            try:
                sol = json.loads(zf.read("solution.json").decode("utf-8"))
                ei  = json.loads(zf.read("export_info.json").decode("utf-8"))
                s_uid = sol.get("init", "")
                e_uid = ei.get("solutionUid", "")
                if s_uid != e_uid:
                    errors.append(
                        f"N11 UUID 不匹配: solution.init={s_uid!r} "
                        f"!= export_info.solutionUid={e_uid!r}"
                    )
                else:
                    # 检查 solution icon 字段是否有对应文件
                    for proj in sol.get("projects", []):
                        icon = proj.get("icon", "")
                        icon_name = icon.rsplit("/", 1)[-1] if "/" in icon else icon
                        if icon_name and icon_name not in names:
                            warnings.append(
                                f"solution.projects icon={icon_name!r} 在 zip 里找不到对应文件"
                            )
            except Exception as exc:
                errors.append(f"读 solution/export_info 出错: {exc!r}")

    return {
        "name": "gate4_zip_completeness",
        "pass": len(errors) == 0,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "stats": {},
    }


# ---------------------------------------------------------------------------
# Orchestration + output
# ---------------------------------------------------------------------------

def run_all(
    target_zip: Path,
    baseline_zip: Optional[Path] = None,
) -> Dict[str, Any]:
    target_ws = load_ws_from_zip(target_zip)
    baseline_ws = load_ws_from_zip(baseline_zip) if baseline_zip else None

    gates = [
        run_gate1(target_ws),
        run_gate2(target_ws, baseline_ws),
        run_gate3(target_ws),
        run_gate4_zip_completeness(target_zip),
    ]

    overall_pass = all(g["pass"] for g in gates)
    return {
        "target": str(target_zip),
        "baseline": str(baseline_zip) if baseline_zip else None,
        "overall_pass": overall_pass,
        "gate_total": len(gates),
        "gate_passed": sum(1 for g in gates if g["pass"]),
        "gate_failed": sum(1 for g in gates if not g["pass"]),
        "gates": gates,
    }


def print_human(report: Dict[str, Any]) -> None:
    overall = "PASS" if report["overall_pass"] else "FAIL"
    print(f"=== verify_gates  {overall}  ({report['gate_passed']}/{report['gate_total']}) ===")
    print(f"target  : {report['target']}")
    if report.get("baseline"):
        print(f"baseline: {report['baseline']}")
    print()

    for g in report["gates"]:
        tag = "PASS" if g["pass"] else "FAIL"
        extra = f"  mode={g['mode']}" if "mode" in g else ""
        print(
            f"[{tag}] {g['name']}{extra}  "
            f"errors={g['error_count']}  warnings={g['warning_count']}"
        )
        for e in g["errors"][:10]:
            print(f"       ERR  {e}")
        if g["error_count"] > 10:
            print(f"       ... {g['error_count'] - 10} more errors")
        for w in g["warnings"][:5]:
            print(f"       warn {w}")
        if g["warning_count"] > 5:
            print(f"       ... {g['warning_count'] - 5} more warnings")
        print()


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", type=Path, help="target zip")
    parser.add_argument("--baseline", type=Path, default=None, help="baseline zip for gate2")
    parser.add_argument("--json", action="store_true", help="emit structured JSON")
    parser.add_argument("--quiet", action="store_true", help="with --json, suppress human summary")
    args = parser.parse_args(argv[1:])

    if not args.target.exists():
        print(f"[ERR] target not found: {args.target}", file=sys.stderr)
        return 3
    if args.baseline and not args.baseline.exists():
        print(f"[ERR] baseline not found: {args.baseline}", file=sys.stderr)
        return 3

    try:
        report = run_all(args.target, args.baseline)
    except Exception as exc:
        print(f"[ERR] unexpected failure: {exc!r}", file=sys.stderr)
        return 3

    if args.json:
        if not args.quiet:
            print_human(report)
            print("--- JSON ---")
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)

    return 0 if report["overall_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
