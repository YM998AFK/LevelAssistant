"""
Generate "抗寒跑操-小核桃队长展喵" level zip.

Three Q-ish characters (小核桃/队长/展喵) are stuck inside 队长小木屋 (scene 21597).
They shiver with dangfeng animations, decide to run laps around the room to warm up,
run 2 laps past 4 invisible waypoints (P1..P4), then recover and celebrate.

Pure演出 (no OJ, no cin_cut). Based on 参考-extracted/三角对白-小核桃队长展喵 skeleton.

Key SKILL rules followed:
  - Position static: 米 (meters)
  - CameraFollow distance/height: 厘米 (centimeters)  ← preset B: 640, 0, 500
  - Blocks平铺 (no `next` chains) — use sections[0].children arrays only
  - params slot counts per level-common "代码块参数槽规则"
  - Character.Position facing 90 = 朝X+ (面向摄像机，和摄像机-90对冲)
  - SaySeconds blocks the running coroutine — 跑操中途不插台词
  - Use PlaySound(name) referencing Sound nodes at scene root
"""

from __future__ import annotations

import json
import shutil
import tempfile
import time
import uuid
import zipfile
from pathlib import Path

# --------------------------------------------------------------------------- #
# Asset IDs (all verified in asset_catalog.md / presets.md)
# --------------------------------------------------------------------------- #
SCENE_ASSETID = 21597      # 队长小木屋内景
CHAR_XHT = 12156           # 小核桃
CHAR_DZ = 12146            # 队长
CHAR_ZM = 12153            # 展喵
BGM_ASSETID = 28986        # 轻松休闲1
SND_TUXIAN = 28972         # 凸显
SND_SHENGWEN = 29278       # 升温
SND_SUCCESS = 28966        # 结算效果-成功
CONTROL_MESH = 10548       # 不可见占位 MeshPart
UI_BASIC = 27561
UI_ICONS = 27562

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def new_uuid_dashed() -> str:
    return str(uuid.uuid4())


def new_uuid_hex() -> str:
    return uuid.uuid4().hex


def var(v: str | int | float) -> dict:
    """A value-typed parameter."""
    return {"type": "var", "val": str(v)}


def block(b: dict) -> dict:
    """Wrap a block-typed parameter (used for nested operators)."""
    return {"type": "block", "val": b}


# Block constructor — "children" approach (no next chains). Each block returns
# {"define": ..., "sections": [{"params": [...], "children": [...]?}]}
def blk(define: str, params: list | None = None, children: list | None = None) -> dict:
    section: dict = {"params": params or []}
    if children is not None:
        section["children"] = children
    return {"define": define, "sections": [section]}


# Hat-block convenience wrappers
def hat_when_game_starts(children: list) -> dict:
    return blk("WhenGameStarts", [], children)


def hat_on_message(msg: str, children: list) -> dict:
    return blk("WhenReceiveMessage", [var(msg)], children)


# Action builders
def point_in_direction(deg: float | str) -> dict:
    return blk("PointInDirection", [{}, var(deg)])


def point_in_pitch(deg: float | str) -> dict:
    return blk("PointInPitch", [{}, var(deg)])


def set_size(pct: int | str) -> dict:
    return blk("SetSize", [{}, var(pct)])


def set_speed_mul(v: float | str) -> dict:
    return blk("SetSpeedMul", [var(v)])


def run_to_target(target: str) -> dict:
    return blk("RunToTargetAndWait", [var(target)])


def play_animation(name: str) -> dict:
    return blk("PlayAnimation", [var(name)])


def play_animation_until(name: str) -> dict:
    return blk("PlayAnimationUntil", [var(name)])


def say_seconds(text: str, seconds: float | str) -> dict:
    return blk("SaySeconds", [var(text), var(seconds)])


def wait_seconds(sec: float | str) -> dict:
    return blk("WaitSeconds", [var(sec)])


def play_sound(name: str) -> dict:
    return blk("PlaySound", [var(name)])


def play_bgm(name: str, volume: int | str = 100) -> dict:
    return blk("PlayBGM", [var(name), var(volume)])


def broadcast(msg: str) -> dict:
    return blk("BroadcastMessage", [var(msg)])


def broadcast_and_wait(msg: str) -> dict:
    return blk("BroadcastMessageAndWait", [var(msg)])


def repeat_(times: int | str, children: list) -> dict:
    return blk("Repeat", [var(times)], children)


def camera_follow(target: str, dist: int, offy: int, height: int) -> dict:
    return blk(
        "CameraFollow",
        [var(target), var(dist), var(offy), var(height)],
    )


