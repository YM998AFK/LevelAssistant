# -*- coding: utf-8 -*-
"""
天空王国（岔路版）Phase 1:
  - scene AssetId = 20734
  - 4 个角色放置到最大岛 NavMesh 可行走面
  - BlockScript 留空等待 MCP add_fragment
"""
from __future__ import annotations
import io, json, shutil, sys, time, uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "scripts" / "navmesh"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import navmesh_validate as V
import pkg_utils
import scene_utils

SCENE_ASSET_ID = 20734          # 天空王国（岔路版）
LEVEL_NAME     = "tiankong_quartet"
WORKDIR = REPO / "output" / "new" / f"_{LEVEL_NAME}_workdir"
TEMPLATE_ZIP   = REPO / "output" / "new" / "小核桃队长动作秀.zip"

CHAR_NAMES  = ["小核桃", "队长", "机甲小核桃", "小核桃2"]
CHAR_ASSETS = {
    "小核桃":   12156,
    "队长":     12146,
    "机甲小核桃": 12158,
    "小核桃2":  12156,
}
CHAR_SIZES = {
    "小核桃":   ["1", "1.967731", "1"],
    "队长":     ["1", "2.277619", "1"],
    "机甲小核桃": ["1", "2", "1"],
    "小核桃2":  ["1", "1.967731", "1"],
}

def new_uuid32(): return uuid.uuid4().hex
def new_uuid4():  return str(uuid.uuid4())


# ── 1. 解压模板 ──────────────────────────────────────────────────────────
if WORKDIR.exists():
    shutil.rmtree(WORKDIR)
info = pkg_utils.extract_zip_into(str(TEMPLATE_ZIP), str(WORKDIR), force=True)
ws_files = list(WORKDIR.glob("*.ws"))
assert ws_files, "解压后没找到 .ws 文件"
WS_PATH = ws_files[0]
print(f"[1] 解压到 {WORKDIR.name}/  ws={WS_PATH.name}")


# ── 2. 加载 + 改 scene AssetId ───────────────────────────────────────────
data = json.loads(WS_PATH.read_text(encoding="utf-8"))
scene = data["scene"]
scene["props"]["AssetId"] = SCENE_ASSET_ID
data["name"] = LEVEL_NAME
data["desc"] = "天空王国（岔路版）四角色站位 demo（NavMesh 驱动）"
data["modified"] = int(time.time())
print(f"[2] 场景 AssetId → {SCENE_ASSET_ID}")


# ── 3. 清空旧角色节点 ─────────────────────────────────────────────────────
keep_types = {"Folder"}
scene["children"] = [c for c in scene.get("children", []) if c["type"] in keep_types]
print(f"[3] 清空旧角色节点，剩 {len(scene['children'])} 个 Folder(services)")


# ── 4. NavMesh 选位置（主岛 island_index=0，788m²）───────────────────────
summary = V.scene_summary(SCENE_ASSET_ID)
print(f"[4] 场景摘要: islands={summary['island_count']}  area={summary['total_walkable_xz_area']:.0f}m²")
print(f"    主岛重心: {summary['largest_island_centroid']}")

for seed in range(1, 80):
    pts = V.place_points_inside(SCENE_ASSET_ID, count=4, min_dist=2.5, margin=2.0,
                                island_index=0, seed=seed)
    if len(pts) == 4:
        print(f"    seed={seed} 拿到 4 个位置")
        break
else:
    raise RuntimeError("NavMesh 采样失败：无法在 island 0 找到 4 个满足间距的点")

positions = [(CHAR_NAMES[i], pts[i].position) for i in range(4)]
for name, pos in positions:
    print(f"    {name}: ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f})")

# 校验
rep = V.validate_positions(
    SCENE_ASSET_ID, positions,
    require_reachable_pairs=[
        (CHAR_NAMES[0], CHAR_NAMES[1]),
        (CHAR_NAMES[0], CHAR_NAMES[2]),
        (CHAR_NAMES[1], CHAR_NAMES[3]),
    ],
    min_spacing=2.0,
)
assert rep.ok, f"NavMesh FAIL: {rep.issues}"
print(f"    NavMesh validate: PASS")


