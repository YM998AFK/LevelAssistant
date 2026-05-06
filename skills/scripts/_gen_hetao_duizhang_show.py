# -*- coding: utf-8 -*-
"""
生成『小核桃-队长-动作秀』关卡。
基于『修改2』母本，裁剪到只保留必要骨架，替换角色与脚本。
输出: output/new/小核桃队长动作秀.zip
"""
import json
import shutil
import uuid
import zipfile
from pathlib import Path

BASE = Path(r"参考-extracted/修改2")
WS_SRC = BASE / "673eb237-fc27-4f20-9404-294d1f091000.ws"
SOL_SRC = BASE / "solution.json"
EXP_SRC = BASE / "export_info.json"
ICON_SRC = BASE / "7b5bb1fd-0609-47ac-83e5-32e7013d9938.png"

WORK = Path(r"output/new/_xiaohetao_duizhang_workdir")
OUT_ZIP = Path(r"output/new/小核桃队长动作秀.zip")


def new_id(prefix=""):
    return prefix + uuid.uuid4().hex


def v(val):
    """生成 {"type": "var", "val": ...} 参数"""
    return {"type": "var", "val": str(val)}


def block(define, *params_blocks, children=None, next_=None):
    """构造单个 block，参数用 self 占位用 {} 传入 params"""
    section = {}
    if params_blocks:
        section["params"] = list(params_blocks)
    if children is not None:
        section["children"] = children
    b = {"define": define, "sections": [section]}
    if next_:
        b["next"] = next_
    return b


def bval(b):
    """嵌套 block 作为参数槽"""
    return {"type": "block", "val": b}


def when_game_starts(children):
    return {
        "head": {
            "define": "WhenGameStarts",
            "sections": [{"children": children}],
        }
    }


def when_receive_message(msg, children):
    return {
        "head": {
            "define": "WhenReceiveMessage",
            "sections": [
                {"params": [v(msg)], "children": children},
            ],
        }
    }


def fragment(pos_x, pos_y, head_obj):
    return {
        "pos": [str(pos_x), str(pos_y)],
        **head_obj,
    }


# ---------- 加载原始 ws ----------
data = json.loads(WS_SRC.read_text(encoding="utf-8"))

scene = data["scene"]

# ---------- 清理 props2 / #EVENT ----------
# 保留 L0 基础 OJ 变量
KEEP_VARS = [
    "variable",
    "#EVENT",
    "err_msg",
    "*OJ-输入信息",
    "*OJ-执行结果",
    "cmd",
    "state",
    "*OJ-Judge",
    "输入元素",
    "n",
    "cin_cut",
    "输出元素",
    "n1",
    "space-flag",
    "cout_cut",
]
new_props2 = {k: scene["props2"][k] for k in KEEP_VARS if k in scene["props2"]}

# 新的事件列表
EVENTS = [
    "CMD_NewMessage",
    "传递失败",
    "传递成功",
    "初始化",
    "展示关卡效果",
]
new_props2["#EVENT"] = {"type": "SimpleList", "value": EVENTS}

scene["props2"] = new_props2

# ---------- 重建 scene.children ----------
# 保留 services Folder、顶级 BlockScript、control、Effect * 2、Music、Sound * 2
# 删除所有箱子、前置占位、UIView 标签、分割数据、乌拉呼星际服
children = scene["children"]

keep_types = {"Folder"}  # services Folder 全保留
kept = []

for node in children:
    t = node.get("type")
    name = node.get("props", {}).get("Name", "")

    if t == "Folder":
        kept.append(node)
        continue
    if t == "BlockScript" and name == "BlockScript":
        # 顶级判题 BlockScript（传递成功/失败 + BGM）
        kept.append(node)
        continue
    if t == "MeshPart" and name == "control":
        kept.append(node)
        continue
    if t == "Effect" and name in ("样例通过", "样例不通过"):
        kept.append(node)
        continue
    if t == "Music":
        kept.append(node)
        continue
    if t == "Sound" and name in ("结算效果-成功", "结算效果-失败"):
        kept.append(node)
        continue
    # 其它（箱子、前置、UIView、Character 乌拉呼、分割数据、箱子打开音）全删
    if t == "Sound" and name == "箱子打开":
        continue
    if t == "Character":
        continue
    if t == "MeshPart":
        continue
    if t == "UIView":
        continue

