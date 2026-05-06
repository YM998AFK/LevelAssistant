# -*- coding: utf-8 -*-
"""生成【三角对白-小核桃队长桃子】演示关卡 zip（升级版：入场/动作/靠近/魔术特效）。

关卡形态：最小演示关卡（不挂 OJ 骨架）
- 场景：室内通用 (AssetId 28746)
- 三角站位：小核桃 (近景偏右)、队长 (远处左下)、桃子 (远处左上)
- 摄像机：俯 45° 近景（预设 A）
- 演出线：
    0. 三人从场景 X- 深处分别 RunToTargetAndWait 到各自的三角位路标（入场）
    1. 三人分别播放"登场落位"动作 → 互相看中心（写实对视）
    2. 依次对白 1~7；每条对白配各角色专属性格动作
    3. 对白-4 之后：队长 + 桃子 并行 GlideSecsToPosition3D 向中心轻轻靠拢
    4. 对白-7 之后：广播"魔术爆发" → 小核桃身上播 Effect 12566
       "小核桃充能身体特效"，并伸出双手；队长+桃子同步惊叹
    5. 收尾：三人回 idle，BGM 继续

生成规则严格对齐 level-common/SKILL.md 的代码块参数槽规则、
Effect 挂载机制、移动使用 RunToTargetAndWait / GlideSecsToPosition3D。
生成后需跑 scripts/verify_blocks.py 硬校验。
"""
from __future__ import annotations
from pathlib import Path
import json, uuid, time, zipfile, tempfile, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT_ZIP = ROOT / "output" / "new" / "三角对白-小核桃队长桃子.zip"

# ------- 常量（AssetId）-------
SCENE_ID        = 28746    # 室内通用场景
CHAR_XHT        = 12156    # 小核桃
CHAR_DUIZHANG   = 12146    # 队长
CHAR_TAOZI      = 16342    # 桃子
EMPTY_MESH      = 10548    # 不可见空挂点
BGM_ID          = 28985    # 轻松休闲4
EFFECT_CHARGE   = 12566    # 小核桃充能身体特效
UI_BASIC        = 27561
UI_ICONS        = 27562
EFFECT_NAME     = "充能特效"  # 挂在小核桃 Character 下的 Effect.Name（即动画名）

# ------- 站位（三角终点位 / 入场起点 / 靠近后位 / 路标）-------
# 终点位（Y=0.27 主角落地高度）
POS_XHT_END      = ("2.5", "0.27", "0")
POS_DUIZHANG_END = ("0.5", "0.27", "-1.8")
POS_TAOZI_END    = ("0.5", "0.27", "1.8")
# 入场起点：都在 X-（场景深处），Z 与终点同；摄像机在 X+ 俯视 X-，三人从画面里侧跑出
POS_XHT_START      = ("-3", "0.27", "0")
POS_DUIZHANG_START = ("-3", "0.27", "-1.8")
POS_TAOZI_START    = ("-3", "0.27", "1.8")
# 对白-4 后"靠拢"位（队长和桃子都往中间 X 挪一步，Z 绝对值变小）
POS_DUIZHANG_NEAR = ("0.8", "0.27", "-1.2")
POS_TAOZI_NEAR    = ("0.8", "0.27", "1.2")

# 路标节点（隐形 MeshPart AssetId=10548 Visible=false），Position=终点位
WAYPOINTS = [
    ("站位-小核桃", POS_XHT_END),
    ("站位-队长",   POS_DUIZHANG_END),
    ("站位-桃子",   POS_TAOZI_END),
]

