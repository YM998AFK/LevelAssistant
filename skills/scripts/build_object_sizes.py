"""扫 参考-extracted/ 下所有 .ws，统计每个 MeshPart AssetId 的
实际占地尺寸（Size × Scale），生成 `object_sizes.md`。

目的：和 character_tags.md 类似，为 3D 物件积累"实际占地大小的认知"，
让 AI 生成关卡时能按真实尺寸挑选物件（不再只凭名字猜大小）。

规则：
- 扫描范围：`参考-extracted/*/*.ws`（设计师提供的参考关卡）
- 类型：`type == "MeshPart"`（Effect 不摆 3D 碰撞，不纳入尺寸统计）
- 对每个 AssetId，收集所有 (Size, Scale) 组合及其出现次数
- 实际尺寸 = Size × Scale（Scale 单值时各轴同乘，三维时逐轴乘）
- 按最大边长划分尺寸档：
    超小 < 0.3m  (小零件/按钮)
    小   0.3~1m  (可拾取物)
    中   1~3m   (可互动家具/箱)
    大   3~6m   (载具/大型装置)
    巨   > 6m   (建筑/塔)
- 输出 `.cursor/skills/level-generator/object_sizes.md`
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"c:\Users\Hetao\Desktop\公司")
EXTRACTED = ROOT / "参考-extracted"
SKILL_DIR = ROOT / ".cursor" / "skills" / "level-generator"
CATALOG = SKILL_DIR / "asset_catalog.md"
OUT = SKILL_DIR / "object_sizes.md"


def load_asset_id_to_name() -> dict[str, str]:
    """复用 build_object_usage.py 的解析逻辑：从 asset_catalog 各章节
    收集 AssetId → 名称 的映射。"""
    if not CATALOG.exists():
        return {}
    text = CATALOG.read_text(encoding="utf-8")
    mapping: dict[str, str] = {}
    col_idx: dict[str, int] = {}
    header_found = False
    for line in text.splitlines():
        if line.startswith("## ") and header_found:
            header_found = False
            col_idx = {}
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not header_found:
            if "AssetId" in cells and ("名称" in cells or "名字" in cells):
                for i, c in enumerate(cells):
                    col_idx[c] = i
                header_found = True
            continue
        if cells[0].startswith("-"):
            continue
        aid = cells[col_idx["AssetId"]]
        name_col = "名称" if "名称" in col_idx else "名字"
        name = cells[col_idx[name_col]]
        if aid and aid.isdigit():
            mapping.setdefault(aid, name)
    return mapping


def parse_vec3(v) -> tuple[float, float, float] | None:
    """把 Size 字段（形如 ["1", "1.97", "1"]）解析成 float tuple。"""
    if isinstance(v, list) and len(v) == 3:
        try:
            return tuple(float(x) for x in v)  # type: ignore
        except (ValueError, TypeError):
            return None
    return None


def parse_scale(v) -> tuple[float, float, float] | None:
    """Scale 可能是单值 "0.8" 或三维 ["1","1","1"]，统一转 (sx, sy, sz)。"""
    if isinstance(v, str):
        try:
            s = float(v)
            return (s, s, s)
        except ValueError:
            return None
    if isinstance(v, (int, float)):
        return (float(v), float(v), float(v))
    if isinstance(v, list) and len(v) == 3:
        try:
            return tuple(float(x) for x in v)  # type: ignore
        except (ValueError, TypeError):
            return None
    return None


def fmt(x: float) -> str:
    """紧凑数字：整数不带小数，其余保留 2 位。"""
    if abs(x - round(x)) < 1e-4:
        return str(int(round(x)))
    return f"{x:.2f}"


def fmt_vec(v: tuple[float, float, float]) -> str:
    return f"[{fmt(v[0])}, {fmt(v[1])}, {fmt(v[2])}]"


def size_tier(max_edge: float) -> str:
    if max_edge < 0.3:
        return "超小"
    if max_edge < 1.0:
        return "小"
    if max_edge < 3.0:
        return "中"
    if max_edge < 6.0:
        return "大"
    return "巨"


def collect_meshparts(path: Path):
    """返回列表 [(AssetId_str, name_str, Size_tuple, Scale_tuple), ...]。"""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    out = []

    def walk(node):
        if not isinstance(node, dict):
            return
        if node.get("type") == "MeshPart":
            props = node.get("props", {})
            aid = props.get("AssetId")
            if aid is not None:
                size = parse_vec3(props.get("Size"))
                scale = parse_scale(props.get("Scale"))
                if size and scale:
                    out.append((
                        str(aid),
                        str(props.get("Name", "")),
                        size,
                        scale,
                    ))
        for child in node.get("children", []) or []:
            walk(child)

    scene = data.get("scene")
    if scene:
        walk(scene)
    return out


def main():
    asset_id_to_name = load_asset_id_to_name()

    # 每个 AssetId 下，统计 (real_size, size_raw, scale) 组合出现次数
    # key = (aid, size_key, scale_key)  value = count
    combo_count: dict[tuple, int] = defaultdict(int)
    # 每个 AssetId 的样本总数（跨关卡节点数）
    total_nodes: dict[str, int] = defaultdict(int)
    # 记录该 AssetId 在哪些关卡出现过（用于样本关卡数）
    levels_of: dict[str, set] = defaultdict(set)
    # 捕获一个 in-scene 名称（有时比 asset_catalog 里的名字更准）
    in_scene_name: dict[str, str] = {}

    level_count = 0
    for ws_path in sorted(EXTRACTED.glob("*/*.ws")):
        nodes = collect_meshparts(ws_path)
        if not nodes:
            continue
        level_count += 1
        level_name = ws_path.parent.name
        for aid, name, size, scale in nodes:
            real = (size[0] * scale[0], size[1] * scale[1], size[2] * scale[2])
            key = (aid, size, scale)
            combo_count[key] += 1
            total_nodes[aid] += 1
            levels_of[aid].add(level_name)
            if aid not in in_scene_name and name:
                in_scene_name[aid] = name

    print(f"扫描关卡数: {level_count}")
    print(f"出现过的 MeshPart AssetId 数: {len(total_nodes)}")

    # 按 AssetId 聚合：挑"最常见组合"作为主尺寸
    aggregated = []  # [(aid, name, primary_combo, all_combos)]
    for aid in total_nodes:
        combos = [
            (size, scale, cnt)
            for (a, size, scale), cnt in combo_count.items()
            if a == aid
        ]
        combos.sort(key=lambda x: -x[2])
        primary_size, primary_scale, primary_cnt = combos[0]
        primary_real = (
            primary_size[0] * primary_scale[0],
            primary_size[1] * primary_scale[1],
            primary_size[2] * primary_scale[2],
        )
        aggregated.append({
            "aid": aid,
            "name": asset_id_to_name.get(aid) or in_scene_name.get(aid, "(未在 asset_catalog 中)"),
            "primary_size": primary_size,
            "primary_scale": primary_scale,
            "primary_real": primary_real,
            "primary_cnt": primary_cnt,
            "total": total_nodes[aid],
            "levels": len(levels_of[aid]),
            "combos": combos,
            "max_edge": max(primary_real),
        })

    # 输出：先按尺寸档排序，每档内按使用数降序
    TIER_ORDER = ["超小", "小", "中", "大", "巨"]
    for it in aggregated:
        it["tier"] = size_tier(it["max_edge"])
    aggregated.sort(key=lambda x: (TIER_ORDER.index(x["tier"]), -x["total"], int(x["aid"])))

    lines = [
        "# 3D 物件实际占地尺寸 (object_sizes)",
        "",
        "> 自动由 [scripts/build_object_sizes.py](../../../scripts/build_object_sizes.py) 生成。",
        f"> 数据来源：扫描 `参考-extracted/` 下 {level_count} 个参考关卡的 `.ws` 文件，"
        f"收集 {sum(total_nodes.values())} 个 MeshPart 节点的 Size × Scale。",
        "",
        "## 口径说明",
        "",
        "- **实际尺寸 = Size × Scale**（Scale 单值时各轴同乘，三维时逐轴乘）",
        "- **主尺寸**：该 AssetId 在所有参考包里出现最多的 (Size, Scale) 组合",
        "- **尺寸档**（按主尺寸的最大边长）：",
        "  - 超小 `<0.3m` —— 小零件、按钮、徽章类",
        "  - 小   `0.3~1m` —— 可拾取物、道具",
        "  - 中   `1~3m`  —— 可互动家具、箱、柜",
        "  - 大   `3~6m`  —— 载具、大型装置",
        "  - 巨   `>6m`  —— 建筑、塔、门",
        "- 一个 AssetId 如果有多种 Scale 变体，主尺寸下方用子表列出",
        "",
        "## 用途",
        "",
        "- AI 挑物件时，按功能 + 尺寸双重筛选（如「找中等大小可开启的容器」）",
        "- 生成关卡前核对「能不能穿过门」「会不会把主角挡死」这类空间冲突",
        "- 配合 [SKILL.md 3D 物件选取规则](SKILL.md#3d-物件选取规则强制) 使用",
        "",
        "## 统计表（按尺寸档分组，档内按使用数降序）",
        "",
    ]

    # 分档分组输出
    for tier in TIER_ORDER:
        group = [x for x in aggregated if x["tier"] == tier]
        if not group:
            continue
        lines.append(f"### {tier}物件（最大边 {_tier_desc(tier)}）")
        lines.append("")
        lines.append("| AssetId | 名称 | 原始 Size | 常用 Scale | 实际尺寸[长×宽×高] | 最大边(m) | 主尺寸占比 | 出现关卡数 |")
        lines.append("|---------|------|-----------|-----------|---------------------|-----------|-----------|-----------|")
        for it in group:
            s = it["primary_size"]
            sc = it["primary_scale"]
            r = it["primary_real"]
            scale_str = fmt(sc[0]) if sc[0] == sc[1] == sc[2] else fmt_vec(sc)
            real_str = f"{fmt(r[0])} × {fmt(r[2])} × {fmt(r[1])}"  # 长(X) × 宽(Z) × 高(Y)
            pct = 100 * it["primary_cnt"] / it["total"]
            lines.append(
                f"| {it['aid']} | {it['name']} | {fmt_vec(s)} | {scale_str} | {real_str} | "
                f"{fmt(it['max_edge'])} | {pct:.0f}%({it['primary_cnt']}/{it['total']}) | {it['levels']} |"
            )
        lines.append("")

    # 追加：有多种尺寸变体的 AssetId 详单
    multi = [x for x in aggregated if len(x["combos"]) > 1]
    if multi:
        lines.append("## 多尺寸变体详单")
        lines.append("")
        lines.append("> 同一个 AssetId 在不同关卡被调成不同大小，这里列出所有变体供核对。")
        lines.append("")
        for it in multi:
            lines.append(f"### {it['aid']} | {it['name']}")
            lines.append("")
            lines.append("| 原始 Size | Scale | 实际尺寸 | 出现次数 |")
            lines.append("|-----------|-------|---------|---------|")
            for size, scale, cnt in it["combos"]:
                real = (size[0] * scale[0], size[1] * scale[1], size[2] * scale[2])
                sc_str = fmt(scale[0]) if scale[0] == scale[1] == scale[2] else fmt_vec(scale)
                real_str = f"{fmt(real[0])} × {fmt(real[2])} × {fmt(real[1])}"
                lines.append(f"| {fmt_vec(size)} | {sc_str} | {real_str} | {cnt} |")
            lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"已写出: {OUT}")


def _tier_desc(tier: str) -> str:
    return {
        "超小": "<0.3m",
        "小": "0.3~1m",
        "中": "1~3m",
        "大": "3~6m",
        "巨": ">6m",
    }[tier]


if __name__ == "__main__":
    main()
