"""
extract_zip.py - 统一的关卡 zip 解压工具

用法:
  python scripts/extract_zip.py <zip_path>             # 解压单个zip 到 参考-extracted/<name>/
  python scripts/extract_zip.py <dir>                  # 解压目录下所有zip
  python scripts/extract_zip.py <zip> --out <dir>      # 指定输出目录
  python scripts/extract_zip.py <zip> --force          # 强制重新解压
  python scripts/extract_zip.py --ref                  # 解压 参考/ 下所有zip

默认行为:
  - 自动解压到 参考-extracted/<zip名去掉.zip>/
  - 若目标目录已存在 .ws 文件且未加 --force，跳过（避免覆盖手动修改）
  - 打印 .ws / solution.json / export_info.json 路径

设计目标:
  所有"需要看参考/待修改包"的场景统一调用此脚本，不再在对话中重复写解压代码。
"""
import sys
import shutil
import zipfile
import argparse
from pathlib import Path

ROOT              = Path(__file__).resolve().parent.parent
DEFAULT_REF_DIR   = ROOT / "参考"
DEFAULT_EXTRACT   = ROOT / "参考-extracted"


def extract_one(zip_path: Path, out_base: Path, force: bool = False) -> dict:
    zip_path = Path(zip_path).resolve()
    if not zip_path.exists() or zip_path.suffix.lower() != ".zip":
        return {"ok": False, "zip": str(zip_path), "error": "not a zip file"}

    target_dir = out_base / zip_path.stem

    if target_dir.exists() and not force:
        ws_files = list(target_dir.glob("*.ws"))
        if ws_files:
            return {
                "ok": True, "zip": str(zip_path), "dir": str(target_dir),
                "skipped": True, "ws": [str(w) for w in ws_files],
            }

    if force and target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(target_dir)
    except Exception as e:
        return {"ok": False, "zip": str(zip_path), "error": f"extract failed: {e}"}

    ws_files  = list(target_dir.glob("*.ws"))
    sol_file  = target_dir / "solution.json"
    info_file = target_dir / "export_info.json"
    return {
        "ok":          True,
        "zip":         str(zip_path),
        "dir":         str(target_dir),
        "skipped":     False,
        "ws":          [str(w) for w in ws_files],
        "solution":    str(sol_file)  if sol_file.exists()  else None,
        "export_info": str(info_file) if info_file.exists() else None,
    }


def extract_many(source: Path, out_base: Path, force: bool = False) -> list:
    results = []
    source = Path(source).resolve()
    if source.is_file() and source.suffix.lower() == ".zip":
        results.append(extract_one(source, out_base, force))
    elif source.is_dir():
        for zp in sorted(source.glob("*.zip")):
            results.append(extract_one(zp, out_base, force))
    else:
        results.append({"ok": False, "zip": str(source), "error": "not found or not zip/dir"})
    return results


def print_result(r: dict):
    status = "SKIP" if r.get("skipped") else "OK  " if r["ok"] else "FAIL"
    name = Path(r["zip"]).name
    if r["ok"]:
        print(f"[{status}] {name}")
        print(f"       -> {r['dir']}")
        for w in r.get("ws", []):
            print(f"          ws:  {Path(w).name}")
        if r.get("solution"):    print(f"          solution.json")
        if r.get("export_info"): print(f"          export_info.json")
    else:
        print(f"[{status}] {name}  {r['error']}")


def main():
    parser = argparse.ArgumentParser(description="Extract Pangu3D level zip packages")
    parser.add_argument("src", nargs="?", help="zip file or directory containing zips")
    parser.add_argument("--out",   help="output base directory (default: 参考-extracted/)")
    parser.add_argument("--force", action="store_true", help="force re-extract")
    parser.add_argument("--ref",   action="store_true", help="extract all zips in 参考/")
    args = parser.parse_args()

    out_base = Path(args.out).resolve() if args.out else DEFAULT_EXTRACT
    out_base.mkdir(parents=True, exist_ok=True)

    if args.ref:
        print(f"[ref] source: {DEFAULT_REF_DIR}")
        print(f"      output: {out_base}")
        results = extract_many(DEFAULT_REF_DIR, out_base, args.force)
    elif args.src:
        results = extract_many(args.src, out_base, args.force)
    else:
        parser.print_help()
        sys.exit(1)

    for r in results:
        print_result(r)
    ok = sum(1 for r in results if r["ok"])
    print(f"\ndone: {ok}/{len(results)} extracted")


if __name__ == "__main__":
    main()