# ------- 对白脚本 -------
# 每条对白的 anim 字段 = 角色自带骨骼动画（非 loop 的动作型，如 jingya/beixi；
# 或 loop 型的展示姿势，如 kaixin_idle/shenchushuangshou_loop）；
# 对白播完统一 PlayAnimation("idle") 收尾
DIALOG = [
    {"msg": "对白-1", "who": "小核桃", "line": "队长，桃子姐！你们快来，我发现了个好玩的东西！", "dur": "3", "anim": "jingya"},
    {"msg": "对白-2", "who": "队长",   "line": "又发现啥了？上回你说的\"宝藏\"最后是块普通石头。",     "dur": "4", "anim": "beixi"},
    {"msg": "对白-3", "who": "桃子",   "line": "别打击他嘛队长～我看小核桃眼睛都亮了。",              "dur": "3", "anim": "kaixin_idle"},
    {"msg": "对白-4", "who": "小核桃", "line": "这次是真的！你们俩走得近点，我给你们看……",          "dur": "3", "anim": "shenchushuangshou_loop"},
    {"msg": "对白-5", "who": "队长",   "line": "行吧行吧，我站这儿了。",                              "dur": "2", "anim": "idle02"},
    {"msg": "对白-6", "who": "桃子",   "line": "小核桃，只要不是毛毛虫我都能接受。",                  "dur": "3", "anim": "wanyao_idle"},
    {"msg": "对白-7", "who": "小核桃", "line": "哈哈，是——我新学会的一个魔术！准备好了吗？",        "dur": "3", "anim": "taishou"},
]

# 魔术爆发阶段每个角色的反应（都由 "魔术爆发" 广播触发，所有角色并行）
MAGIC_REACT = {
    # 小核桃：并行播特效 + 伸手动作 + 喊口号
    "小核桃": {"effect": EFFECT_NAME, "anim": "shenchushuangshou_loop",
               "line": "见证奇迹的时刻——！", "dur": "3"},
    "队长":   {"effect": None, "anim": "jingya",
               "line": "哇——这……这真的？！", "dur": "3"},
    "桃子":   {"effect": None, "anim": "kaixin_idle",
               "line": "好厉害呀小核桃！", "dur": "3"},
}

# 角色初始配置：入场前朝 X+ 跑动；终点朝向各自写实方向
CHARS = {
    "小核桃": {"asset": CHAR_XHT,      "start": POS_XHT_START,
                "end": POS_XHT_END,      "end_dir": "-90", "wp": "站位-小核桃"},
    "队长":   {"asset": CHAR_DUIZHANG, "start": POS_DUIZHANG_START,
                "end": POS_DUIZHANG_END, "end_dir": "45",  "wp": "站位-队长"},
    "桃子":   {"asset": CHAR_TAOZI,    "start": POS_TAOZI_START,
                "end": POS_TAOZI_END,   "end_dir": "135", "wp": "站位-桃子"},
}

CONTROL_POS = ("1.5", "0.27", "0")  # 摄像机跟随的中心锚点（和场景原点差一点点，好构图）

# 摄像机预设 A：近景俯 45°
CAM = {"fov": "25", "dir": "-90", "pitch": "125",
       "follow_target": "control", "dist": "400", "off_y": "0", "height": "150"}

# ------- 工具 -------
def uid() -> str:
    return uuid.uuid4().hex

def uid_dashed() -> str:
    return str(uuid.uuid4())

def var(val) -> dict:
    return {"type": "var", "val": str(val)}

def seq(*nodes) -> list:
    """顺序积木数组，放在 sections[0].children（参考包实证：运行时只认 children，不认 next）。"""
    return list(nodes)

# ------- 常用积木 -------
def blk_play_anim(name: str) -> dict:
    return {"define": "PlayAnimation", "sections": [{"params": [var(name)]}]}

def blk_say_seconds(line: str, dur: str) -> dict:
    return {"define": "SaySeconds", "sections": [{"params": [var(line), var(dur)]}]}

def blk_wait(sec: str) -> dict:
    return {"define": "WaitSeconds", "sections": [{"params": [var(sec)]}]}

def blk_broadcast_wait(msg: str) -> dict:
    return {"define": "BroadcastMessageAndWait", "sections": [{"params": [var(msg)]}]}

def blk_broadcast(msg: str) -> dict:
    return {"define": "BroadcastMessage", "sections": [{"params": [var(msg)]}]}

def blk_point_dir(deg: str) -> dict:
    return {"define": "PointInDirection", "sections": [{"params": [{}, var(deg)]}]}