def set_fov(v: int) -> dict:
    return blk("SetCameraFOV", [var(v)])


def fragment(x: int, y: int, head: dict) -> dict:
    return {"pos": [str(x), str(y)], "head": head}


def block_script(uid: str, fragments: list) -> dict:
    return {
        "type": "BlockScript",
        "id": uid,
        "props": {"Name": "BlockScript", "EditMode": 0},
        "fragments": fragments,
    }


# --------------------------------------------------------------------------- #
# Fragment authoring — one function per character / per control
# --------------------------------------------------------------------------- #


def camera_fragment() -> dict:
    """Camera preset B: 室内俯 45 广角."""
    return fragment(
        80,
        80,
        hat_when_game_starts(
            [
                set_fov(25),
                point_in_direction(-90),
                point_in_pitch(125),
                camera_follow("control", 640, 0, 500),
            ]
        ),
    )


def bgm_fragment() -> dict:
    return fragment(80, 80, hat_when_game_starts([play_bgm("轻松休闲1", 100)]))


def xiaohetao_script_fragments() -> list:
    """小核桃: 剧情主角 + 跑操领队."""
    init_hat = hat_when_game_starts(
        [
            point_in_direction(90),
            set_size(80),
            play_animation("idle"),
        ]
    )

    # Phase 1 · 冻僵
    frag_shiver = hat_on_message(
        "冻僵-3",
        [
            play_animation("dangfeng"),
            say_seconds("再这么冻下去,手指都不听使唤了!", 2.3),
            play_animation("idle"),
        ],
    )

    # Phase 2 · 出主意
    frag_idea = hat_on_message(
        "出主意",
        [
            play_animation_until("jingya"),
            play_sound("凸显"),
            play_animation("taishou_loop"),
            say_seconds("有办法!绕屋子跑操,跑起来就暖和了!", 3.3),
            play_animation("idle"),
        ],
    )

    # Phase 2b · 口令
    frag_cmd = hat_on_message(
        "口令",
        [
            play_animation("taishou_loop"),
            say_seconds("一、二——出发!", 0.9),
            play_animation("idle"),
        ],
    )

    # Phase 3 · 跑操(领队, 2 圈)
    frag_run = hat_on_message(
        "跑操开始",
        [
            set_speed_mul(2.8),
            repeat_(
                2,
                [
                    run_to_target("P2"),
                    run_to_target("P3"),
                    run_to_target("P4"),
                    run_to_target("P1"),
                ],
            ),
            play_animation("idle"),
        ],
    )

    # Phase 4 · 暖和了
    # ⚠️ 不用 PlayAnimationUntil("*_loop") 避免 loop 动画永久阻塞
    frag_warm = hat_on_message(
        "暖和了-3",
        [
            play_animation("shenchushuangshou_loop"),
            say_seconds("合影一张!——跑操小队,成立!", 2.3),
            play_animation("idle"),
        ],
    )

    return [
        fragment(60, 60, init_hat),
        fragment(60, 260, frag_shiver),
        fragment(60, 440, frag_idea),
        fragment(60, 640, frag_cmd),
        fragment(60, 820, frag_run),
        fragment(60, 1060, frag_warm),
    ]


def duizhang_script_fragments() -> list:
    """队长: 跟队伍, 发抖/抬头."""
    init_hat = hat_when_game_starts(
        [
            point_in_direction(90),
            set_size(80),
            play_animation("idle"),
        ]
    )

    frag_shiver = hat_on_message(
        "冻僵-2",
        [
            play_animation("dangfeng"),
            say_seconds("刚刚有股寒流灌进来,炉子又熄了……", 2.3),
            play_animation("idle"),
        ],
    )

    frag_reply = hat_on_message(
        "回应",
        [
            play_animation("taitou_Loop02"),
            say_seconds("身体发热确实能抗寒。跟我走!", 1.8),
            play_animation("idle02"),
        ],
    )

    # 队长跑操错位 0.3s
    frag_run = hat_on_message(
        "跑操开始",
        [
            wait_seconds(0.3),
            set_speed_mul(2.6),
            repeat_(
                2,
                [
                    run_to_target("P2"),
                    run_to_target("P3"),
                    run_to_target("P4"),
                    run_to_target("P1"),
                ],
            ),
            play_animation("idle"),
        ],
    )

    frag_warm = hat_on_message(
        "暖和了-2",
        [
            play_animation("taitou_Loop"),
            wait_seconds(0.8),
            play_animation("idle02"),
            say_seconds("体育锻炼,抗寒秘籍。下次炉子熄了还这样干!", 2.3),
            play_animation("idle"),
        ],
    )

    return [
        fragment(60, 60, init_hat),
        fragment(60, 260, frag_shiver),
        fragment(60, 460, frag_reply),
        fragment(60, 660, frag_run),
        fragment(60, 900, frag_warm),
    ]


