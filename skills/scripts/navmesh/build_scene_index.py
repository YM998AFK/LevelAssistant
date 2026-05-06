# -*- coding: utf-8 -*-
r"""
建立「场景 AssetId ↔ .unity 绝对路径 ↔ NavMesh.asset 绝对路径」索引。

数据源:
  1. .cursor/skills/level-common/asset_catalog.md 的「## 场景 (Scene)」表
     → 提供 AssetId ↔ 名称 ↔ .unity 文件名 ↔ 课程分类
  2. .cursor/skills/level-common/资源预览图/preview_urls.md
     → 提供 AssetId ↔ 预览图 URL
  3. Unity 工程文件系统扫描(D:\meishu\Assets\BundleResources\ide\scene\**)
     → 提供 .unity 文件名 ↔ 绝对路径,按同名子目录规则找 NavMesh.asset

输出:
  scripts/navmesh/scene_index.json
  scripts/navmesh/scene_index_missing.md  (四类异常报告)
"""
from __future__ import annotations
import json, re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_MD = REPO_ROOT / ".cursor" / "skills" / "level-common" / "asset_catalog.md"
PREVIEW_MD = REPO_ROOT / ".cursor" / "skills" / "level-common" / "资源预览图" / "preview_urls.md"
OUT_DIR = REPO_ROOT / "scripts" / "navmesh"
OUT_JSON = OUT_DIR / "scene_index.json"
OUT_MISSING = OUT_DIR / "scene_index_missing.md"

UNITY_SCENE_ROOT = Path(r"D:\meishu\Assets\BundleResources\ide\scene")


def parse_catalog(md_path: Path) -> List[Dict]:
    """解析 asset_catalog.md 的「## 场景 (Scene)」章节。"""
    text = md_path.read_text(encoding="utf-8")
    m = re.search(r"##\s*场景\s*\(Scene\)\s*\n(.*?)(?=\n##\s|\Z)", text, re.S)
    if not m:
        raise RuntimeError(f"未在 {md_path} 找到「## 场景 (Scene)」段")
    body = m.group(1)

    rows: List[Dict] = []
    row_re = re.compile(
        r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*$",
        re.M,
    )
    for mm in row_re.finditer(body):
        asset_id = int(mm.group(1))
        name = mm.group(2).strip()
        unity_file = mm.group(3).strip()
        category = mm.group(4).strip()
        if unity_file.lower().endswith(".unity"):
            rows.append({
                "asset_id": asset_id,
                "name": name,
                "unity_file": unity_file,
                "category": category,
            })
    return rows


def parse_preview_urls(md_path: Path) -> Dict[int, str]:
    """抽取 `AssetId=12836 → URL` 映射。"""
    if not md_path.exists():
        return {}
    text = md_path.read_text(encoding="utf-8")
    out: Dict[int, str] = {}
    for m in re.finditer(r"AssetId=(\d+)\)[^\n]*?(https?://[^\s)]+)", text):
        out[int(m.group(1))] = m.group(2).strip()
    return out


def scan_unity_fs(root: Path) -> Tuple[Dict[str, List[Path]], List[Path]]:
    """扫描 Unity 工程场景目录,返回:
    - 按小写 .unity 文件名分组的绝对路径(用于去重/多分支问题)
    - 所有 .unity 文件列表
    """
    by_name: Dict[str, List[Path]] = {}
    all_unity: List[Path] = []
    if not root.exists():
        return by_name, all_unity
    for p in root.rglob("*.unity"):
        if not p.is_file():
            continue
        all_unity.append(p)
        by_name.setdefault(p.name.lower(), []).append(p)
    return by_name, all_unity


def infer_navmesh_path(unity_abspath: Path) -> Optional[Path]:
    """按「同名子目录」规则拼 NavMesh.asset 路径,不存在返回 None。"""
    stem = unity_abspath.stem
    candidate = unity_abspath.parent / stem / "NavMesh.asset"
    return candidate if candidate.exists() else None