scene["children"] = kept

# ---------- 重写 control 脚本 ----------
control_node = next(n for n in scene["children"] if n["type"] == "MeshPart" and n["props"]["Name"] == "control")
# control 作为摄像机锚点，摆在两人重心（2, 0.27, 0），Visible 保持默认 false
# 两人分别站在 (2, 0.27, -2) 与 (2, 0.27, +2)，欧氏距离 4m，远超 NEVER 6/7 的 1m 硬阈值
control_node["props"]["Position"] = ["2", "0.27", "0"]
# control 内的 BlockScript 只保留一个 WhenGameStarts
control_bs = control_node["children"][0]
control_bs["fragments"] = [
    fragment(
        200, 200,
        when_game_starts([
            block("SetVar", v("*OJ-Judge"), v("1")),
            block("ListAdd", v("1"), v("cin_cut")),
            block("If",
                  bval(block("IsEqual",
                             bval(block("Variable", v("*OJ-Judge"))),
                             {},
                             v("1"))),
                  children=[
                      block("BroadcastMessageAndWait", v("展示关卡效果")),
                      block("BroadcastMessageAndWait", v("传递成功")),
                  ]),
        ])
    ),
]

# ---------- 重写 顶级 BlockScript（传递成功/失败/BGM）----------
top_bs = next(n for n in scene["children"] if n["type"] == "BlockScript")
top_bs["fragments"] = [
    # 传递成功
    fragment(200, 200, when_receive_message("传递成功", [
        block("StopAllSound"),
        block("PlaySound", v("结算效果-成功")),
        block("PlayAnimationUntil", v("样例通过")),
        block("WaitSeconds", v("2")),
        block("SetVar", v("*OJ-输入信息"), v("")),
        block("SetVar", v("*OJ-执行结果"), v("")),
        block("EndRun", v("运行结束"), v("")),
        block("StopScript", v("all")),
    ])),
    # 传递失败
    fragment(600, 200, when_receive_message("传递失败", [
        block("StopAllSound"),
        block("PlaySound", v("结算效果-失败")),
        block("PlayAnimationUntil", v("样例不通过")),
        block("WaitSeconds", v("2")),
        block("BroadcastMessageAndWait", v("初始化")),
        block("SetVar", v("*OJ-输入信息"), v("")),
        block("SetVar", v("*OJ-执行结果"), v("")),
        block("StopScript", v("other scripts in sprite")),
        block("EndRun", v("没过关"), bval(block("Variable", v("err_msg")))),
        block("StopScript", v("all")),
    ])),
    # BGM
    fragment(200, 700, when_game_starts([
        block("PlayBGM", v("轻松休闲4"), v("100")),
    ])),
]

# ---------- 摄像机 BlockScript（预设B：俯45° 广角）----------
services_folder = next(n for n in scene["children"] if n["type"] == "Folder")
camera_service = next(n for n in services_folder["children"] if n["type"] == "CameraService")
camera_service["props"]["Current"] = "Camera45"
camera_bs = camera_service["children"][0]  # 第一个 BlockScript
camera_bs["fragments"] = [
    fragment(400, 400,
        when_game_starts([
            block("SetCameraFOV", v("25")),
            block("PointInDirection", {}, v("-90")),
            block("PointInPitch", {}, v("125")),
            block("CameraFollow", v("control"), v("640"), v("0"), v("500")),
        ])),
]

