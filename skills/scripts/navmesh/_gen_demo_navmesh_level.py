# -*- coding: utf-8 -*-
"""
Demo 关卡生成:NavMesh 驱动的三角色静态站位。

场景: 21597 队长小木屋内景  (1 岛完整连通, ~212 m^2)
角色: 小核桃 / 队长 / 小核桃 2
目标: 3 个角色坐标全部吸附到 NavMesh 表面,互相距离 >= 1m,
      跑 validate_positions 全 PASS = 不穿模.

不使用任何策划母本,只拿一份已存在的 workspace JSON 作"引擎结构骨架"
(Folder/services, CameraService 等是引擎硬要求的,不算策划参考)。
"""
from __future__ import annotations
import copy
import io
import json
import shutil
import sys
import time
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "scripts" / "navmesh"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import navmesh_validate as V
import pkg_utils

# ---- 参数 ----
SCENE_ASSET_ID = 21597                 # 队长小木屋内景
LEVEL_NAME = "navmesh_demo_trio"       # 输出 zip 文件名
DESC = "NavMesh 驱动的三角色站位 demo"
CHAR_NAMES = ["小核桃", "队长", "小核桃2"]

# 角色 AssetId (引擎已知, 模板里拿到):
#   小核桃 12156 / 队长 12146
# "小核桃2" 复用 12156 即可, 只改 Name.
CHAR_ASSETS = {"小核桃": 12156, "队长": 12146, "小核桃2": 12156}

# "引擎结构骨架"源 workspace (只拷整体 JSON 骨架, 不用里面的剧情/脚本)
TEMPLATE_WS = REPO / "output" / "new" / "_xiaohetao_duizhang_workdir" / "f05766a9-ec87-4509-896d-440e406f3e40.ws"

WORKDIR = REPO / "output" / "new" / f"_{LEVEL_NAME}_workdir"
OUT_ZIP = REPO / "output" / "new" / f"{LEVEL_NAME}.zip"


def new_uuid32() -> str:
    return uuid.uuid4().hex


def new_uuid4() -> str:
    return str(uuid.uuid4())


def make_character(name: str, asset_id: int, position_xyz: tuple, yaw_deg: float) -> dict:
    return {
        "type": "Character",
        "id": new_uuid32(),
        "props": {
            "Name": name,
            "EditMode": 0,
            "Visible": True,
            "Position": [f"{position_xyz[0]:g}", f"{position_xyz[1]:g}", f"{position_xyz[2]:g}"],
            "EulerAngles": ["0", f"{yaw_deg:g}", "0"],
            "RotConstraint": 0,
            "ConstraintEulerAngles": ["0", "0", "0"],
            "Scale": "0.6",
            "CastShadow": True,
            "Color": "#FFFFFFFF",
            "Material": "Basic",
            "Transparency": "0",
            "Size": ["1", "1.967731", "1"],
            "Touchable": False,
            "Moveable": False,
            "EnableTouchEvent": True,
            "PhysicsPreset": "Normal",
            "Density": "0.1",
            "Friction": "0.3",
            "Bounce": "0.5",
            "UseGravity": True,
            "Lighting": False,
            "LightType": "Point",
            "LightFace": "Top",
            "LightColor": "#FFFFFFFF",
            "LightIntensity": "1",
            "LightRange": "8",
            "LightSpotAngle": "120",
            "LightInnerSpotAngle": "60",
            "AssetId": asset_id,
            "EmotionAnimations": "[]",
        },
        "children": [
            {
                "type": "BlockScript",
                "id": new_uuid32(),
                "props": {"Name": "BlockScript", "EditMode": 0},
                "fragments": [
                    {
                        "pos": ["200", "200"],
                        "head": {
                            "define": "WhenGameStarts",
                            "sections": [
                                {
                                    "children": [
                                        {
                                            "define": "GotoPosition3D",
                                            "sections": [
                                                {
                                                    "params": [
                                                        {"type": "var", "val": f"{position_xyz[0]:g}"},
                                                        {"type": "var", "val": f"{position_xyz[1]:g}"},
                                                        {"type": "var", "val": f"{position_xyz[2]:g}"},
                                                    ]
                                                }
                                            ],
                                        },
                                        {
                                            "define": "PointInDirection",
                                            "sections": [
                                                {
                                                    "params": [
                                                        {},
                                                        {"type": "var", "val": f"{yaw_deg:g}"},
                                                    ]
                                                }
                                            ],
                                        },
                                    ]
                                }
                            ],
                        },
                    }
                ],
                "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
            }
        ],
    }