# ── 5. 放 control ─────────────────────────────────────────────────────────
cx = sum(p[0] for _, p in positions) / 4
cy = positions[0][1][1]
cz = sum(p[2] for _, p in positions) / 4
ctrl_script_id = new_uuid32()
control = {
    "type": "MeshPart",
    "id": new_uuid32(),
    "props": {
        "Name": "control", "EditMode": 0, "Visible": False,
        "Position": [f"{cx:.4g}", f"{cy:.4g}", f"{cz:.4g}"],
        "EulerAngles": ["0","0","0"], "RotConstraint": 0,
        "ConstraintEulerAngles": ["0","0","0"], "Scale": "1",
        "CastShadow": True, "Color": "#FFFFFFFF", "Material": "Basic",
        "Transparency": "0", "Size": ["1","1","1"],
        "Touchable": False, "Moveable": False, "EnableTouchEvent": True,
        "PhysicsPreset": "Normal", "Density": "0.1", "Friction": "0.3",
        "Bounce": "0.5", "UseGravity": True, "Lighting": False,
        "LightType": "Point", "LightFace": "Top", "LightColor": "#FFFFFFFF",
        "LightIntensity": "1", "LightRange": "8",
        "LightSpotAngle": "120", "LightInnerSpotAngle": "60",
        "AssetId": 10548, "EmotionAnimations": "[]",
    },
    "props2": {
        "@/fall": {"type": "Simple", "value": ""},
        "@/collide": {"type": "Simple", "value": ""},
        "@/fixed": {"type": "Simple", "value": ""},
    },
    "children": [{
        "type": "BlockScript", "id": ctrl_script_id,
        "props": {"Name": "BlockScript", "EditMode": 0},
        "fragments": [],
        "uiState": {"pos": ["0","0"], "scroll": ["0","0"], "scale": "1"},
    }],
}
scene["children"].append(control)


# ── 6. 放 4 个角色（空 BlockScript）────────────────────────────────────────
char_script_ids = {}
yaws = [45, 135, 225, 315]
for i, (name, pos) in enumerate(positions):
    sid = new_uuid32()
    char_script_ids[name] = sid
    char = {
        "type": "Character",
        "id": new_uuid32(),
        "props": {
            "Name": name, "EditMode": 0, "Visible": True,
            "Position": [f"{pos[0]:.4g}", f"{pos[1]:.4g}", f"{pos[2]:.4g}"],
            "EulerAngles": ["0", f"{yaws[i]}", "0"],
            "RotConstraint": 0, "ConstraintEulerAngles": ["0","0","0"],
            "Scale": "0.6", "CastShadow": True, "Color": "#FFFFFFFF",
            "Material": "Basic", "Transparency": "0",
            "Size": CHAR_SIZES[name],
            "Touchable": False, "Moveable": False, "EnableTouchEvent": True,
            "PhysicsPreset": "Normal", "Density": "0.1", "Friction": "0.3",
            "Bounce": "0.5", "UseGravity": True, "Lighting": False,
            "LightType": "Point", "LightFace": "Top", "LightColor": "#FFFFFFFF",
            "LightIntensity": "1", "LightRange": "8",
            "LightSpotAngle": "120", "LightInnerSpotAngle": "60",
            "AssetId": CHAR_ASSETS[name], "EmotionAnimations": "[]",
        },
        "children": [{
            "type": "BlockScript", "id": sid,
            "props": {"Name": "BlockScript", "EditMode": 0},
            "fragments": [],
            "uiState": {"pos": ["200","200"], "scroll": ["0","0"], "scale": "1"},
        }],
    }
    scene["children"].append(char)
print(f"[6] 添加 {len(positions)} 个角色（BlockScript 暂空）")


# ── 7. 写回 .ws ────────────────────────────────────────────────────────────
WS_PATH.write_text(json.dumps(data, ensure_ascii=False, separators=(",",":")), encoding="utf-8")
print(f"[7] 写回 {WS_PATH.name}  ({WS_PATH.stat().st_size} bytes)")

# ── 8. 输出后续 MCP 需要的元数据 ──────────────────────────────────────────
meta = {
    "ws_path": str(WS_PATH),
    "char_script_ids": char_script_ids,
    "ctrl_script_id": ctrl_script_id,
    "positions": {n: list(p) for n, p in positions},
}
meta_path = WORKDIR / "_phase1_meta.json"
meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[8] 元数据 → {meta_path.name}")
print()
print("=== Phase 1 完成，等待 MCP add_fragment ===")
print(f"ws_path = {WS_PATH}")
for name, sid in char_script_ids.items():
    pos = next(p for n, p in positions if n == name)
    print(f"  {name}: script_id={sid}  pos=({pos[0]:.4g},{pos[1]:.4g},{pos[2]:.4g})")
