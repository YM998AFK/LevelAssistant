# -*- coding: utf-8 -*-
r"""
批量调用 Unity Editor (batch mode) 跑 NavMesh 导出。

用法:
  python scripts/navmesh/run_unity_export.py --mode single --asset-id 12836
  python scripts/navmesh/run_unity_export.py --mode all
  python scripts/navmesh/run_unity_export.py --mode all --force
  python scripts/navmesh/run_unity_export.py --mode all --unity "C:\Program Files\..."

默认:
  Unity.exe      = C:\Program Files\Unity\Hub\Editor\2021.3.11f1\Editor\Unity.exe
  Project path   = D:\meishu
  Repo path      = (自动检测,当前仓库)
  Log file       = scripts/navmesh/unity_editor_scripts/unity_batch.log

返回码:
  0   成功(全部 ok)
  非0  有失败或未启动成功
"""
from __future__ import annotations
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_UNITY = r"C:\Program Files\Unity\Hub\Editor\2021.3.11f1\Editor\Unity.exe"
DEFAULT_PROJECT = r"D:\meishu"
DEFAULT_LOG = REPO_ROOT / "scripts" / "navmesh" / "unity_editor_scripts" / "unity_batch.log"
CACHE_DIR = REPO_ROOT / "scripts" / "navmesh" / "navmesh_cache"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["single", "all"], required=True,
                    help="single: 只导一个场景 (需 --asset-id); all: 全量")
    ap.add_argument("--asset-id", type=int, default=0, help="single 模式必填")
    ap.add_argument("--force", action="store_true", help="强制重导,覆盖已有缓存")
    ap.add_argument("--unity", default=DEFAULT_UNITY, help="Unity.exe 绝对路径")
    ap.add_argument("--project", default=DEFAULT_PROJECT, help="Unity 工程目录")
    ap.add_argument("--repo", default=str(REPO_ROOT), help="仓库根目录 (含 scripts/navmesh/)")
    ap.add_argument("--log", default=str(DEFAULT_LOG), help="Unity 日志输出路径")
    ap.add_argument("--dry-run", action="store_true", help="只打印命令不执行")
    args = ap.parse_args()

    if args.mode == "single" and args.asset_id <= 0:
        print("[ERROR] single 模式必须提供 --asset-id", file=sys.stderr)
        return 64

    unity = Path(args.unity)
    project = Path(args.project)
    repo = Path(args.repo)
    log = Path(args.log)

    if not unity.exists():
        print(f"[ERROR] Unity.exe 不存在: {unity}", file=sys.stderr)
        return 65
    if not (project / "Assets").exists():
        print(f"[ERROR] Unity 工程目录无效: {project}", file=sys.stderr)
        return 66
    index_json = repo / "scripts" / "navmesh" / "scene_index.json"
    if not index_json.exists():
        print(f"[ERROR] 缺 scene_index.json: {index_json},请先跑 build_scene_index.py", file=sys.stderr)
        return 67

    log.parent.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(unity),
        "-batchmode",
        "-nographics",
        "-silent-crashes",
        "-projectPath", str(project),
        "-executeMethod", "NavMeshExporter.BatchExportAll",
        "-RepoPath", str(repo),
        "-logFile", str(log),
        "-quit",
    ]
    if args.mode == "single":
        cmd += ["-BatchAssetId", str(args.asset_id)]
    if args.force:
        cmd += ["-BatchForce"]

    print("==================================================")
    print(f"Unity       : {unity}")
    print(f"Project     : {project}")
    print(f"Repo        : {repo}")
    print(f"Mode        : {args.mode}" + (f"  (asset_id={args.asset_id})" if args.mode == 'single' else ""))
    print(f"Force       : {args.force}")
    print(f"Log         : {log}")
    print(f"Cache dir   : {CACHE_DIR}")
    print("--------------------------------------------------")
    print("Command:")
    print("  " + " ".join(f'"{c}"' if " " in c else c for c in cmd))
    print("==================================================")

    if args.dry_run:
        print("[dry-run] 未启动 Unity")
        return 0

    lib = project / "Library"
    if not lib.exists():
        print("[WARN] 工程 Library/ 不存在,这是首次打开,资源全量 import 可能耗 20-60 分钟。")
        print("[WARN] 请耐心等待,不要强制关闭。Unity 日志会实时写入 log 文件。")

    started = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] 启动 Unity batch mode...")
    try:
        proc = subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        print("[ERROR] 用户中断。Unity 可能仍在后台运行,请手动确认。", file=sys.stderr)
        return 130

    elapsed = time.time() - started
    print("==================================================")
    print(f"Unity 退出: code={proc.returncode}  耗时={elapsed/60:.1f} min")

    json_count = len(list(CACHE_DIR.glob("*.json")))
    summary = CACHE_DIR / "_summary.json"
    print(f"Cache 目录有 JSON 文件 {json_count} 个")
    if summary.exists():
        print(f"_summary.json: {summary}")
        try:
            import json
            s = json.load(open(summary, encoding="utf-8"))
            print(f"  ok={s.get('ok')}  failed={s.get('failed')}")
            fails = [it for it in s.get("items", []) if it.get("status") == "failed"]
            if fails:
                print(f"  失败 {len(fails)} 条 (前 5):")
                for it in fails[:5]:
                    print(f"    - {it.get('asset_id')} {it.get('name')}: {it.get('error')}")
        except Exception as e:
            print(f"  (读 summary 失败: {e})")

    print(f"日志: {log}")
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
