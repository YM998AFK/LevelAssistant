"""
build_thumbnail_colors.py
下载物件缩略图并提取主色调，写入 resource_index.jsonl。
"""

import re
import json
import colorsys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from PIL import Image

# ── 路径配置 ──────────────────────────────────────────────────────────────────
ROOT = Path(r"c:\Users\Hetao\Desktop\公司")
PREVIEW_MD = ROOT / ".cursor/skills/level-common/资源预览图/preview_urls.md"
SAVE_DIR = ROOT / ".tmp_thumbnails"
COLOR_JSON = ROOT / "scripts/_color_results.json"
RESOURCE_JSONL = ROOT / ".cursor/skills/level-common/resource_index.jsonl"

SAVE_DIR.mkdir(exist_ok=True)

# ── Step 1: 解析物件 URL ──────────────────────────────────────────────────────
def parse_object_urls(md_path: Path) -> list[tuple[str, str]]:
    text = md_path.read_text(encoding="utf-8")
    idx = text.find("## 物件")
    if idx == -1:
        raise ValueError("未找到 '## 物件' 段落")
    obj_section = text[idx:]
    # 截止到下一个 ## 段（如果有）
    next_section = re.search(r"\n## ", obj_section[3:])
    if next_section:
        obj_section = obj_section[: next_section.start() + 3]
    pattern = r"AssetId=(\d+)\):\s*(https?://\S+)"
    return re.findall(pattern, obj_section)


# ── Step 2: 下载单张图 ────────────────────────────────────────────────────────
def download_one(asset_id: str, url: str) -> tuple[str, bool, str]:
    save_path = SAVE_DIR / f"{asset_id}.png"
    if save_path.exists():
        return asset_id, True, "cached"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        save_path.write_bytes(r.content)
        return asset_id, True, "ok"
    except Exception as e:
        return asset_id, False, str(e)


# ── Step 3: 提取主色调 ────────────────────────────────────────────────────────
def rgb_to_name(r: int, g: int, b: int) -> str:
    if max(r, g, b) - min(r, g, b) < 30:
        if max(r, g, b) > 200:
            return "白"
        if max(r, g, b) < 60:
            return "黑"
        return "灰"
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if s < 0.15:
        return "灰"
    h_deg = h * 360
    if h_deg < 15 or h_deg >= 345:
        return "红"
    if h_deg < 45:
        return "橙"
    if h_deg < 75:
        return "黄"
    if h_deg < 165:
        return "绿"
    if h_deg < 195:
        return "青"
    if h_deg < 255:
        return "蓝"
    if h_deg < 285:
        return "紫"
    if h_deg < 345:
        return "粉"
    return "红"


def dominant_color(img_path: Path) -> str:
    try:
        img = Image.open(img_path).convert("RGBA")
        bg = Image.new("RGB", img.size, (200, 200, 200))
        bg.paste(img, mask=img.split()[3])
        bg = bg.resize((32, 32))
        pixels = list(bg.getdata())
        r = sum(p[0] for p in pixels) // len(pixels)
        g = sum(p[1] for p in pixels) // len(pixels)
        b = sum(p[2] for p in pixels) // len(pixels)
        return rgb_to_name(r, g, b)
    except Exception:
        return "未知"


# ── Step 4: 合并到 resource_index.jsonl ──────────────────────────────────────
def patch_resource_index(color_results: dict[str, str]) -> int:
    lines = RESOURCE_JSONL.read_text(encoding="utf-8").splitlines()
    patched = 0
    new_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            new_lines.append(line)
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            new_lines.append(line)
            continue
        asset_id = str(obj.get("id", ""))
        if asset_id in color_results and obj.get("type") == "MeshPart":
            obj["dominant_color"] = color_results[asset_id]
            patched += 1
        new_lines.append(json.dumps(obj, ensure_ascii=False))
    RESOURCE_JSONL.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return patched


# ── 主流程 ────────────────────────────────────────────────────────────────────
def main():
    print("=== Step 1: 解析物件 URL ===")
    entries = parse_object_urls(PREVIEW_MD)
    print(f"  找到 {len(entries)} 条物件条目")

    print("\n=== Step 2: 并发下载缩略图 (max_workers=20) ===")
    ok_ids, fail_ids = [], []
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(download_one, aid, url): aid for aid, url in entries}
        done = 0
        for fut in as_completed(futures):
            asset_id, success, msg = fut.result()
            done += 1
            if success:
                ok_ids.append(asset_id)
                status = "✓"
            else:
                fail_ids.append(asset_id)
                status = "✗"
                print(f"  [{done}/{len(entries)}] {status} {asset_id}: {msg}")
            if done % 50 == 0 or done == len(entries):
                print(f"  进度: {done}/{len(entries)} | 成功: {len(ok_ids)} 失败: {len(fail_ids)}")

    print(f"\n下载完成 — 成功: {len(ok_ids)}, 失败: {len(fail_ids)}")

    print("\n=== Step 3: 提取主色调 ===")
    color_results: dict[str, str] = {}
    for i, asset_id in enumerate(ok_ids, 1):
        img_path = SAVE_DIR / f"{asset_id}.png"
        color_results[asset_id] = dominant_color(img_path)
        if i % 100 == 0 or i == len(ok_ids):
            print(f"  颜色提取进度: {i}/{len(ok_ids)}")

    # 统计颜色分布
    from collections import Counter
    dist = Counter(color_results.values())
    print("\n颜色分布:")
    for color, cnt in sorted(dist.items(), key=lambda x: -x[1]):
        print(f"  {color}: {cnt}")

    print("\n=== Step 4: 写入 _color_results.json ===")
    COLOR_JSON.write_text(
        json.dumps(color_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  已写入 {COLOR_JSON}")

    print("\n=== Step 5: 合并到 resource_index.jsonl ===")
    patched = patch_resource_index(color_results)
    print(f"  已更新 {patched} 条 MeshPart 记录")

    print("\n=== 汇总 ===")
    print(f"  下载成功: {len(ok_ids)}")
    print(f"  下载失败: {len(fail_ids)}")
    print(f"  颜色写入 resource_index.jsonl: {patched} 条")
    print("  颜色分布:", dict(dist))


if __name__ == "__main__":
    main()
