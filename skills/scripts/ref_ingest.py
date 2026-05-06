"""ref_ingest.py — 批量解压 + 扫描驱动器

递归扫描 `参考/` 下所有 zip，解压到 `参考-extracted/<stem>/`，然后对每个
包（含 _mine/ 之外的任何有 .ws 的目录）跑 ref_scan.py，产出 _analysis.md。

用法:
    python scripts/ref_ingest.py                 # 默认：扫 参考/、扫 参考-extracted/ 已有目录
    python scripts/ref_ingest.py --force-extract # 已解压目录也强制重解
    python scripts/ref_ingest.py --rescan-only   # 跳过解压，只跑 ref_scan
    python scripts/ref_ingest.py --skip-mine     # 跳过 _mine/（默认已跳过）
"""
import argparse
import shutil
import sys
import zipfile
from pathlib import Path

# 复用 ref_scan
sys.path.insert(0, str(Path(__file__).parent))
from ref_scan import scan_one  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REF_DIR = ROOT / '参考'
EXTRACT_DIR = ROOT / '参考-extracted'


def find_zips(base: Path):
    """递归找所有 .zip。"""
    return sorted(base.rglob('*.zip'))


def extract_one(zip_path: Path, force: bool = False):
    target = EXTRACT_DIR / zip_path.stem
    status = 'ok'
    if target.exists():
        has_ws = any(target.glob('*.ws'))
        if has_ws and not force:
            return target, 'skipped'
        if force:
            shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(target)
    except Exception as e:
        return target, f'extract_failed: {e}'
    return target, status


def find_extracted_packs():
    """返回 参考-extracted/ 下所有含 .ws 的目录（除 _mine/ 内）。"""
    out = []
    for p in sorted(EXTRACT_DIR.iterdir()):
        if not p.is_dir():
            continue
        if p.name == '_mine':
            continue
        if any(p.glob('*.ws')):
            out.append(p)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--force-extract', action='store_true')
    parser.add_argument('--rescan-only', action='store_true')
    parser.add_argument('--json', action='store_true', help='per-pack _analysis.json')
    args = parser.parse_args()

    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    stats = {'extract_ok': 0, 'extract_skip': 0, 'extract_fail': 0,
             'scan_ok': 0, 'scan_fail': 0}

    if not args.rescan_only:
        zips = find_zips(REF_DIR)
        print(f"[ingest] 在 {REF_DIR} 下发现 {len(zips)} 个 zip")
        for z in zips:
            tgt, st = extract_one(z, args.force_extract)
            rel = z.relative_to(REF_DIR)
            if st == 'ok':
                stats['extract_ok'] += 1
                print(f"  [EXTRACT] {rel}  ->  {tgt.name}/")
            elif st == 'skipped':
                stats['extract_skip'] += 1
            else:
                stats['extract_fail'] += 1
                print(f"  [FAIL   ] {rel}  {st}")
        print(f"[ingest] 解压：ok={stats['extract_ok']}  skip={stats['extract_skip']}  fail={stats['extract_fail']}")

    # 扫描所有已解压包
    packs = find_extracted_packs()
    print(f"\n[ingest] 将扫描 {len(packs)} 个已解压包")
    for p in packs:
        r = scan_one(p, write_json=args.json)
        if r['ok']:
            stats['scan_ok'] += 1
            # 安静模式
        else:
            stats['scan_fail'] += 1
            print(f"  [SCAN FAIL] {p.name}  {r['error']}")

    print(f"\n[ingest] 扫描：ok={stats['scan_ok']}  fail={stats['scan_fail']}")
    print(f"[ingest] 产物：每个 {EXTRACT_DIR}/<pack>/_analysis.md")


if __name__ == '__main__':
    main()