def make_control(x: float, y: float, z: float) -> dict:
    return {
        "type": "MeshPart",
        "id": new_uuid32(),
        "props": {
            "Name": "control",
            "EditMode": 0,
            "Visible": False,
            "Position": [f"{x:g}", f"{y:g}", f"{z:g}"],
            "EulerAngles": ["0", "90", "0"],
            "RotConstraint": 0,
            "ConstraintEulerAngles": ["0", "0", "0"],
            "Scale": "1",
            "CastShadow": True,
            "Color": "#FFFFFFFF",
            "Material": "Basic",
            "Transparency": "0",
            "Size": ["1", "1", "1"],
            "Touchable": False,
            "Moveable": False,
            "EnableTouchEvent": True,
            "PhysicsPreset": "Normal",
            "Density": "0.1",
            "Friction": "0.3",
            "Bounce": "0.5",
            "UseGravity": True,
            "Lighting": False,
            "LightType": "Point",
            "LightFace": "Top",
            "LightColor": "#FFFFFFFF",
            "LightIntensity": "1",
            "LightRange": "8",
            "LightSpotAngle": "120",
            "LightInnerSpotAngle": "60",
            "AssetId": 10548,
            "EmotionAnimations": "[]",
        },
        "props2": {
            "@/fall": {"type": "Simple", "value": ""},
            "@/collide": {"type": "Simple", "value": ""},
            "@/fixed": {"type": "Simple", "value": ""},
        },
        "children": [],
    }


def pick_positions_via_navmesh() -> list[tuple[str, tuple[float, float, float]]]:
    """用 NavMesh 工具链给 3 个角色挑位置: 都在主岛, 互相距离 >= 1.5m, 离边界 >= 1m。"""
    summary = V.scene_summary(SCENE_ASSET_ID)
    print(f"[scene {SCENE_ASSET_ID}] {summary['name']}")
    print(f"  islands={summary['island_count']}  "
          f"walkable={summary['total_walkable_xz_area']} m^2  "
          f"largest_centroid={summary['largest_island_centroid']}")

    # 尝试几组 seed 一直到拿到 3 个点
    for seed in range(1, 30):
        pts = V.place_points_inside(
            SCENE_ASSET_ID,
            count=3, min_dist=1.5, margin=1.0,
            island_index=0, seed=seed,
        )
        if len(pts) == 3:
            print(f"[pick] seed={seed} 拿到 3 个位置")
            return [(nm, p.position) for nm, p in zip(CHAR_NAMES, pts)]
    raise RuntimeError("30 个 seed 都没采够 3 个点, 换 min_dist/margin")


def load_template() -> dict:
    data = json.loads(TEMPLATE_WS.read_text(encoding="utf-8"))
    # 拿原始骨架: 只留 Folder(services) + CameraService-like 以外的都删
    scene = data["scene"]
    keep_types = {"Folder"}  # 只保留引擎必需的 services 文件夹
    new_children = [c for c in scene.get("children", []) if c.get("type") in keep_types]
    scene["children"] = new_children
    return data