def zhanmiao_script_fragments() -> list:
    """展喵: 最虚弱 → 被感染 → 恢复点赞."""
    init_hat = hat_when_game_starts(
        [
            point_in_direction(90),
            set_size(80),
            play_animation("idle"),
        ]
    )

    frag_shiver = hat_on_message(
        "冻僵-1",
        [
            play_animation("xuruo_loop"),
            wait_seconds(0.6),
            play_animation("xusheng"),
            say_seconds("这...这屋子比外面还冷啊喵!", 2.3),
            play_animation("idle"),
        ],
    )

    frag_reply = hat_on_message(
        "回应",
        [
            play_animation("taitou_Loop"),
            say_seconds("喵喵...那、那我也跟上!", 1.8),
            play_animation("idle"),
        ],
    )

    # 展喵错位 0.6s,且速度稍慢 (体现虚弱)
    frag_run = hat_on_message(
        "跑操开始",
        [
            wait_seconds(0.6),
            set_speed_mul(2.2),
            repeat_(
                2,
                [
                    run_to_target("P2"),
                    run_to_target("P3"),
                    run_to_target("P4"),
                    run_to_target("P1"),
                ],
            ),
            play_animation("idle"),
        ],
    )

    frag_warm = hat_on_message(
        "暖和了-1",
        [
            play_animation_until("chuanqi"),
            play_animation("dianzan"),
            say_seconds("喵~ 真的暖起来了!这办法绝了!", 2.3),
            play_animation("idle"),
        ],
    )

    return [
        fragment(60, 60, init_hat),
        fragment(60, 260, frag_shiver),
        fragment(60, 460, frag_reply),
        fragment(60, 660, frag_run),
        fragment(60, 900, frag_warm),
    ]


def control_script_fragments() -> list:
    """control 节点: 剧情节拍总调度."""
    pacing = hat_when_game_starts(
        [
            wait_seconds(0.8),
            # Phase 1 · 冻僵
            broadcast_and_wait("冻僵-1"),
            wait_seconds(0.3),
            broadcast_and_wait("冻僵-2"),
            wait_seconds(0.3),
            broadcast_and_wait("冻僵-3"),
            wait_seconds(0.5),
            # Phase 2 · 出主意 / 回应 / 口令
            broadcast_and_wait("出主意"),
            wait_seconds(0.3),
            broadcast_and_wait("回应"),
            wait_seconds(0.4),
            broadcast_and_wait("口令"),
            # Phase 3 · 跑操 (非阻塞广播 + 等 12s)
            broadcast("跑操开始"),
            wait_seconds(12),
            # Phase 4 · 回温音效
            play_sound("升温"),
            wait_seconds(0.5),
            # 暖和了三段
            broadcast_and_wait("暖和了-1"),
            wait_seconds(0.3),
            broadcast_and_wait("暖和了-2"),
            wait_seconds(0.3),
            broadcast_and_wait("暖和了-3"),
            wait_seconds(0.5),
            play_sound("结算效果-成功"),
            wait_seconds(2),
        ]
    )
    return [fragment(80, 80, pacing)]


# --------------------------------------------------------------------------- #
# Scene node assembly
# --------------------------------------------------------------------------- #


def make_mesh(name: str, position: list[str], assetid: int, visible: bool = False) -> dict:
    """Invisible waypoint marker (or control)."""
    return {
        "type": "MeshPart",
        "id": new_uuid_hex(),
        "props": {
            "Name": name,
            "Visible": visible,
            "Position": position,
            "EulerAngles": ["0", "0", "0"],
            "Scale": "1",
            "AssetId": assetid,
        },
    }


def make_control_node() -> dict:
    node = make_mesh("control", ["1", "0.27", "0"], CONTROL_MESH, visible=False)
    node["children"] = [block_script(new_uuid_hex(), control_script_fragments())]
    return node


def make_character(
    name: str, assetid: int, position: list[str], fragments: list
) -> dict:
    return {
        "type": "Character",
        "id": new_uuid_hex(),
        "props": {
            "Name": name,
            "Visible": True,
            "Position": position,
            "EulerAngles": ["0", "0", "0"],
            "Scale": "0.8",
            "AssetId": assetid,
        },
        "children": [block_script(new_uuid_hex(), fragments)],
    }