def blk_set_size(v: str) -> dict:
    return {"define": "SetSize", "sections": [{"params": [{}, var(v)]}]}

def blk_set_speed(mul: str) -> dict:
    return {"define": "SetSpeedMul", "sections": [{"params": [var(mul)]}]}

def blk_run_to(target: str) -> dict:
    return {"define": "RunToTargetAndWait", "sections": [{"params": [var(target)]}]}

def blk_glide(t: str, x: str, y: str, z: str) -> dict:
    return {"define": "GlideSecsToPosition3D",
            "sections": [{"params": [var(t), var(x), var(y), var(z)]}]}

def blk_goto(x: str, y: str, z: str) -> dict:
    # GotoPosition3D: strict 3 参数 [x, y, z]，无 self 占位。瞬移无动画。
    return {"define": "GotoPosition3D",
            "sections": [{"params": [var(x), var(y), var(z)]}]}

# ------- 角色脚本 -------
def build_character_script(name: str, cfg: dict) -> dict:
    """每个角色的 BlockScript：含 5 个 fragment
       1) WhenGameStarts：初始朝 X+ (90) + SetSize + idle
       2) WhenReceiveMessage("登场")：设速 + 跑向路标 + 调整终点朝向 + idle
       3) WhenReceiveMessage("靠近")：仅队长/桃子有，GlideSecsToPosition3D 轻推一步
       4) N 条 WhenReceiveMessage("对白-X")：动作 + SaySeconds + 回 idle
       5) WhenReceiveMessage("魔术爆发")：小核桃播特效 + 动作 + 喊口号；
          队长/桃子播惊叹动作 + 呐喊
    """
    fragments = []

    # ---- fragment 1: WhenGameStarts 初始化 ----
    # 关键：Character.props.Position 固定为终点位（编辑器预览一眼可见三角站位）。
    # 运行时在此 GotoPosition3D 瞬移到入场起点 X=-3（无动画），
    # 然后等 control 广播"登场"时 RunToTargetAndWait 跑回终点。
    start = cfg["start"]
    init_body = seq(
        blk_goto(start[0], start[1], start[2]),
        blk_point_dir("90"),     # 瞬移后朝 X+（面向镜头方向）跑出
        blk_set_size("100"),
        blk_play_anim("idle"),
    )
    fragments.append({
        "pos": ["60", "60"],
        "head": {"define": "WhenGameStarts",
                 "sections": [{"params": [], "children": init_body}]},
    })

    # ---- fragment 2: WhenReceiveMessage("登场") 入场跑位 ----
    enter_body = seq(
        blk_set_speed("3"),
        blk_run_to(cfg["wp"]),
        blk_point_dir(cfg["end_dir"]),
        blk_play_anim("idle"),
    )
    fragments.append({
        "pos": ["60", "240"],
        "head": {"define": "WhenReceiveMessage",
                 "sections": [{"params": [var("登场")], "children": enter_body}]},
    })

    y = 420
    # ---- fragment 3: WhenReceiveMessage("靠近") 仅队长/桃子 ----
    if name == "队长":
        near_body = seq(
            blk_play_anim("walk"),
            blk_glide("1.5", POS_DUIZHANG_NEAR[0], POS_DUIZHANG_NEAR[1], POS_DUIZHANG_NEAR[2]),
            blk_point_dir(cfg["end_dir"]),
            blk_play_anim("idle"),
        )
        fragments.append({
            "pos": ["60", str(y)],
            "head": {"define": "WhenReceiveMessage",
                     "sections": [{"params": [var("靠近")], "children": near_body}]},
        })
        y += 220
    elif name == "桃子":
        near_body = seq(
            blk_play_anim("walk"),
            blk_glide("1.5", POS_TAOZI_NEAR[0], POS_TAOZI_NEAR[1], POS_TAOZI_NEAR[2]),
            blk_point_dir(cfg["end_dir"]),
            blk_play_anim("idle"),
        )
        fragments.append({
            "pos": ["60", str(y)],
            "head": {"define": "WhenReceiveMessage",
                     "sections": [{"params": [var("靠近")], "children": near_body}]},
        })
        y += 220

    # ---- fragment 4: 对白片段 ----
    for d in DIALOG:
        if d["who"] != name:
            continue
        body = seq(
            blk_play_anim(d["anim"]),            # 非阻塞：动作立即开始
            blk_say_seconds(d["line"], d["dur"]),  # 阻塞 dur 秒
            blk_play_anim("idle"),                # 对白结束回到 idle
        )
        fragments.append({
            "pos": ["60", str(y)],
            "head": {"define": "WhenReceiveMessage",
                     "sections": [{"params": [var(d["msg"])], "children": body}]},
        })
        y += 200

    # ---- fragment 5: 魔术爆发 ----
    react = MAGIC_REACT.get(name)
    if react:
        magic_body = []
        if react.get("effect"):
            magic_body.append(blk_play_anim(react["effect"]))  # 非阻塞：先点燃特效
        magic_body.append(blk_play_anim(react["anim"]))         # 非阻塞：同时摆动作
        magic_body.append(blk_say_seconds(react["line"], react["dur"]))
        magic_body.append(blk_play_anim("idle"))
        fragments.append({
            "pos": ["60", str(y)],
            "head": {"define": "WhenReceiveMessage",
                     "sections": [{"params": [var("魔术爆发")], "children": magic_body}]},
        })
        y += 220

    return {
        "type": "BlockScript",
        "id": uid(),
        "props": {"Name": "BlockScript", "EditMode": 0},
        "fragments": fragments,
    }

