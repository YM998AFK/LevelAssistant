# -*- coding: utf-8 -*-
"""生成【三角对白-小核桃队长展喵】演示关卡 zip。

题材：轻松日常搞笑（"队长的穿鞋壮举"梗，6 幕）
角色：小核桃(12156) + 队长(12146) + 展喵(12153)
站位：三角形 face_inner（后中队长正对摄像机；前左/前右朝内心）
摄像机：预设 A 近景俯 45°（control, 200, 0, 150）
BGM：轻松休闲4 (28985)

本脚本骨架复用自 scripts/_gen_dialog_level.py（桃子魔术版），
保留 battle-tested 的 scene / services / solution / icon PNG 结构，
只改剧情层面的常量（角色、对白、动画、坐标、朝向）。

动画名严格来自 asset_catalog.md 的三位角色动画清单实证，不编造：
  - 小核桃(12156)：idle03, zuozhuan_kanzuobian_loop, yundao_shuijiao
  - 队长(12146):   idle02, taitou_Loop, ditou_idle
  - 展喵(12153):   dianzan, qienuo_xuanyun

生成后必须跑：
  python scripts/verify_blocks.py      output/new/三角对白-小核桃队长展喵.zip
  python scripts/verify_no_new_next.py output/new/三角对白-小核桃队长展喵.zip
"""
from __future__ import annotations
from pathlib import Path
import json, uuid, time, zipfile, tempfile, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT_ZIP = ROOT / "output" / "new" / "三角对白-小核桃队长展喵.zip"

SCENE_ID        = 28746    # 营地物资库内景（室内通用）
CHAR_XHT        = 12156    # 小核桃
CHAR_DUIZHANG   = 12146    # 队长
CHAR_ZHANMIAO   = 12153    # 展喵
EMPTY_MESH      = 10548    # 不可见空挂点
BGM_ID          = 28985    # 轻松休闲4
UI_BASIC        = 27561
UI_ICONS        = 27562
EFFECT_DUIZHANG_ID   = 22238         # 队长升级特效（skill 多次示范的队长专属特效）
EFFECT_DUIZHANG_NAME = "穿鞋壮举光环"  # Effect.Name = PlayAnimation 的动画名

# 站位（Character.props.Position 单位为**米**，实证：14-1 参考包乌拉呼 Y=0.25 脚底）
# v3 全体往 X+ 平移 2m（远离场景深处的机器人控制台/机械臂仪器），避免人仪器重叠
POS_DUIZHANG = ("1", "0.27", "0")   # 后中，正对摄像机
POS_XHT      = ("2", "0.27", "-1")  # 前左
POS_ZHANMIAO = ("2", "0.27", "1")   # 前右

# face_inner 朝向 = 每个角色朝 control (0, 0.27, 0) 的方向
# 公式：angle = degrees(atan2(dX, dZ))，dX/dZ = control - self
#   队长  (-1, 0)  朝中心： dX=+1,  dZ=0   → 90°    （正对摄像机）
#   小核桃(0.5,-1) 朝中心： dX=-0.5,dZ=+1  → -27°   （朝 Z+ 略带 X-，半侧脸）
#   展喵  (0.5, 1) 朝中心： dX=-0.5,dZ=-1  → -153°  （朝 Z- 略带 X-，半侧脸）
DIR_DUIZHANG = "90"
DIR_XHT      = "-27"
DIR_ZHANMIAO = "-153"

CONTROL_POS = ("1.5", "0.27", "0")  # 三角形几何中心，跟 POS_* 一起往 X+ 平移

# 摄像机预设 B 室内俯45广角（dist=640/height=500，presets.md 表2）。
# 预设 A（dist=200/height=150）是"1 主角近景"的参数，对三人三角形完全装不下
# （视场半宽仅 0.44m 而三角 Z 跨度 2m），上一版实测只能看到 1~2 个人。
# 预设 B 的视场半宽约 1.42m，能把 Z=±1、X=-1~+0.5 的三人完整框进画面 + 留白。
CAM = {"fov": "25", "dir": "-90", "pitch": "125",
       "follow_target": "control", "dist": "640", "off_y": "0", "height": "500"}