def make_sound(name: str, assetid: int) -> dict:
    return {
        "type": "Sound",
        "id": new_uuid_hex(),
        "props": {
            "Name": name,
            "AssetId": assetid,
            "Loop": False,
            "Is3D": False,
        },
    }


def make_music(name: str, assetid: int) -> dict:
    return {
        "type": "Music",
        "id": new_uuid_hex(),
        "props": {
            "Name": name,
            "AssetId": assetid,
            "Loop": False,
            "Is3D": False,
        },
    }


def make_services() -> dict:
    return {
        "type": "Folder",
        "id": new_uuid_hex(),
        "props": {"Name": "services", "EditMode": 0},
        "children": [
            {
                "type": "BlockService",
                "id": new_uuid_hex(),
                "props": {
                    "Name": "Blocks",
                    "EditMode": 0,
                    "Modules": [
                        "motion", "looks", "events", "control", "sound",
                        "sensing", "operators", "variable", "myblocks",
                        "music", "magic", "physics", "stage", "ui", "animation",
                    ],
                },
            },
            {
                "type": "SkyboxService",
                "id": new_uuid_hex(),
                "props": {
                    "Name": "Skybox",
                    "EditMode": 0,
                    "TimeOfDay": "0",
                    "AmbientColor": "#00000000",
                    "SunSize": "0.2",
                    "SunColor": "#00000000",
                    "SunBrightness": "0.5",
                    "MoonSize": "0.2",
                    "MoonColor": "#00000000",
                    "MoonBrightness": "0.2",
                    "StarCount": 3000,
                },
            },
            {
                "type": "CameraService",
                "id": new_uuid_hex(),
                "props": {
                    "Name": "Camera",
                    "EditMode": 0,
                    "Current": "CamEdit",
                },
                "children": [block_script(new_uuid_hex(), [camera_fragment()])],
            },
        ],
    }


def build_scene() -> dict:
    # ★ Character 初始站位 (米): 三人横排,Z=-1/0/+1,X=0 (前排最近镜头)
    # 跑圈路标 P1~P4 (米): P1=左前, P2=左后, P3=右后, P4=右前
    # 循环顺序 P1→P2→P3→P4→P1 (顺时针一圈)
    children = [
        make_services(),
        # Root BlockScript for BGM
        block_script(new_uuid_hex(), [bgm_fragment()]),
        # 三位主角
        make_character(
            "小核桃",
            CHAR_XHT,
            ["0", "0.27", "-1.5"],
            xiaohetao_script_fragments(),
        ),
        make_character(
            "队长",
            CHAR_DZ,
            ["0", "0.27", "0"],
            duizhang_script_fragments(),
        ),
        make_character(
            "展喵",
            CHAR_ZM,
            ["0", "0.27", "1.5"],
            zhanmiao_script_fragments(),
        ),
        # 控制节点
        make_control_node(),
        # 跑圈路标 (不可见)
        make_mesh("P1", ["0",   "0.27", "-2"], CONTROL_MESH),
        make_mesh("P2", ["2.5", "0.27", "-2"], CONTROL_MESH),
        make_mesh("P3", ["2.5", "0.27",  "2"], CONTROL_MESH),
        make_mesh("P4", ["0",   "0.27",  "2"], CONTROL_MESH),
        # 音频节点
        make_music("轻松休闲1", BGM_ASSETID),
        make_sound("凸显", SND_TUXIAN),
        make_sound("升温", SND_SHENGWEN),
        make_sound("结算效果-成功", SND_SUCCESS),
    ]

    return {
        "type": "Scene",
        "id": new_uuid_hex(),
        "props": {
            "Name": "Scene",
            "EditMode": 0,
            "BoundsCenter": ["0", "2.833", "0"],
            "BoundsSize": ["16", "7.67", "12"],
            "AssetId": SCENE_ASSETID,
        },
        "props2": {
            "variable": {"type": "Simple", "value": "0"},
            "#EVENT": {
                "type": "SimpleList",
                "value": [
                    "冻僵-1", "冻僵-2", "冻僵-3",
                    "出主意", "回应", "口令",
                    "跑操开始",
                    "暖和了-1", "暖和了-2", "暖和了-3",
                ],
            },
        },
        "children": children,
    }