# ---------- 添加小核桃 ----------
xhtt_id = new_id()
xhtt_bs_id = new_id()
xiaohetao = {
    "type": "Character",
    "id": xhtt_id,
    "props": {
        "Name": "小核桃",
        "EditMode": 0,
        "Visible": True,
        "Position": ["2", "0.27", "-2"],
        "EulerAngles": ["0", "90", "0"],
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
        "AssetId": 12156,
        "EmotionAnimations": "[]",
    },
    "children": [
        {
            "type": "BlockScript",
            "id": xhtt_bs_id,
            "props": {"Name": "BlockScript", "EditMode": 0},
            "fragments": [
                fragment(200, 200, when_game_starts([
                    block("GotoPosition3D", v("2"), v("0.27"), v("-2")),
                    block("PointInDirection", {}, v("90")),
                    block("PlayAnimation", v("idle")),
                ])),
                fragment(200, 500, when_receive_message("初始化", [
                    block("GotoPosition3D", v("2"), v("0.27"), v("-2")),
                    block("PointInDirection", {}, v("90")),
                    block("PlayAnimation", v("idle")),
                ])),
                fragment(200, 900, when_receive_message("展示关卡效果", [
                    block("SetSpeedMul", v("3")),
                    block("PlayAnimation", v("run")),
                    block("GlideSecsToPosition3D", v("1"), v("2"), v("0.27"), v("-4")),
                    block("PlayAnimation", v("idle")),
                    block("WaitSeconds", v("0.2")),
                    block("PointInDirection", {}, v("0")),
                    block("PlayAnimationUntil", v("jingya")),
                    block("WaitSeconds", v("0.2")),
                    block("PointInDirection", {}, v("90")),
                    block("PlayAnimation", v("run")),
                    block("GlideSecsToPosition3D", v("0.8"), v("2"), v("0.27"), v("-2")),
                    block("PlayAnimation", v("idle")),
                    block("WaitSeconds", v("0.2")),
                    block("PlayAnimationUntil", v("chuanqi")),
                    block("PlayAnimationUntil", v("dangfeng")),
                    block("PlayAnimationUntil", v("taishou_loop")),
                    block("PlayAnimation", v("idle")),
                ])),
            ],
            "uiState": {"pos": ["500", "500"], "scroll": ["400", "400"], "scale": "1"},
        }
    ],
}

# ---------- 添加队长 ----------
dz_id = new_id()
dz_bs_id = new_id()
duizhang = {
    "type": "Character",
    "id": dz_id,
    "props": {
        "Name": "队长",
        "EditMode": 0,
        "Visible": True,
        "Position": ["2", "0.27", "2"],
        "EulerAngles": ["0", "90", "0"],
        "RotConstraint": 0,
        "ConstraintEulerAngles": ["0", "0", "0"],
        "Scale": "0.6",
        "CastShadow": True,
        "Color": "#FFFFFFFF",
        "Material": "Basic",
        "Transparency": "0",
        "Size": ["1", "2.277619", "1"],
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
        "AssetId": 12146,
        "EmotionAnimations": "[]",
    },
    "children": [
        {
            "type": "BlockScript",
            "id": dz_bs_id,
            "props": {"Name": "BlockScript", "EditMode": 0},
            "fragments": [
                fragment(200, 200, when_game_starts([
                    block("GotoPosition3D", v("2"), v("0.27"), v("2")),
                    block("PointInDirection", {}, v("90")),
                    block("PlayAnimation", v("idle")),
                ])),
                fragment(200, 500, when_receive_message("初始化", [
                    block("GotoPosition3D", v("2"), v("0.27"), v("2")),
                    block("PointInDirection", {}, v("90")),
                    block("PlayAnimation", v("idle")),
                ])),
                fragment(200, 900, when_receive_message("展示关卡效果", [
                    block("SetSpeedMul", v("3")),
                    block("WaitSeconds", v("0.15")),
                    block("PlayAnimation", v("run")),
                    block("GlideSecsToPosition3D", v("1"), v("2"), v("0.27"), v("4")),
                    block("PlayAnimation", v("idle")),
                    block("WaitSeconds", v("0.2")),
                    block("PointInDirection", {}, v("180")),
                    block("PlayAnimationUntil", v("jingya")),
                    block("PlayAnimationUntil", v("taitou_Loop")),
                    block("PointInDirection", {}, v("90")),
                    block("PlayAnimation", v("run")),
                    block("GlideSecsToPosition3D", v("0.8"), v("2"), v("0.27"), v("2")),
                    block("PlayAnimation", v("idle")),
                    block("WaitSeconds", v("0.2")),
                    block("PlayAnimationUntil", v("dangfeng")),
                    block("PlayAnimationUntil", v("shenshoukan_loop")),
                    block("PlayAnimation", v("idle")),
                ])),
            ],
            "uiState": {"pos": ["500", "500"], "scroll": ["400", "400"], "scale": "1"},
        }
    ],
}