def main() -> None:
    print(f"[1/4] 读 catalog: {CATALOG_MD.relative_to(REPO_ROOT)}")
    scenes = parse_catalog(CATALOG_MD)
    print(f"      catalog 场景行数 = {len(scenes)}")

    print(f"[2/4] 读 preview urls: {PREVIEW_MD.relative_to(REPO_ROOT)}")
    preview_map = parse_preview_urls(PREVIEW_MD)
    print(f"      preview url 数 = {len(preview_map)}")

    print(f"[3/4] 扫 Unity: {UNITY_SCENE_ROOT}")
    fs_by_name, all_unity = scan_unity_fs(UNITY_SCENE_ROOT)
    print(f"      filesystem .unity 数 = {len(all_unity)}")
    print(f"      按文件名分组 = {len(fs_by_name)} 个唯一名")

    print(f"[4/4] 合并 + 写出")
    index: Dict[str, Dict] = {}
    missing_unity: List[Dict] = []
    missing_navmesh: List[Dict] = []
    ambiguous: List[Dict] = []

    claimed_names = {s["unity_file"].lower() for s in scenes}

    for s in scenes:
        key = s["unity_file"].lower()
        matches = fs_by_name.get(key, [])
        entry = {
            "asset_id": s["asset_id"],
            "name": s["name"],
            "category": s["category"],
            "unity_file": s["unity_file"],
            "unity_abspath": None,
            "navmesh_abspath": None,
            "has_navmesh": False,
            "preview_url": preview_map.get(s["asset_id"]),
        }
        if not matches:
            missing_unity.append(s)
        else:
            chosen = matches[0]
            if len(matches) > 1:
                ambiguous.append({**s, "candidates": [str(p) for p in matches]})
            entry["unity_abspath"] = str(chosen)
            nav = infer_navmesh_path(chosen)
            if nav:
                entry["navmesh_abspath"] = str(nav)
                entry["has_navmesh"] = True
            else:
                missing_navmesh.append({**s, "unity_abspath": str(chosen)})
        index[str(s["asset_id"])] = entry

    orphan_unity = [str(p) for p in all_unity if p.name.lower() not in claimed_names]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "_meta": {
            "catalog_source": str(CATALOG_MD.relative_to(REPO_ROOT)).replace("\\", "/"),
            "unity_scene_root": str(UNITY_SCENE_ROOT),
            "counts": {
                "catalog_rows": len(scenes),
                "fs_unity_files": len(all_unity),
                "indexed_scenes": len(index),
                "with_navmesh": sum(1 for e in index.values() if e["has_navmesh"]),
                "missing_unity": len(missing_unity),
                "missing_navmesh": len(missing_navmesh),
                "ambiguous": len(ambiguous),
                "orphan_unity": len(orphan_unity),
            },
        },
        "scenes": index,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"      写 {OUT_JSON.relative_to(REPO_ROOT)}")

    lines: List[str] = []
    lines.append("# Scene Index Missing / Anomaly Report\n")
    lines.append(f"- catalog 行数: **{len(scenes)}**")
    lines.append(f"- 文件系统 .unity 总数: **{len(all_unity)}**")
    lines.append(f"- 成功建立 NavMesh 索引: **{payload['_meta']['counts']['with_navmesh']}** 个")
    lines.append("")

    lines.append(f"## ① catalog 声明但文件系统找不到 .unity ({len(missing_unity)})\n")
    if missing_unity:
        lines.append("| AssetId | 名称 | 声明文件名 | 课程分类 |")
        lines.append("|---|---|---|---|")
        for s in missing_unity:
            lines.append(f"| {s['asset_id']} | {s['name']} | `{s['unity_file']}` | {s['category']} |")
    else:
        lines.append("_无_")
    lines.append("")

    lines.append(f"## ② 有 .unity 但没烘 NavMesh ({len(missing_navmesh)})\n")
    if missing_navmesh:
        lines.append("| AssetId | 名称 | .unity 绝对路径 |")
        lines.append("|---|---|---|")
        for s in missing_navmesh:
            lines.append(f"| {s['asset_id']} | {s['name']} | `{s['unity_abspath']}` |")
    else:
        lines.append("_无_")
    lines.append("")

    lines.append(f"## ③ 同文件名多处出现,需人工裁决 ({len(ambiguous)})\n")
    if ambiguous:
        for s in ambiguous:
            lines.append(f"- **{s['asset_id']} / {s['name']}** (`{s['unity_file']}`)")
            for c in s["candidates"]:
                lines.append(f"  - {c}")
    else:
        lines.append("_无_")
    lines.append("")

    lines.append(f"## ④ 文件系统有但 catalog 没登记 ({len(orphan_unity)})\n")
    if orphan_unity:
        for p in orphan_unity:
            lines.append(f"- {p}")
    else:
        lines.append("_无_")
    lines.append("")

    OUT_MISSING.write_text("\n".join(lines), encoding="utf-8")
    print(f"      写 {OUT_MISSING.relative_to(REPO_ROOT)}")

    print("\n=== 统计 ===")
    for k, v in payload["_meta"]["counts"].items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