# ------- 对白脚本（6 幕）-------
# anim 字段 = 该角色骨骼动画（已对 asset_catalog.md 动画清单校验）
# 每幕内部：PlayAnimation（非阻塞） + SaySeconds（阻塞 dur 秒） + PlayAnimation("idle") 收尾
DIALOG = [
    {"msg": "对白-1", "who": "队长",
     "line": "你们猜，今天我干了件什么大事？", "dur": "2.5", "anim": "taitou_Loop"},
    {"msg": "对白-2", "who": "小核桃",
     "line": "又在吹牛了？", "dur": "2", "anim": "zuozhuan_kanzuobian_loop"},
    {"msg": "对白-3", "who": "展喵",
     "line": "说说说！听听听！", "dur": "2", "anim": "dianzan"},
    # 队长在此幕一脸郑重宣布"大事"，头上并行炸开"升级光环"特效——反差萌爆点
    {"msg": "对白-4", "who": "队长",
     "line": "我今天……第一次把鞋子穿对了！", "dur": "3",
     "anim": "idle02", "effect": EFFECT_DUIZHANG_NAME},
]

# 笑点爆发 phase：小核桃晕倒 + 展喵眩晕 并行，然后队长困惑收尾
# 由 control 广播 "笑点爆发"，所有角色同时响应
REACT = {
    "小核桃": {"anim": "yundao_shuijiao", "line": "……", "dur": "2"},
    "展喵":   {"anim": "qienuo_xuanyun", "line": "这也算大事？？", "dur": "2"},
    "队长":   {"anim": "ditou_idle",    "line": "？？？不算吗？", "dur": "2"},
}

CHARS = {
    "小核桃": {"asset": CHAR_XHT,      "pos": POS_XHT,      "dir": DIR_XHT},
    "队长":   {"asset": CHAR_DUIZHANG, "pos": POS_DUIZHANG, "dir": DIR_DUIZHANG},
    "展喵":   {"asset": CHAR_ZHANMIAO, "pos": POS_ZHANMIAO, "dir": DIR_ZHANMIAO},
}

# ================= 工具 =================
def uid() -> str:
    return uuid.uuid4().hex

def uid_dashed() -> str:
    return str(uuid.uuid4())

def var(val) -> dict:
    return {"type": "var", "val": str(val)}

def seq(*nodes) -> list:
    return list(nodes)

def blk_play_anim(name: str) -> dict:
    return {"define": "PlayAnimation", "sections": [{"params": [var(name)]}]}

def blk_say_seconds(line: str, dur: str) -> dict:
    return {"define": "SaySeconds", "sections": [{"params": [var(line), var(dur)]}]}

def blk_wait(sec: str) -> dict:
    return {"define": "WaitSeconds", "sections": [{"params": [var(sec)]}]}

def blk_broadcast_wait(msg: str) -> dict:
    return {"define": "BroadcastMessageAndWait", "sections": [{"params": [var(msg)]}]}

def blk_point_dir(deg: str) -> dict:
    return {"define": "PointInDirection", "sections": [{"params": [{}, var(deg)]}]}

def blk_set_size(v: str) -> dict:
    return {"define": "SetSize", "sections": [{"params": [{}, var(v)]}]}

def blk_goto(x: str, y: str, z: str) -> dict:
    return {"define": "GotoPosition3D",
            "sections": [{"params": [var(x), var(y), var(z)]}]}