def build_effect_charge_node() -> dict:
    """挂在小核桃 Character 下的特效子节点，Name="充能特效"，
    PlayAnimation("充能特效") 即可触发（Effect.Name 被动态注册为动画名）。"""
    return {
        "type": "Effect",
        "id": uid(),
        "props": {
            "Name": EFFECT_NAME,
            "EditMode": 0,
            "AssetId": EFFECT_CHARGE,
            "Loop": False,
            "FullScreenBeforeUI": True,
        },
    }

def build_character(name: str, cfg: dict) -> dict:
    children = [build_character_script(name, cfg)]
    if name == "小核桃":
        children.append(build_effect_charge_node())
    return {
        "type": "Character",
        "id": uid(),
        "props": {
            "Name": name,
            "Visible": True,
            # 编辑器预览位 = 终点三角位（保证打开就能看见三人排好）；
            # 运行时脚本会先 GotoPosition3D 瞬移到入场起点再 RunToTargetAndWait 跑回。
            "Position": list(cfg["end"]),
            "EulerAngles": ["0", "0", "0"],
            "Scale": "1",
            "AssetId": cfg["asset"],
        },
        "children": children,
    }

# ------- 路标节点 -------
def build_waypoint(name: str, pos) -> dict:
    return {
        "type": "MeshPart",
        "id": uid(),
        "props": {
            "Name": name,
            "Visible": False,
            "Position": list(pos),
            "EulerAngles": ["0", "0", "0"],
            "Scale": "1",
            "AssetId": EMPTY_MESH,
        },
    }

# ------- control 脚本 -------
def build_control_script() -> dict:
    body = [blk_wait("0.8")]
    # 入场
    body.append(blk_broadcast_wait("登场"))
    body.append(blk_wait("0.4"))
    # 对白 1~4
    for d in DIALOG[:4]:
        body.append(blk_broadcast_wait(d["msg"]))
        body.append(blk_wait("0.3"))
    # 对白-4 之后靠拢
    body.append(blk_broadcast_wait("靠近"))
    body.append(blk_wait("0.2"))
    # 对白 5~7（5-6, 6-7 之间 0.3 拍；7 结束后留一个更戏剧的屏息 0.6，
    # 让"准备好了吗？"的余音撑住，然后特效爆开）
    for i, d in enumerate(DIALOG[4:]):
        body.append(blk_broadcast_wait(d["msg"]))
        if i < 2:
            body.append(blk_wait("0.3"))
    body.append(blk_wait("0.6"))
    # 魔术爆发
    body.append(blk_broadcast_wait("魔术爆发"))
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