def main() -> int:
    # 1. 加载结构骨架
    data = load_template()
    scene = data["scene"]

    # 2. 切场景
    scene["props"]["AssetId"] = SCENE_ASSET_ID
    scene["props"]["Name"] = "Scene"

    # 3. 元数据
    data["name"] = LEVEL_NAME
    data["desc"] = DESC
    data["author"] = ""
    data["modified"] = int(time.time())

    # 4. NavMesh 选位置
    picked = pick_positions_via_navmesh()

    # 5. 放 control(角色 XZ 均值)
    xs = [p[0] for _, p in picked]
    zs = [p[2] for _, p in picked]
    ctrl_x = sum(xs) / len(xs)
    ctrl_z = sum(zs) / len(zs)
    ctrl_y = picked[0][1][1]  # 任取一个角色的 y (贴地)
    scene["children"].append(make_control(ctrl_x, ctrl_y, ctrl_z))

    # 6. 摆角色
    for i, (name, pos) in enumerate(picked):
        yaw = [90, 180, 270][i % 3]  # 朝 3 个不同方向, 互相看不到就少了
        scene["children"].append(make_character(name, CHAR_ASSETS[name], pos, yaw))

    # 7. NavMesh 严格验证
    print("\n[NavMesh validate]")
    rep = V.validate_positions(
        SCENE_ASSET_ID,
        [(name, pos) for name, pos in picked],
        require_reachable_pairs=[
            (CHAR_NAMES[0], CHAR_NAMES[1]),
            (CHAR_NAMES[0], CHAR_NAMES[2]),
        ],
        min_spacing=1.0,
        snap=True,
        max_snap_dist=1.0,
    )
    print(rep.pretty())
    assert rep.ok, f"NavMesh 验证未通过: {rep.issues}"

    # 8. 写 workspace 到 workdir
    WORKDIR.mkdir(parents=True, exist_ok=True)
    # 清空 workdir 里上次的 .ws/solution.json
    for p in WORKDIR.glob("*"):
        if p.is_file():
            p.unlink()

    ws_uuid = new_uuid4()
    ws_file = WORKDIR / f"{ws_uuid}.ws"
    ws_file.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    # 9. 写 icon 占位图 (1×1 灰色 PNG, 引擎需要 icon 字段非空)
    ICON_SRC = REPO / "output" / "new" / "_xiaohetao_duizhang_workdir" / "2873199d-1e16-4b7f-84d8-509e37482fcf.png"
    icon_uuid = new_uuid4()
    icon_dest = WORKDIR / f"{icon_uuid}.png"
    if ICON_SRC.exists():
        shutil.copy2(ICON_SRC, icon_dest)
    else:
        # 最小合法 1x1 白色 PNG (46 bytes)
        import base64
        TINY_PNG = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8"
            "z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=="
        )
        icon_dest.write_bytes(TINY_PNG)

    icon_path_in_zip = f"pangu3d/universe/develop/612921974867361800/{icon_uuid}.png"

    # 10. 写 solution.json
    project_uuid = new_uuid4()
    solution_uid = new_uuid4()   # init ← 和 export_info.json 保持一致
    solution = {
        "init": solution_uid,
        "name": LEVEL_NAME,
        "author": "",
        "modified": int(time.time()),
        "version": 1,
        "projects": [
            {
                "file": f"pangu3d/universe/develop/612921974867361800/{ws_uuid}.ws",
                "icon": icon_path_in_zip,
                "name": "Project_0",
                "uuid": project_uuid,
            }
        ],
        "globals": [
            {
                "refs": [project_uuid],
                "obj": {
                    "type": "CameraService",
                    "id": new_uuid32(),
                    "props": {
                        "Name": "Camera",
                        "EditMode": 0,
                        "Current": "Camera45",
                    },
                    "children": [
                        {
                            "type": "BlockScript",
                            "id": new_uuid32(),
                            "props": {"Name": "BlockScript", "EditMode": 0},
                            "uiState": {"pos": ["510", "848"], "scroll": ["722", "746"], "scale": "1"},
                        },
                        {
                            "type": "BlockScript",
                            "id": new_uuid32(),
                            "props": {"Name": "BlockScript", "EditMode": 0},
                            "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                        },
                    ],
                },
            }
        ],
    }
    (WORKDIR / "solution.json").write_text(
        json.dumps(solution, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    # 11. 写 export_info.json (引擎合法性校验必须有)
    export_info = {"solutionUid": solution_uid}
    (WORKDIR / "export_info.json").write_text(
        json.dumps(export_info, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    # 12. 打 zip
    if OUT_ZIP.exists():
        OUT_ZIP.unlink()
    pkg_utils.pack_zip_clean(str(WORKDIR), str(OUT_ZIP))

    size = OUT_ZIP.stat().st_size
    print(f"\n[OK] 生成: {OUT_ZIP}  ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