# ================= 角色 BlockScript =================
def build_character_script(name: str, cfg: dict) -> dict:
    """每个角色 4~5 个 fragment：
       1) WhenGameStarts：瞬移到站位 + 朝向 + idle（保险：防 props.Position 和脚本不一致）
       2) 对白分片（本角色出演的每条对白一个 WhenReceiveMessage）
       3) 笑点爆发（所有三人都有 WhenReceiveMessage("笑点爆发")）
    """
    fragments = []

    # fragment 1: 初始化（不含 GotoPosition3D）
    # 关键单位坑：Character.props.Position 是**米**，但 GotoPosition3D 参数是**厘米**。
    # v1/v2 在此写了 blk_goto(米值) → 运行时被按厘米解读 → 三人全瞬移到原点 1cm 内
    # → 画面三人重叠成一团（用户截图 image-b687e6a8 实证）。
    # 修复：删除 Goto，让 Character.props.Position 的米制静态值作为唯一定位源。
    # （本关卡无入场跑位需求，Goto 本来就是冗余的。）
    init_body = seq(
        blk_point_dir(cfg["dir"]),
        blk_set_size("100"),
        blk_play_anim("idle"),
    )
    fragments.append({
        "pos": ["60", "60"],
        "head": {"define": "WhenGameStarts",
                 "sections": [{"params": [], "children": init_body}]},
    })

    y = 280
    # fragment 2: 本角色出演的对白
    for d in DIALOG:
        if d["who"] != name:
            continue
        body_nodes = [blk_play_anim(d["anim"])]
        # 若本幕附带特效（如队长对白-4 的"穿鞋壮举光环"），与动作并行触发
        if d.get("effect"):
            body_nodes.append(blk_play_anim(d["effect"]))
        body_nodes.append(blk_say_seconds(d["line"], d["dur"]))
        body_nodes.append(blk_play_anim("idle"))
        body = seq(*body_nodes)
        fragments.append({
            "pos": ["60", str(y)],
            "head": {"define": "WhenReceiveMessage",
                     "sections": [{"params": [var(d["msg"])], "children": body}]},
        })
        y += 220

    # fragment 3: 笑点爆发（三人并行反应）
    r = REACT.get(name)
    if r:
        react_body = seq(
            blk_play_anim(r["anim"]),
            blk_say_seconds(r["line"], r["dur"]),
            blk_play_anim("idle"),
        )
        fragments.append({
            "pos": ["60", str(y)],
            "head": {"define": "WhenReceiveMessage",
                     "sections": [{"params": [var("笑点爆发")], "children": react_body}]},
        })
        y += 220

    return {
        "type": "BlockScript",
        "id": uid(),
        "props": {"Name": "BlockScript", "EditMode": 0},
        "fragments": fragments,
    }

def build_effect_duizhang_node() -> dict:
    """队长 Character 子节点：升级特效。
    Name = "穿鞋壮举光环" → PlayAnimation("穿鞋壮举光环") 即可触发。
    props 严格对齐参考包（skill ⚠️规则）：只保留 Name/EditMode/AssetId/Loop/FullScreenBeforeUI，
    绝不设 Visible=false（设了就永远不播）。"""
    return {
        "type": "Effect",
        "id": uid(),
        "props": {
            "Name": EFFECT_DUIZHANG_NAME,
            "EditMode": 0,
            "AssetId": EFFECT_DUIZHANG_ID,
            "Loop": False,
            "FullScreenBeforeUI": True,
        },
    }

def build_character(name: str, cfg: dict) -> dict:
    children = [build_character_script(name, cfg)]
    if name == "队长":
        children.append(build_effect_duizhang_node())
    return {
        "type": "Character",
        "id": uid(),
        "props": {
            "Name": name,
            "Visible": True,
            "Position": list(cfg["pos"]),
            "EulerAngles": ["0", "0", "0"],
            "Scale": "1",
            "AssetId": cfg["asset"],
        },
        "children": children,
    }

# ================= control（编排者 / 摄像机锚点）=================
def build_control_script() -> dict:
    """control 作为总导演，按顺序串对白，最后触发笑点爆发。
    开场 0.8s 给摄像机/BGM就位，然后每幕 BroadcastMessageAndWait 串行。
    对白之间 0.3s 小停顿，第 4 幕结束后 0.6s 屏息，然后并行爆发。"""
    body = [blk_wait("0.8")]
    for d in DIALOG:
        body.append(blk_broadcast_wait(d["msg"]))
        body.append(blk_wait("0.3"))
    body.append(blk_wait("0.6"))
    body.append(blk_broadcast_wait("笑点爆发"))
    body.append(blk_wait("1"))

    fragment = {
        "pos": ["80", "80"],
        "head": {"define": "WhenGameStarts",
                 "sections": [{"params": [], "children": body}]},
    }
    return {
        "type": "BlockScript",
        "id": uid(),
        "props": {"Name": "BlockScript", "EditMode": 0},
        "fragments": [fragment],
    }