# ------- Scene-level BlockScript：BGM ----
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

# ------- Camera 脚本 -------
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

# ------- services 文件夹 -------
def build_services() -> dict:
    # 规则（SKILL level-common）：新关卡统一用 "CamEdit" 作 Current，
    # 编辑器打开是编辑模式，运行时由 BlockScript 接管摄像机。
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

# ------- BGM Music 节点 -------
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

# ------- Scene -------
def build_scene() -> dict:
    children = [build_services(), build_scene_bgm_script()]
    # 路标（隐形 MeshPart）
    for wp_name, wp_pos in WAYPOINTS:
        children.append(build_waypoint(wp_name, wp_pos))
    # 三个角色
    for name, cfg in CHARS.items():
        children.append(build_character(name, cfg))
    # control 节点
    children.append(build_control_node())
    # BGM
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
                "value": [d["msg"] for d in DIALOG] + ["登场", "靠近", "魔术爆发"],
            },
        },
        "children": children,
    }

# ------- .ws 顶层 -------
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
                CHAR_XHT, CHAR_DUIZHANG, CHAR_TAOZI, BGM_ID, EFFECT_CHARGE],
        "showmyblock": True,
        "dialogues": {"DialogueGroups": []},
        # editorScene.cameras 必须至少有 1 项 default 视角，否则编辑器弹"创建分镜"
        # 且整个 3D 预览不渲染。实证：所有能跑的参考包（14-3-6 / 动作特效包 / 测试 / ym）
        # cameras 数组都非空。rotation 四元数格式为 [x,y,z,w]。
        # 视角结构抄自"动作特效包"（已 battle-tested 的有效四元数），
        # position 适配我的小场景坐标（原参考包坐标是 55~73 量级）。
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

# ------- solution.json / export_info.json -------
# 下列 UUID 均来自能跑的参考包 (input/15-2 关卡3.zip 和 input/低16-2 练习2.zip)。
# 它们不是随机生成的，而是 pangu3d 引擎识别的"初始化模板/全局 CameraService
# 分镜库"锚点。缺了这些 UUID 或缺了下面 myblocks 里的两个标准分镜，
# 编辑器打开工程时会弹"创建分镜"引导 UI，并拒绝渲染任何 object。
INIT_UUID_TEMPLATE = "8b4c0a4d-4f98-4665-8b1e-b018f6a82c91"
GLOBAL_CAMERA_ID   = "a8af06cfce3a4e6e910fdca8cd45cc09"
GLOBAL_EMPTY_BS_ID = "c55d1b06be574374878514105bb57f35"

# "外景侧45跟随" / "室内侧45跟随" 是引擎认定的**标准摄像机分镜 myblock**，
# 这两个 define 名是 pangu3d 注册表里的固定 UUID，不能换。
MYBLOCK_OUTDOOR_DEFINE = "6377b110e62644a28570625c30d5c6ad/myblockdefine"
MYBLOCK_INDOOR_DEFINE  = "09c264dd7fab4e08b2968afd8408d113/myblockdefine"

def _cam_myblock_body(follow_target: str, dist: str, off_y: str, height: str) -> list:
    """分镜 myblock 的标准 body：FOV → 方向 → 俯仰 → 跟随目标（Camera45 Preset A 参数）。"""
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
    # 两个内嵌 BlockScript id：第一个随机、第二个必须固定模板 id
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
        "name": "三角对白-小核桃队长桃子",
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

# 最小合法占位 PNG (1x1 transparent)。引擎校验 icon 文件存在 + 是合法 PNG；
# 参考包里 icon 是关卡缩略图 (60~70 KB)，这里用最小占位避免工程被判定"未初始化"。
MINIMAL_PNG_BYTES = bytes.fromhex(
    "89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C4890000000A"
    "49444154789C63000100000500010D0A2DB40000000049454E44AE426082"
)

# ------- 主流程 -------
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
        # icon PNG —— 缺了引擎会认为工程未初始化，弹"创建分镜"引导 UI
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
