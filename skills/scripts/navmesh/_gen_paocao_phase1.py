# -*- coding: utf-8 -*-
"""
天空王国（岔路版）抗寒跑操 Phase 1
  - 从 loop#0（外轮廓 141.7m）采 8 个等距航点
  - 3 个角色分别站在航点 0、2、5（错开起跑位）
  - BlockScript 留空，等待 MCP add_fragment 写入 Forever 跑圈逻辑
  - 输出 _phase1_meta.json（含 waypoints + 各角色 script_id）
"""
from __future__ import annotations
import io, json, shutil, sys, time, uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "scripts" / "navmesh"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import navmesh_query as Q
import navmesh_validate as V
from navmesh_loader import load_navmesh
import pkg_utils
import scene_utils

SCENE_ASSET_ID = 20734          # 天空王国（岔路版）
LEVEL_NAME     = "tiankong_paocao"
WORKDIR = REPO / "output" / "new" / f"_{LEVEL_NAME}_workdir"
TEMPLATE_ZIP   = REPO / "output" / "new" / "小核桃队长动作秀.zip"
LOOP_INDEX     = 0              # 外轮廓
N_WAYPOINTS    = 8              # 跑圈航点数

CHAR_NAMES  = ["小核桃", "队长", "小核桃2"]
CHAR_ASSETS = {"小核桃": 12156, "队长": 12146, "小核桃2": 12156}
CHAR_SIZES  = {
    "小核桃": ["1", "1.967731", "1"],
    "队长":   ["1", "2.277619", "1"],
    "小核桃2": ["1", "1.967731", "1"],
}
# 3 个角色分别从 8 个航点的第 0、2、5 个出发（错开约 1/3 圈）
START_INDICES = [0, 2, 5]

def new_uuid32(): return uuid.uuid4().hex
def new_uuid4():  return str(uuid.uuid4())


# ── 1. 解压模板 ──────────────────────────────────────────────────────────
if WORKDIR.exists():
    shutil.rmtree(WORKDIR)
pkg_utils.extract_zip_into(str(TEMPLATE_ZIP), str(WORKDIR), force=True)
ws_files = list(WORKDIR.glob("*.ws"))
assert ws_files, "解压后没找到 .ws 文件"
WS_PATH = ws_files[0]
print(f"[1] 解压到 {WORKDIR.name}/  ws={WS_PATH.name}")


# ── 2. 加载 + 改 scene AssetId ───────────────────────────────────────────
data = json.loads(WS_PATH.read_text(encoding="utf-8"))
scene = data["scene"]
scene["props"]["AssetId"] = SCENE_ASSET_ID
data["name"] = LEVEL_NAME
data["desc"] = "天空王国（岔路版）抗寒跑操 demo（NavMesh 边界驱动）"
data["modified"] = int(time.time())
print(f"[2] 场景 AssetId → {SCENE_ASSET_ID}")


# ── 3. 清空旧节点 ─────────────────────────────────────────────────────────
keep_types = {"Folder"}
scene["children"] = [c for c in scene.get("children", []) if c["type"] in keep_types]
print(f"[3] 清空旧角色节点，剩 {len(scene['children'])} 个 Folder(services)")


# ── 4. 采样 8 个边界航点 ──────────────────────────────────────────────────
m = load_navmesh(SCENE_ASSET_ID)
raw_waypoints = Q.sample_boundary(m, N_WAYPOINTS, loop_index=LOOP_INDEX)
perimeter = Q._loop_perimeter([m.cverts[i] for i in m.boundary_loops[LOOP_INDEX]])

print(f"[4] loop#{LOOP_INDEX} 周长={perimeter:.1f}m → {N_WAYPOINTS} 个航点（间距≈{perimeter/N_WAYPOINTS:.1f}m）")
for i, wp in enumerate(raw_waypoints):
    print(f"    wp{i}: ({wp[0]:.3f}, {wp[1]:.3f}, {wp[2]:.3f})")

# 把 waypoints 转成 [x,y,z] float list
waypoints = [[wp[0], wp[1], wp[2]] for wp in raw_waypoints]


# ── 5. 放 control ─────────────────────────────────────────────────────────
cx = sum(wp[0] for wp in waypoints) / len(waypoints)
cy = waypoints[0][1]
cz = sum(wp[2] for wp in waypoints) / len(waypoints)
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


# ── 6. 放 3 个角色（各自起跑位，BlockScript 留空）──────────────────────────
char_script_ids = {}
# 面向下一个航点
def yaw_toward(cur, nxt):
    import math
    dx, dz = nxt[0]-cur[0], nxt[2]-cur[2]
    deg = math.degrees(math.atan2(dx, dz))
    return round(deg % 360)

for ci, (name, si) in enumerate(zip(CHAR_NAMES, START_INDICES)):
    pos = waypoints[si]
    next_wp = waypoints[(si + 1) % N_WAYPOINTS]
    yaw = yaw_toward(pos, next_wp)
    sid = new_uuid32()
    char_script_ids[name] = sid
    char = {
        "type": "Character",
        "id": new_uuid32(),
        "props": {
            "Name": name, "EditMode": 0, "Visible": True,
            "Position": [f"{pos[0]:.4g}", f"{pos[1]:.4g}", f"{pos[2]:.4g}"],
            "EulerAngles": ["0", f"{yaw}", "0"],
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
    print(f"[6] {name}: start=wp{si} pos=({pos[0]:.3f},{pos[1]:.3f},{pos[2]:.3f}) yaw={yaw}")

print(f"    共 {len(CHAR_NAMES)} 个角色放置完毕")


# ── 7. 写回 .ws ────────────────────────────────────────────────────────────
WS_PATH.write_text(json.dumps(data, ensure_ascii=False, separators=(",",":")), encoding="utf-8")
print(f"[7] 写回 {WS_PATH.name}  ({WS_PATH.stat().st_size} bytes)")


# ── 8. 输出元数据（含 waypoints 供 MCP 使用）──────────────────────────────
meta = {
    "ws_path": str(WS_PATH),
    "char_script_ids": char_script_ids,
    "ctrl_script_id": ctrl_script_id,
    "waypoints": waypoints,          # 8 个 [x,y,z]
    "start_indices": START_INDICES,  # [0,2,5]
    "n_waypoints": N_WAYPOINTS,
}
meta_path = WORKDIR / "_phase1_meta.json"
meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[8] 元数据 → {meta_path.name}")
print()
print("=== Phase 1 完成 ===")
for name, sid in char_script_ids.items():
    si = START_INDICES[CHAR_NAMES.index(name)]
    print(f"  {name}: script_id={sid}  start=wp{si}")
print("  waypoints:", waypoints)