def build_control_node() -> dict:
    return {
        "type": "MeshPart",
        "id": uid(),
        "props": {
            "Name": "control",
            "Visible": False,
            "Position": list(CONTROL_POS),
            "EulerAngles": ["0", "0", "0"],
            "Scale": "1",
            "AssetId": EMPTY_MESH,
        },
        "children": [build_control_script()],
    }

# ================= Scene-level BGM =================
def build_scene_bgm_script() -> dict:
    body = [{"define": "PlayBGM",
             "sections": [{"params": [var("轻松休闲4"), var("100")]}]}]
    fragment = {
        "pos": ["80", "80"],
        "head": {"define": "WhenGameStarts",
                 "sections": [{"params": [], "children": body}]},
    }
    return {
        "type": "BlockScript",
        "id": uid(),
        "props": {"Name": "BlockScript", "EditMode": 0},
        "fragments": [fragment],
    }

# ================= Camera 脚本 =================
def build_camera_script() -> dict:
    body = seq(
        {"define": "SetCameraFOV",
         "sections": [{"params": [var(CAM["fov"])]}]},
        {"define": "PointInDirection",
         "sections": [{"params": [{}, var(CAM["dir"])]}]},
        {"define": "PointInPitch",
         "sections": [{"params": [{}, var(CAM["pitch"])]}]},
        {"define": "CameraFollow",
         "sections": [{"params": [
             var(CAM["follow_target"]),
             var(CAM["dist"]),
             var(CAM["off_y"]),
             var(CAM["height"]),
         ]}]},
    )
    fragment = {
        "pos": ["80", "80"],
        "head": {"define": "WhenGameStarts",
                 "sections": [{"params": [], "children": body}]},
    }
    return {
        "type": "BlockScript",
        "id": uid(),
        "props": {"Name": "BlockScript", "EditMode": 0},
        "fragments": [fragment],
    }

# ================= services =================
def build_services() -> dict:
    cam_service = {
        "type": "CameraService",
        "id": uid(),
        "props": {"Name": "Camera", "EditMode": 0, "Current": "CamEdit"},
        "children": [build_camera_script()],
    }
    sky = {
        "type": "SkyboxService",
        "id": uid(),
        "props": {
            "Name": "Skybox", "EditMode": 0,
            "TimeOfDay": "0",
            "AmbientColor": "#00000000",
            "SunSize": "0.2", "SunColor": "#00000000", "SunBrightness": "0.5",
            "MoonSize": "0.2", "MoonColor": "#00000000", "MoonBrightness": "0.2",
            "StarCount": 3000,
        },
    }
    blocks = {
        "type": "BlockService",
        "id": uid(),
        "props": {
            "Name": "Blocks", "EditMode": 0,
            "Modules": ["motion","looks","events","control","sound","sensing",
                        "operators","variable","myblocks","music","magic",
                        "physics","stage","ui","animation"],
        },
    }
    return {
        "type": "Folder",
        "id": uid(),
        "props": {"Name": "services", "EditMode": 0},
        "children": [blocks, sky, cam_service],
    }

def build_bgm_node() -> dict:
    return {
        "type": "Music",
        "id": uid(),
        "props": {
            "Name": "轻松休闲4",
            "AssetId": BGM_ID,
            "Loop": False,
            "Is3D": False,
        },
    }