# 追加到 scene.children（放在 Effect 之前就好）
scene["children"].extend([xiaohetao, duizhang])

# ---------- 更新 res 列表 ----------
# 去除没用的物件 AssetId，添加两个新角色
old_res = set(data.get("res", []))
# 去掉 17009（箱子）、28012（乌拉呼）、28969（箱子打开音）、27561/27562 若没UI用不到；保留 UI 包，以备扩展
old_res.discard(17009)
old_res.discard(28012)
old_res.discard(28969)
# 加入新角色
old_res.add(12156)
old_res.add(12146)
# 最终去重
data["res"] = sorted(old_res)

# ---------- project 元数据 ----------
# 修改 name/desc
data["name"] = "Project_0"
data["desc"] = "小核桃与队长的动作秀（移动+动作+特效）"

# ---------- 更新 UI 资产（移除无用 UI 包？保留 Basic 供气泡使用，但本关无UI；删除以节省）----------
# 保留 assets 文件夹但清空 UI 包（本关不用 UI）
assets_folder = data.get("assets")
if assets_folder:
    assets_folder["children"] = []
# 移除 UI 包 AssetId
for aid in (27561, 27562):
    if aid in data["res"]:
        data["res"].remove(aid)

# ---------- 写入工作目录 ----------
if WORK.exists():
    shutil.rmtree(WORK)
WORK.mkdir(parents=True, exist_ok=True)

# 复用原 uuid 文件名? 生成新的以免与母本冲突
new_ws_uuid = str(uuid.uuid4())
new_icon_uuid = str(uuid.uuid4())
new_solution_uid = uuid.uuid4().hex
new_project_uuid = str(uuid.uuid4())

ws_name = f"{new_ws_uuid}.ws"
icon_name = f"{new_icon_uuid}.png"

(WORK / ws_name).write_text(
    json.dumps(data, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)

# icon: 沿用母本图
shutil.copy(ICON_SRC, WORK / icon_name)

# solution.json
sol = json.loads(SOL_SRC.read_text(encoding="utf-8"))
sol["name"] = "小核桃队长动作秀"
# init 用新 uid
sol["init"] = new_solution_uid[:8] + "-" + new_solution_uid[8:12] + "-" + new_solution_uid[12:16] + "-" + new_solution_uid[16:20] + "-" + new_solution_uid[20:32]
proj = sol["projects"][0]
proj["name"] = "Project_0"
proj["uuid"] = new_project_uuid
# path 也要对齐
proj_file_new = f"pangu3d/universe/develop/612921974867361800/{ws_name}"
proj_icon_new = f"pangu3d/universe/develop/612921974867361800/{icon_name}"
proj["file"] = proj_file_new
proj["icon"] = proj_icon_new
# globals[0].refs 指向 project uuid
if sol.get("globals"):
    sol["globals"][0]["refs"] = [new_project_uuid]
    # globals[0].obj: 保留母本 CameraService global 配置（不影响）

(WORK / "solution.json").write_text(
    json.dumps(sol, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)

# export_info.json
exp = json.loads(EXP_SRC.read_text(encoding="utf-8"))
exp["solutionUid"] = sol["init"]
(WORK / "export_info.json").write_text(
    json.dumps(exp, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)

# ---------- 打 zip ----------
if OUT_ZIP.exists():
    OUT_ZIP.unlink()

with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for fname in (ws_name, icon_name, "solution.json", "export_info.json"):
        src = WORK / fname
        zf.write(src, arcname=fname)

print(f"[OK] wrote {OUT_ZIP} ({OUT_ZIP.stat().st_size} bytes)")
print(f"     ws: {ws_name}")
