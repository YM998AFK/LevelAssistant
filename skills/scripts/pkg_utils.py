"""
pkg_utils.py - 关卡 zip 解压/打包工具集（MCP 流水线专用）

背景（2026-04-23）：
  hetu-mcp 的 load/save_workspace_file 有沙箱限制，只能访问 workspace_root 下
  的路径；且 MCP 不负责 zip 层面的操作（解压 / 打包 / 清理 .bak）。
  本模块补齐这些"胶水"能力。

提供的函数：
  - extract_zip_into(zip_path, workdir) -> dict
      解压 zip 到仓库内工作目录（强制在 workspace_root 内，避免 MCP 沙箱报错）
  - pack_zip_clean(workdir, out_zip) -> Path
      打包目录为 zip，**自动跳过** .bak / .backup / .swp / __pycache__ 等临时文件
  - clean_backups(workdir) -> list[Path]
      清理目录内的 .bak / .backup 残留（MCP save 若未用 create_backup=False 会产生）

典型 MCP 流水线：
  from scripts.pkg_utils import extract_zip_into, pack_zip_clean, clean_backups
  info = extract_zip_into("参考/Xxx.zip", "output/new/Xxx_workdir")
  ws_path = info["ws"][0]
  # … 调用 hetu-mcp load/modify/save（save_workspace_file 必须 create_backup=False） …
  clean_backups(info["dir"])           # 保险：二次清理
  pack_zip_clean(info["dir"], "output/new/Xxx-v1.zip")

命令行用法（兼容调用，不推荐在流水线里用）：
  python scripts/pkg_utils.py extract 参考/Xxx.zip output/new/Xxx_workdir
  python scripts/pkg_utils.py pack   output/new/Xxx_workdir output/new/Xxx-v1.zip
  python scripts/pkg_utils.py clean  output/new/Xxx_workdir
"""
from __future__ import annotations

import sys
import shutil
import zipfile
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent

BACKUP_SUFFIXES = (".bak", ".backup", ".swp", ".tmp", ".orig")
BACKUP_SUBSTRS  = (".backup_", ".bak_", ".orig_")
IGNORED_DIRS    = ("__pycache__", ".DS_Store")


def _ensure_inside_workspace(path: Path) -> Path:
    p = Path(path).resolve()
    try:
        p.relative_to(ROOT)
    except ValueError:
        raise ValueError(
            f"路径 {p} 不在仓库根目录 {ROOT} 下。\n"
            f"MCP 工具沙箱只允许访问仓库内的路径，请改到 output/ 或 参考-extracted/ 下。"
        )
    return p


def _is_backup_file(name: str) -> bool:
    """
    判定一个文件名是不是临时/备份文件：
      - .bak / .backup / .swp / .tmp / .orig 后缀
      - 含 .backup_<...> / .bak_<...> / .orig_<...> 子串（MCP save_workspace_file 带时间戳
        的备份形如 `foo.backup_20260423_120000.ws`）
    """
    lower = name.lower()
    if any(lower.endswith(suf) for suf in BACKUP_SUFFIXES):
        return True
    if any(sub in lower for sub in BACKUP_SUBSTRS):
        return True
    return False


def extract_zip_into(zip_path: str | Path, workdir: str | Path, force: bool = True) -> dict:
    """
    解压 zip_path 到 workdir（必须在仓库根目录内，否则 MCP 会 Path escapes workspace root）。

    返回 dict: { ok, zip, dir, ws: [...], solution, export_info }
    """
    zip_path = Path(zip_path).resolve()
    workdir  = _ensure_inside_workspace(Path(workdir))

    if not zip_path.exists() or zip_path.suffix.lower() != ".zip":
        return {"ok": False, "zip": str(zip_path), "error": "not a zip file"}

    if workdir.exists():
        if force:
            shutil.rmtree(workdir)
        else:
            ws_files = list(workdir.glob("*.ws"))
            if ws_files:
                return {
                    "ok": True, "zip": str(zip_path), "dir": str(workdir),
                    "skipped": True, "ws": [str(w) for w in ws_files],
                }
    workdir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(workdir)
    except Exception as e:
        return {"ok": False, "zip": str(zip_path), "error": f"extract failed: {e}"}

    ws_files  = list(workdir.glob("*.ws"))
    sol_file  = workdir / "solution.json"
    info_file = workdir / "export_info.json"
    return {
        "ok":          True,
        "zip":         str(zip_path),
        "dir":         str(workdir),
        "skipped":     False,
        "ws":          [str(w) for w in ws_files],
        "solution":    str(sol_file)  if sol_file.exists()  else None,
        "export_info": str(info_file) if info_file.exists() else None,
    }


def clean_backups(workdir: str | Path) -> list[Path]:
    """删除 workdir 内所有 .bak / .backup / .swp / .tmp / .orig。返回被删文件列表。"""
    workdir = Path(workdir).resolve()
    removed: list[Path] = []
    if not workdir.is_dir():
        return removed
    for p in workdir.rglob("*"):
        if p.is_file() and _is_backup_file(p.name):
            try:
                p.unlink()
                removed.append(p)
            except Exception:
                pass
    return removed


def _iter_pack_entries(workdir: Path) -> Iterable[tuple[Path, str]]:
    for p in workdir.rglob("*"):
        if not p.is_file():
            continue
        if _is_backup_file(p.name):
            continue
        rel_parts = p.relative_to(workdir).parts
        if any(part in IGNORED_DIRS for part in rel_parts):
            continue
        arcname = "/".join(rel_parts)
        yield p, arcname


def pack_zip_clean(workdir: str | Path, out_zip: str | Path) -> Path:
    """
    将 workdir 打包为 zip，自动跳过 .bak / .backup / __pycache__ 等临时文件。
    会先调用 clean_backups 做物理清理。
    """
    workdir = Path(workdir).resolve()
    out_zip = Path(out_zip).resolve()
    if not workdir.is_dir():
        raise FileNotFoundError(f"workdir not found: {workdir}")

    removed = clean_backups(workdir)
    if removed:
        print(f"[pkg_utils] cleaned {len(removed)} backup file(s): "
              + ", ".join(p.name for p in removed[:5])
              + ("…" if len(removed) > 5 else ""))

    out_zip.parent.mkdir(parents=True, exist_ok=True)
    if out_zip.exists():
        out_zip.unlink()

    count = 0
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for src, arcname in _iter_pack_entries(workdir):
            zf.write(src, arcname)
            count += 1

    print(f"[pkg_utils] packed {count} file(s) -> {out_zip}")
    return out_zip


def _cli():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "extract":
        if len(sys.argv) < 4:
            print("usage: pkg_utils.py extract <zip> <workdir>")
            sys.exit(1)
        r = extract_zip_into(sys.argv[2], sys.argv[3])
        print(r)
    elif cmd == "pack":
        if len(sys.argv) < 4:
            print("usage: pkg_utils.py pack <workdir> <out_zip>")
            sys.exit(1)
        pack_zip_clean(sys.argv[2], sys.argv[3])
    elif cmd == "clean":
        if len(sys.argv) < 3:
            print("usage: pkg_utils.py clean <workdir>")
            sys.exit(1)
        removed = clean_backups(sys.argv[2])
        print(f"cleaned {len(removed)} file(s):")
        for p in removed:
            print(f"  - {p}")
    else:
        print(f"unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    _cli()