# ================= Scene =================
def build_scene() -> dict:
    children = [build_services(), build_scene_bgm_script()]
    for name, cfg in CHARS.items():
        children.append(build_character(name, cfg))
    children.append(build_control_node())
    children.append(build_bgm_node())

    return {
        "type": "Scene",
        "id": uid(),
        "props": {
            "Name": "Scene",
            "EditMode": 0,
            "BoundsCenter": ["0", "2.833", "0"],
            "BoundsSize": ["16", "7.67", "12"],
            "AssetId": SCENE_ID,
        },
        "props2": {
            "variable": {"type": "Simple", "value": "0"},
            "#EVENT": {
                "type": "SimpleList",
                "value": [d["msg"] for d in DIALOG] + ["笑点爆发"],
            },
        },
        "children": children,
    }

# ================= .ws 顶层 =================
def build_ws() -> dict:
    now = int(time.time())
    scene = build_scene()
    return {
        "name": "Project_0",
        "desc": "",
        "icon": "",
        "author": "",
        "created": now,
        "modified": now,
        "type": 3,
        "version": 3,
        "stageType": 0,
        "scene": scene,
        "agents": {
            "type": "Folder",
            "id": uid(),
            "props": {"Name": "agents", "EditMode": 0},
        },
        "assets": {
            "type": "Folder",
            "id": uid(),
            "props": {"Name": "assets", "EditMode": 0},
            "children": [
                {"type": "UIPackageObject", "id": uid(),
                 "props": {"Name": "Basic", "EditMode": 0, "AssetId": UI_BASIC}},
                {"type": "UIPackageObject", "id": uid(),
                 "props": {"Name": "Icons", "EditMode": 0, "AssetId": UI_ICONS}},
            ],
        },
        "res": [UI_BASIC, UI_ICONS, SCENE_ID, EMPTY_MESH,
                CHAR_XHT, CHAR_DUIZHANG, CHAR_ZHANMIAO, BGM_ID,
                EFFECT_DUIZHANG_ID],
        "showmyblock": True,
        "dialogues": {"DialogueGroups": []},
        "editorScene": {
            "cameras": [{
                "name": "default",
                "position": ["8", "5", "6"],
                "rotation": ["-0.2126311", "0.6743797", "-0.2126311", "-0.6743797"],
                "fov": 25.0,
            }],
        },
        "projectMode": 2,
    }

# ================= solution / export_info =================
# 这三个 UUID 是 pangu3d 引擎识别的"初始化模板/全局 CameraService 分镜库"锚点。
# 缺了它们，编辑器打开工程会弹"创建分镜"引导 UI 且拒绝渲染 object。不能随便换。
INIT_UUID_TEMPLATE = "8b4c0a4d-4f98-4665-8b1e-b018f6a82c91"
GLOBAL_CAMERA_ID   = "a8af06cfce3a4e6e910fdca8cd45cc09"
GLOBAL_EMPTY_BS_ID = "c55d1b06be574374878514105bb57f35"

MYBLOCK_OUTDOOR_DEFINE = "6377b110e62644a28570625c30d5c6ad/myblockdefine"
MYBLOCK_INDOOR_DEFINE  = "09c264dd7fab4e08b2968afd8408d113/myblockdefine"

def _cam_myblock_body(follow_target: str, dist: str, off_y: str, height: str) -> list:
    return [
        {"define": "SetCameraFOV",
         "sections": [{"params": [var("25")]}]},
        {"define": "PointInDirection",
         "sections": [{"params": [{}, var("-90")]}]},
        {"define": "PointInPitch",
         "sections": [{"params": [{}, var("125")]}]},
        {"define": "CameraFollow",
         "sections": [{"params": [
             var(follow_target), var(dist), var(off_y), var(height)
         ]}]},
    ]