def build_ws(project_name: str) -> dict:
    ts = int(time.time())
    return {
        "name": "Project_0",
        "desc": "",
        "icon": "",
        "author": "",
        "created": ts,
        "modified": ts,
        "type": 3,
        "version": 3,
        "stageType": 0,
        "scene": build_scene(),
        "agents": {
            "type": "Folder",
            "id": new_uuid_hex(),
            "props": {"Name": "agents", "EditMode": 0},
        },
        "assets": {
            "type": "Folder",
            "id": new_uuid_hex(),
            "props": {"Name": "assets", "EditMode": 0},
            "children": [
                {
                    "type": "UIPackageObject",
                    "id": new_uuid_hex(),
                    "props": {
                        "Name": "Basic",
                        "EditMode": 0,
                        "AssetId": UI_BASIC,
                    },
                },
                {
                    "type": "UIPackageObject",
                    "id": new_uuid_hex(),
                    "props": {
                        "Name": "Icons",
                        "EditMode": 0,
                        "AssetId": UI_ICONS,
                    },
                },
            ],
        },
        "res": [
            UI_BASIC, UI_ICONS,
            SCENE_ASSETID,
            CONTROL_MESH,
            CHAR_XHT, CHAR_DZ, CHAR_ZM,
            BGM_ASSETID,
            SND_TUXIAN, SND_SHENGWEN, SND_SUCCESS,
        ],
        "showmyblock": True,
        "dialogues": {"DialogueGroups": []},
        "editorScene": {
            "cameras": [
                {
                    "name": "default",
                    "position": ["8", "5", "6"],
                    "rotation": [
                        "-0.2126311",
                        "0.6743797",
                        "-0.2126311",
                        "-0.6743797",
                    ],
                    "fov": 25.0,
                }
            ]
        },
        "projectMode": 2,
    }


def build_solution(
    level_name: str, ws_uuid: str, icon_uuid: str, solution_uid: str
) -> dict:
    return {
        "init": new_uuid_dashed(),
        "name": level_name,
        "author": "",
        "modified": int(time.time()),
        "version": 1,
        "projects": [
            {
                "file": f"pangu3d/universe/develop/{solution_uid}/{ws_uuid}.ws",
                "icon": f"pangu3d/universe/develop/{solution_uid}/{icon_uuid}.png",
                "name": "Project_0",
                "uuid": new_uuid_dashed(),
            }
        ],
        "globals": [
            {
                "obj": {
                    "type": "CameraService",
                    "id": new_uuid_hex(),
                    "props": {
                        "Name": "Camera",
                        "EditMode": 1,
                        "Current": "CamEdit",
                    },
                    "props2": {
                        "GlobalUseProjectConfig": {
                            "type": "Boolean",
                            "value": False,
                        }
                    },
                    "children": [
                        {
                            "type": "BlockScript",
                            "id": new_uuid_hex(),
                            "props": {"Name": "BlockScript", "EditMode": 0},
                        }
                    ],
                }
            }
        ],
    }


# --------------------------------------------------------------------------- #
# Build & package
# --------------------------------------------------------------------------- #

ICON_PNG_1x1 = bytes.fromhex(
    # minimal 1x1 transparent PNG
    "89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C489"
    "0000000D49444154789C6360000000000500010D0A2DB40000000049454E44AE426082"
)


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    level_name = "抗寒跑操-小核桃队长展喵"
    out_dir = repo / "output" / "new"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_zip = out_dir / f"{level_name}.zip"
    if out_zip.exists():
        stamp = time.strftime("%Y%m%d-%H%M%S")
        out_zip = out_dir / f"{level_name}-{stamp}.zip"

    solution_uid = str(int(time.time() * 1_000_000))
    ws_uuid = new_uuid_dashed()
    icon_uuid = new_uuid_dashed()

    ws = build_ws(level_name)
    solution = build_solution(level_name, ws_uuid, icon_uuid, solution_uid)
    export_info = {"solutionUid": solution_uid}

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        (td_path / f"{ws_uuid}.ws").write_text(
            json.dumps(ws, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        (td_path / "solution.json").write_text(
            json.dumps(solution, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        (td_path / "export_info.json").write_text(
            json.dumps(export_info, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        (td_path / f"{icon_uuid}.png").write_bytes(ICON_PNG_1x1)

        with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in td_path.iterdir():
                zf.write(f, arcname=f.name)

    print(f"[OK] wrote: {out_zip}")
    print(f"     size: {out_zip.stat().st_size} bytes")
    print(f"     ws_uuid: {ws_uuid}")


if __name__ == "__main__":
    main()