def build_solution(ws_uuid: str, solution_uid: str, icon_uuid: str) -> dict:
    project_uuid = uid_dashed()
    cam_bs1_id = uid()
    myblock_outdoor = {
        "name": MYBLOCK_OUTDOOR_DEFINE,
        "displayName": "外景侧45跟随",
        "wrapBlockName": "",
        "fragment": {
            "pos": ["615.9999", "216"],
            "head": {
                "define": MYBLOCK_OUTDOOR_DEFINE,
                "sections": [{"children": _cam_myblock_body("队长", "640", "0", "500")}],
            },
        },
    }
    myblock_indoor = {
        "name": MYBLOCK_INDOOR_DEFINE,
        "displayName": "室内侧45跟随",
        "wrapBlockName": "",
        "fragment": {
            "pos": ["1304", "208"],
            "head": {
                "define": MYBLOCK_INDOOR_DEFINE,
                "sections": [{"children": _cam_myblock_body("队长", "200", "0", "150")}],
            },
        },
    }

    return {
        "init": INIT_UUID_TEMPLATE,
        "name": "三角对白-小核桃队长展喵",
        "author": "",
        "modified": int(time.time()),
        "version": 1,
        "projects": [{
            "file":  f"pangu3d/universe/develop/{solution_uid}/{ws_uuid}.ws",
            "icon":  f"pangu3d/universe/develop/{solution_uid}/{icon_uuid}.png",
            "name":  "Project_0",
            "uuid":  project_uuid,
        }],
        "globals": [{
            "obj": {
                "type": "CameraService",
                "id": GLOBAL_CAMERA_ID,
                "props": {"Name": "Camera", "EditMode": 1, "Current": "CamEdit"},
                "props2": {
                    "GlobalUseProjectConfig": {"type": "Boolean", "value": False},
                },
                "children": [
                    {
                        "type": "BlockScript",
                        "id": cam_bs1_id,
                        "props": {"Name": "BlockScript", "EditMode": 0},
                        "myblocks": [myblock_outdoor, myblock_indoor],
                        "uiState": {
                            "pos": ["775", "739"],
                            "scroll": ["775.9", "739.8"],
                            "scale": "1",
                        },
                    },
                    {
                        "type": "BlockScript",
                        "id": GLOBAL_EMPTY_BS_ID,
                        "props": {"Name": "BlockScript", "EditMode": 0},
                        "uiState": {
                            "pos": ["0", "0"],
                            "scroll": ["0", "0"],
                            "scale": "1",
                        },
                    },
                ],
            },
        }],
    }

def build_export_info(solution_uid: str) -> dict:
    return {"solutionUid": solution_uid}

# 最小合法占位 PNG (1x1 transparent)。引擎校验 icon 文件存在。
MINIMAL_PNG_BYTES = bytes.fromhex(
    "89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C4890000000A"
    "49444154789C63000100000500010D0A2DB40000000049454E44AE426082"
)

# ================= 主流程 =================
def main():
    ws_uuid = uid_dashed()
    icon_uuid = uid_dashed()
    solution_uid = str(int(time.time() * 1000)) + "000"

    ws_obj = build_ws()
    sol_obj = build_solution(ws_uuid, solution_uid, icon_uuid)
    info_obj = build_export_info(solution_uid)

    OUT_ZIP.parent.mkdir(parents=True, exist_ok=True)
    if OUT_ZIP.exists():
        ts = time.strftime("%Y%m%d-%H%M%S")
        backup = OUT_ZIP.with_name(OUT_ZIP.stem + "-" + ts + ".zip")
        OUT_ZIP.rename(backup)
        print(f"[BACKUP] 旧 zip -> {backup.name}")

    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        (tdp / f"{ws_uuid}.ws").write_text(
            json.dumps(ws_obj, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        (tdp / "solution.json").write_text(
            json.dumps(sol_obj, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        (tdp / "export_info.json").write_text(
            json.dumps(info_obj, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        (tdp / f"{icon_uuid}.png").write_bytes(MINIMAL_PNG_BYTES)
        with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(tdp.iterdir()):
                zf.write(p, p.name)

    sz = OUT_ZIP.stat().st_size
    print(f"[OK] 生成: {OUT_ZIP}")
    print(f"     大小: {sz} bytes")
    print(f"     ws_uuid: {ws_uuid}")
    print(f"     icon_uuid: {icon_uuid}")
    print(f"     solution_uid: {solution_uid}")

if __name__ == "__main__":
    main()
