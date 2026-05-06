# -*- coding: utf-8 -*-
"""
生成关卡："5级角色升级"（筛选5的倍数 for 循环）
基于"修改2"参考包的简化模式骨架，替换角色、场景、UI 和 control 逻辑。
"""
import json
import os
import sys
import uuid
import time
import shutil
import copy
import zipfile
import tempfile

sys.stdout.reconfigure(encoding='utf-8')

# ==================== 配置 ====================

LEVEL_NAME = "5级角色升级-教师端"
SCENE_ASSET_ID = 20733      # 四季山谷（户外空旷）
HERO1_ASSET = 20760         # 小法师(队长)
HERO2_ASSET = 21360         # 小法师升级01（队长）
HERO3_ASSET = 21361         # 小法师升级02（队长）
UPGRADE_EFFECT = 22238      # 队长升级特效
BGM_ASSET = 28985           # 轻松休闲4
PLACEHOLDER_ASSET = 10548   # 空白占位（control / 特效挂载）

# 测试数据 n=10
CIN_N = "10"

# 输出
OUTPUT_NAME = f"{LEVEL_NAME}.zip"
OUTPUT_DIR = "output/new"

# 参考包
REF_DIR = "参考-extracted/修改2"

# ==================== UUID 工具 ====================

def new_uuid():
    """生成 32 字符小写 UUID（hex 形式，无连字符）"""
    return uuid.uuid4().hex


def new_uuid_dash():
    """生成带连字符的 UUID（用于文件名）"""
    return str(uuid.uuid4())


def new_solution_uid():
    """solutionUid 为长数字字符串"""
    import random
    return str(random.randint(10**17, 10**18 - 1))


# ==================== 积木辅助函数 ====================

def V(val):
    """普通变量参数 (type=var)"""
    return {"type": "var", "val": str(val)}


def B(block):
    """块参数 (type=block)"""
    return {"type": "block", "val": block}


def EMPTY():
    """空参数占位"""
    return {}


def _wrap(v):
    """把任意输入转换为 params 槽格式。
    - str/int/float            → {type: var, val: str(v)}
    - {type: var/block, val:…} → 原样返回（已是 params 格式）
    - {define: …, sections:…}  → {type: block, val: v}  自动包装 Operator
    - 空 dict {}               → 原样（EMPTY 占位）
    - 其他 dict                → 原样
    """
    if isinstance(v, dict):
        if "type" in v and "val" in v:
            return v
        if "define" in v:
            return {"type": "block", "val": v}
        return v
    return {"type": "var", "val": str(v)}


# === Operator blocks ===

def Variable(name):
    return {
        "define": "Variable",
        "sections": [{"params": [V(name)]}]
    }


def ListGetItemAt(index, listname):
    return {
        "define": "ListGetItemAt",
        "sections": [{"params": [_wrap(index), V(listname)]}]
    }


def ListGetLength(listname):
    return {
        "define": "ListGetLength",
        "sections": [{"params": [V(listname)]}]
    }


def IsEqual(left, right):
    return {
        "define": "IsEqual",
        "sections": [{"params": [_wrap(left), EMPTY(), _wrap(right)]}]
    }


def IsGreator(left, right):
    return {
        "define": "IsGreator",
        "sections": [{"params": [_wrap(left), EMPTY(), _wrap(right)]}]
    }


def IsLess(left, right):
    return {
        "define": "IsLess",
        "sections": [{"params": [_wrap(left), EMPTY(), _wrap(right)]}]
    }


def Mod(a, b):
    return {
        "define": "Mod",
        "sections": [{"params": [_wrap(a), _wrap(b)]}]
    }


def Add(a, b):
    return {
        "define": "Add",
        "sections": [{"params": [_wrap(a), EMPTY(), _wrap(b)]}]
    }


def StrJoin(a, b):
    return {
        "define": "StrJoin",
        "sections": [{"params": [_wrap(a), _wrap(b)]}]
    }


# === Statement blocks ===

def SetVar(name, value):
    return {
        "define": "SetVar",
        "sections": [{"params": [V(name), _wrap(value)]}]
    }


def IncVar(name, delta="1"):
    return {
        "define": "IncVar",
        "sections": [{"params": [V(name), _wrap(delta)]}]
    }


def ListAdd(item, listname):
    return {
        "define": "ListAdd",
        "sections": [{"params": [_wrap(item), V(listname)]}]
    }


def ListDeleteAll(listname):
    return {
        "define": "ListDeleteAll",
        "sections": [{"params": [V(listname)]}]
    }


def BroadcastMessageAndWait(msg):
    return {
        "define": "BroadcastMessageAndWait",
        "sections": [{"params": [V(msg)]}]
    }


def BroadcastMessage(msg):
    return {
        "define": "BroadcastMessage",
        "sections": [{"params": [V(msg)]}]
    }


def WaitSeconds(sec):
    return {
        "define": "WaitSeconds",
        "sections": [{"params": [V(sec)]}]
    }


def PlaySound(name):
    return {
        "define": "PlaySound",
        "sections": [{"params": [V(name)]}]
    }


def StopAllSound():
    return {"define": "StopAllSound", "sections": [{}]}


def PlayAnimationUntil(name):
    return {
        "define": "PlayAnimationUntil",
        "sections": [{"params": [V(name)]}]
    }


def PlayAnimation(name):
    return {
        "define": "PlayAnimation",
        "sections": [{"params": [V(name)]}]
    }


def PlayBGM(name, volume=100):
    return {
        "define": "PlayBGM",
        "sections": [{"params": [V(name), V(str(volume))]}]
    }


def EndRun(text, extra=""):
    return {
        "define": "EndRun",
        "sections": [{"params": [_wrap(text), _wrap(extra)]}]
    }


def StopScript(mode="all"):
    return {
        "define": "StopScript",
        "sections": [{"params": [V(mode)]}]
    }


def Show():
    return {
        "define": "Show",
        "sections": [{"params": [EMPTY()]}]
    }


def Hide():
    return {
        "define": "Hide",
        "sections": [{"params": [EMPTY()]}]
    }


def SetSize(percent):
    return {
        "define": "SetSize",
        "sections": [{"params": [EMPTY(), _wrap(percent)]}]
    }


def ChangeSize(delta):
    return {
        "define": "ChangeSize",
        "sections": [{"params": [EMPTY(), _wrap(delta)]}]
    }


def GotoPosition3D(x, y, z):
    return {
        "define": "GotoPosition3D",
        "sections": [{"params": [V(str(x)), V(str(y)), V(str(z))]}]
    }


def PointInDirection(angle):
    return {
        "define": "PointInDirection",
        "sections": [{"params": [EMPTY(), V(str(angle))]}]
    }


def SetTitle(text):
    return {
        "define": "SetTitle",
        "sections": [{"params": [_wrap(text)]}]
    }


def If_(condition_block, *body):
    return {
        "define": "If",
        "sections": [{"params": [_wrap(condition_block)], "children": list(body)}]
    }


def IfElse_(condition_block, then_body, else_body):
    return {
        "define": "IfElse",
        "sections": [
            {"params": [_wrap(condition_block)], "children": list(then_body)},
            {"params": [], "children": list(else_body)}
        ]
    }


def Repeat_(times, *body):
    return {
        "define": "Repeat",
        "sections": [{"params": [_wrap(times)], "children": list(body)}]
    }


# === Triggers / Hats ===

def When_GameStarts(*children, pos=None):
    if pos is None:
        pos = ["200", "200"]
    return {
        "pos": pos,
        "head": {
            "define": "WhenGameStarts",
            "sections": [{"children": list(children)}]
        }
    }


def When_ReceiveMessage(msg, *children, pos=None):
    if pos is None:
        pos = ["200", "200"]
    return {
        "pos": pos,
        "head": {
            "define": "WhenReceiveMessage",
            "sections": [{"params": [V(msg)], "children": list(children)}]
        }
    }


# === 摄像机积木 ===

def SetCameraFOV(fov):
    return {
        "define": "SetCameraFOV",
        "sections": [{"params": [V(str(fov))]}]
    }


def PointInPitch(pitch):
    return {
        "define": "PointInPitch",
        "sections": [{"params": [EMPTY(), V(str(pitch))]}]
    }


def CameraFollow(target, distance, offset_y, height):
    return {
        "define": "CameraFollow",
        "sections": [{"params": [V(target), V(str(distance)), V(str(offset_y)), V(str(height))]}]
    }


# ==================== 节点构造 ====================

def make_blockscript(fragments, name="BlockScript", myblocks=None):
    bs = {
        "type": "BlockScript",
        "id": new_uuid(),
        "props": {"Name": name, "EditMode": 0},
        "fragments": fragments
    }
    if myblocks:
        bs["myblocks"] = myblocks
    return bs


def make_character(name, asset_id, position, scale="1", visible=True, euler=None):
    if euler is None:
        euler = ["0", "90", "0"]
    return {
        "type": "Character",
        "id": new_uuid(),
        "props": {
            "Name": name,
            "EditMode": 0,
            "Visible": visible,
            "Position": [str(position[0]), str(position[1]), str(position[2])],
            "EulerAngles": euler,
            "RotConstraint": 0,
            "ConstraintEulerAngles": ["0", "0", "0"],
            "Scale": str(scale),
            "CastShadow": True,
            "Color": "#FFFFFFFF",
            "Material": "Basic",
            "Transparency": "0",
            "Size": ["1.1", "2.55", "1.1"],
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
            "EmotionAnimations": "[]"
        }
    }


def make_meshpart(name, asset_id, position, visible=True, scale="1"):
    return {
        "type": "MeshPart",
        "id": new_uuid(),
        "props": {
            "Name": name,
            "EditMode": 0,
            "Visible": visible,
            "Position": [str(position[0]), str(position[1]), str(position[2])],
            "EulerAngles": ["0", "90", "0"],
            "RotConstraint": 0,
            "ConstraintEulerAngles": ["0", "0", "0"],
            "Scale": str(scale),
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
            "AssetId": asset_id,
            "EmotionAnimations": "[]"
        }
    }


def make_effect(name, asset_id, full_screen=False, visible=True, position=None):
    props = {
        "Name": name,
        "EditMode": 0,
        "AssetId": asset_id,
        "Loop": False
    }
    if full_screen:
        props["FullScreenBeforeUI"] = True
    else:
        if position is not None:
            props["Position"] = [str(p) for p in position]
        props["Visible"] = visible
    return {
        "type": "Effect",
        "id": new_uuid(),
        "props": props
    }


def make_music(name, asset_id):
    return {
        "type": "Music",
        "id": new_uuid(),
        "props": {
            "Name": name,
            "EditMode": 0,
            "AssetId": asset_id,
            "Loop": False,
            "Is3D": False
        }
    }


def make_sound(name, asset_id):
    return {
        "type": "Sound",
        "id": new_uuid(),
        "props": {
            "Name": name,
            "EditMode": 0,
            "AssetId": asset_id,
            "Loop": False,
            "Is3D": False
        }
    }


def make_label_bubble(name, position, size, scale, follow_id=None, follow_node=None,
                     follow_offset=None, title="Lv.0", pivot=None, view="LabelBubblenobg"):
    """创建 LabelBubble / LabelBubblenobg UIView 节点
    view: 'LabelBubblenobg' 裸字无底 / 'LabelBubble' 气泡带底框"""
    if pivot is None:
        pivot = ["0.5", "0.5"]
    props = {
        "Name": name,
        "EditMode": 0,
        "Visible": True,
        "Position": [str(p) for p in position],
        "Size": [str(s) for s in size],
        "Scale": str(scale),
        "Pivot": pivot,
        "Rotation": "0",
        "RotConstraint": 0,
        "Type": "Button",
        "Title": title,
        "Anchor": True,
        "Package": "Basic",
        "View": view,
        "Disable": False,
        "Transparency": "1"
    }
    if follow_id:
        props["Follow"] = follow_id
        props["FollowNode"] = follow_node or "TopBoneCAPFix"
        props["FollowOffset"] = [str(o) for o in (follow_offset or ["-0.75", "-97.6"])]
    return {
        "type": "UIView",
        "id": new_uuid(),
        "props": props
    }


# ==================== 生成主流程 ====================

def build_level():
    # ---- 预先生成关键 UUID（用于互相引用）----
    hero1 = make_character("小法师队长", HERO1_ASSET, (0, 0.27, 0),
                           scale="1", visible=True, euler=["0", "90", "0"])
    hero2 = make_character("小法师升级1", HERO2_ASSET, (0, 0.27, 0),
                           scale="1", visible=False, euler=["0", "90", "0"])
    hero3 = make_character("小法师升级2", HERO3_ASSET, (0, 0.27, 0),
                           scale="1", visible=False, euler=["0", "90", "0"])
    hero1_id = hero1["id"]
    hero2_id = hero2["id"]
    hero3_id = hero3["id"]

    # control 物件
    control = make_meshpart("control", PLACEHOLDER_ASSET, (0, 0.85, 0), visible=False)

    # 升级特效 —— 设计师示范包实证：
    #   Effect 直接作为 Character(hero1) 的子节点，Name 即作为"动画名"注册
    #   脚本里用 PlayAnimation("队长升级特效") 即可触发，无需 Show/Hide
    # Effect props 仅含 {Name, EditMode, AssetId, Loop, FullScreenBeforeUI}（对齐参考包）
    upgrade_fx_effect = make_effect("队长升级特效", UPGRADE_EFFECT, full_screen=True)

    # 头顶等级 UI (绑定主角1)
    lvl_ui = make_label_bubble(
        "等级标签", position=[640, 200], size=[361, 149], scale="0.8",
        follow_id=hero1_id, follow_node="TopBoneCAPFix",
        follow_offset=["-0.75", "-150"], title="Lv.0"
    )
    lvl_ui_id = lvl_ui["id"]

    # 升级统计对话框 UI —— 移至右上角，换带底框的气泡样式（黑字在气泡上更清晰）
    # 屏幕默认 1280x720；右上角 pivot (1, 0)，留 padding ~100
    dialog_ui = make_label_bubble(
        "升级通知",
        position=[1180, 90], size=[198, 149], scale="0.9",
        title="准备升级...",
        pivot=["1", "0"],
        view="LabelBubble"  # 带底框气泡（设计师示范包尺寸 198x149）
    )
    dialog_ui["props"]["Visible"] = False
    dialog_ui_id = dialog_ui["id"]

    # ---- 根 BlockScript ----
    root_bs_fragments = [
        # 传递成功
        When_ReceiveMessage(
            "传递成功",
            StopAllSound(),
            PlaySound("结算效果-成功"),
            PlayAnimationUntil("样例通过"),
            WaitSeconds("3"),
            SetVar("*OJ-输入信息", ""),
            SetVar("*OJ-执行结果", ""),
            EndRun("运行结束", ""),
            StopScript("all"),
            pos=["200", "200"]
        ),
        # 传递失败
        When_ReceiveMessage(
            "传递失败",
            StopAllSound(),
            PlaySound("结算效果-失败"),
            PlayAnimationUntil("样例不通过"),
            WaitSeconds("3"),
            SetVar("*OJ-输入信息", ""),
            SetVar("*OJ-执行结果", ""),
            EndRun("没过关", Variable("err_msg")),
            StopScript("all"),
            pos=["200", "600"]
        ),
        # BGM
        When_GameStarts(
            PlayBGM("轻松休闲4", 100)
        ),
    ]
    root_bs_fragments[2]["pos"] = ["200", "1000"]
    root_bs = make_blockscript(root_bs_fragments)

    # ---- control BlockScript ----
    control_bs_fragments = [
        When_GameStarts(
            SetVar("*OJ-Judge", "1"),
            ListAdd(CIN_N, "cin_cut"),
            # 前置校验：n 必须在 1~30 之间
            If_(
                IsLess(ListGetItemAt("1", "cin_cut"), "1"),
                SetVar("err_msg", "n 需要在 1-30 之间"),
                BroadcastMessageAndWait("传递失败"),
                StopScript("all")
            ),
            If_(
                IsGreator(ListGetItemAt("1", "cin_cut"), "30"),
                SetVar("err_msg", "n 需要在 1-30 之间"),
                BroadcastMessageAndWait("传递失败"),
                StopScript("all")
            ),
            # 判题分支
            If_(
                IsEqual(Variable("*OJ-Judge"), "0"),
                SetVar("err_msg", "代码不正确，再试试吧"),
                BroadcastMessageAndWait("传递失败")
            ),
            If_(
                IsEqual(Variable("*OJ-Judge"), "1"),
                BroadcastMessageAndWait("展示关卡效果"),
                BroadcastMessageAndWait("传递成功")
            )
        )
    ]
    control_bs = make_blockscript(control_bs_fragments)
    control["children"] = [control_bs]

    # ---- 升级特效 ----
    # 不再需要独立 BlockScript —— 特效作为 hero1 子节点，由 PlayAnimation("队长升级特效") 直接触发

    # ---- 头顶等级 UI BlockScript ----
    # 演出主流程放这里：监听"展示关卡效果"，驱动整个循环
    lvl_ui_bs_fragments = [
        When_GameStarts(
            SetTitle("Lv.0"),
            Show()
        ),
        When_ReceiveMessage(
            "展示关卡效果",
            SetVar("i", "0"),
            SetTitle("Lv.0"),
            WaitSeconds("0.5"),
            # 循环 n 次
            Repeat_(
                ListGetItemAt("1", "cin_cut"),
                IncVar("i", "1"),
                SetTitle(StrJoin("Lv.", Variable("i"))),
                # 判断是否 i%5==0
                IfElse_(
                    IsEqual(Mod(Variable("i"), "2"), "0"),  # 这是占位，后面替换
                    [  # then
                        WaitSeconds("0.05"),
                    ],
                    [  # else
                        WaitSeconds("0.15"),
                    ]
                ),
                # 大升级判定
                If_(
                    IsEqual(Mod(Variable("i"), "5"), "0"),
                    BroadcastMessageAndWait("大升级")
                )
            ),
            WaitSeconds("0.5"),
            BroadcastMessageAndWait("完成展示"),
            pos=["200", "500"]
        )
    ]
    # 精简：去掉那个占位的 IfElse
    lvl_ui_bs_fragments[1]["head"]["sections"][0]["children"] = [
        SetVar("i", "0"),
        SetTitle("Lv.0"),
        WaitSeconds("0.5"),
        Repeat_(
            ListGetItemAt("1", "cin_cut"),
            IncVar("i", "1"),
            SetTitle(StrJoin("Lv.", Variable("i"))),
            IfElse_(
                IsEqual(Mod(Variable("i"), "5"), "0"),
                [
                    BroadcastMessageAndWait("大升级"),
                ],
                [
                    BroadcastMessageAndWait("小升级"),
                ]
            ),
            WaitSeconds("0.1")
        ),
        WaitSeconds("0.5"),
        BroadcastMessageAndWait("完成展示")
    ]
    lvl_ui_bs = make_blockscript(lvl_ui_bs_fragments)
    lvl_ui["children"] = [lvl_ui_bs]

    # ---- 对话框 UI BlockScript ----
    dialog_bs_fragments = [
        When_ReceiveMessage(
            "大升级",
            SetTitle(StrJoin("大升级！Lv.", Variable("i"))),
            Show(),
            WaitSeconds("1.2"),
            Hide(),
            pos=["200", "200"]
        ),
        When_ReceiveMessage(
            "完成展示",
            SetTitle("完成！共大升级 2 次"),
            Show(),
            WaitSeconds("1.5"),
            Hide(),
            pos=["200", "600"]
        )
    ]
    dialog_bs = make_blockscript(dialog_bs_fragments)
    dialog_ui["children"] = [dialog_bs]

    # ---- 主角1（队长 20760）BlockScript ----
    # 角色唯一"肉身"，一直显示；升级形态（21360/21361）只是闪烁特效
    # 动画资源（20760 实际拥有）：
    #   - idle（标准待机）
    #   - jingyataitou（惊讶抬头 → 小升级反应）
    #   - qitiao_start / qitiao_loop / qitiao_end（起跳三段 → 大升级仪式）
    # 大升级流程：起跳 → 空中闪升级形态 → 落地 → 自身 SetSize 放大
    hero1_bs_fragments = [
        When_GameStarts(
            Show(),
            SetSize("100"),
            GotoPosition3D("0", "0.27", "0"),
            PointInDirection("90"),
            PlayAnimation("idle")
        ),
        # --- 小升级：特效 + 动作 并行触发（均为非阻塞 PlayAnimation）---
        When_ReceiveMessage(
            "小升级",
            PlayAnimation("队长升级特效"),   # 非阻塞
            PlayAnimation("jingyataitou"),   # 非阻塞（与特效并行）
            WaitSeconds("0.4"),              # 等约 0.4s
            PlayAnimation("idle"),
            pos=["200", "300"]
        ),
        # --- 大升级主线（Phase 1 爆发 → Phase 2 变身 → Phase 3 回归）---
        When_ReceiveMessage(
            "大升级",
            # Phase 1 (0 ~ 2s): 三线并行 —— 特效 / 变大 / xingfen 动作
            PlayAnimation("队长升级特效"),     # 非阻塞：特效开始
            BroadcastMessage("开始变大"),      # 非阻塞：变大协程独立启动（由下方同 Character 内的另一片段响应）
            PlayAnimationUntil("xingfen"),     # 阻塞 ~2s：主线动作等完
            # Phase 2 (2 ~ 5s): 升级形态叠加闪光（阻塞串行）
            IfElse_(
                IsEqual(Variable("i"), "5"),
                [BroadcastMessageAndWait("闪烁升级1")],
                [BroadcastMessageAndWait("闪烁升级2")]
            ),
            # 摄像机跟随（暂留；设计师后续会再调）
            IfElse_(
                IsEqual(Variable("i"), "5"),
                [CameraFollow("control", "390", "0", "65")],
                [CameraFollow("control", "480", "0", "80")]
            ),
            # Phase 3: 回归待机
            PlayAnimation("idle"),
            pos=["200", "500"]
        ),
        # --- 变大协程（独立响应"开始变大"，与主线并行执行）---
        # 共 6 × 0.2s = 1.2s 渐变，每次 +5% 累计 +30%
        # 1.2s 刚好贯穿 xingfen 动作大部分时长，呈现"动作中持续变大"
        When_ReceiveMessage(
            "开始变大",
            Repeat_(
                "6",
                WaitSeconds("0.2"),
                ChangeSize("5")
            ),
            pos=["800", "500"]
        )
    ]
    hero1_bs = make_blockscript(hero1_bs_fragments)
    # 特效作为 hero1 子节点：PlayAnimation("队长升级特效") 能直接识别
    hero1["children"] = [hero1_bs, upgrade_fx_effect]

    # ---- 主角2（升级01 21360）BlockScript ----
    # 资源仅含 yan_shd / yifu_shd / zui_shd 三段发光动画 → 只做变身闪烁
    # 初始隐藏，收到"闪烁升级1"时 Show → 依次播放三段 shd → Hide
    hero2_bs_fragments = [
        When_GameStarts(
            Hide(),
            GotoPosition3D("0", "0.27", "0"),
            PointInDirection("90"),
            SetSize("130"),
            pos=["200", "200"]
        ),
        When_ReceiveMessage(
            "闪烁升级1",
            Show(),
            PlayAnimationUntil("yan_shd"),
            PlayAnimationUntil("yifu_shd"),
            PlayAnimationUntil("zui_shd"),
            Hide(),
            pos=["200", "500"]
        )
    ]
    hero2_bs = make_blockscript(hero2_bs_fragments)
    hero2["children"] = [hero2_bs]

    # ---- 主角3（升级02 21361）BlockScript ----
    hero3_bs_fragments = [
        When_GameStarts(
            Hide(),
            GotoPosition3D("0", "0.27", "0"),
            PointInDirection("90"),
            SetSize("160"),
            pos=["200", "200"]
        ),
        When_ReceiveMessage(
            "闪烁升级2",
            Show(),
            PlayAnimationUntil("yan_shd"),
            PlayAnimationUntil("yifu_shd"),
            PlayAnimationUntil("zui_shd"),
            Hide(),
            pos=["200", "500"]
        )
    ]
    hero3_bs = make_blockscript(hero3_bs_fragments)
    hero3["children"] = [hero3_bs]

    # ---- 摄像机节点 ----
    # 正面视角（胸口平视）：
    #   - Current = "CamEdit"（设计师示范包实证可用，真正起作用的是 WhenGameStarts 里的 PointInPitch/Direction）
    #   - WhenGameStarts Trigger 强制配置水平视角（Pitch=90）
    #   - Pitch=90 = 水平看；PointInDirection(-90) = 朝 X- 方向（场景默认正面）
    #   - CameraFollow(control, 300, 0, 50) = 前方 3m、胸口 50cm 高（NPC 默认胸部中心）
    cam_bs_fragments = [
        When_GameStarts(
            SetCameraFOV("35"),
            PointInDirection("-90"),
            PointInPitch("90"),
            CameraFollow("control", "300", "0", "50"),
            pos=["487", "360"]
        )
    ]
    cam_bs = make_blockscript(cam_bs_fragments)

    camera_service = {
        "type": "CameraService",
        "id": new_uuid(),
        "props": {"Name": "Camera", "EditMode": 0, "Current": "CamEdit"},
        "children": [cam_bs]
    }

    # 室外日间 Skybox
    skybox = {
        "type": "SkyboxService",
        "id": new_uuid(),
        "props": {
            "Name": "Skybox",
            "EditMode": 0,
            "TimeOfDay": "12",
            "AmbientColor": "#FFFFFFFF",
            "SunSize": "0.5",
            "SunColor": "#FFFDE8FF",
            "SunBrightness": "1.0",
            "MoonSize": "0.2",
            "MoonColor": "#00000000",
            "MoonBrightness": "0",
            "StarCount": 0
        }
    }

    block_service = {
        "type": "BlockService",
        "id": new_uuid(),
        "props": {
            "Name": "Blocks",
            "EditMode": 0,
            "Modules": ["motion", "looks", "events", "control", "sound", "sensing",
                       "operators", "variable", "myblocks", "music", "magic",
                       "physics", "stage", "ui", "animation"]
        }
    }

    services_folder = {
        "type": "Folder",
        "id": new_uuid(),
        "props": {"Name": "services", "EditMode": 0},
        "children": [block_service, skybox, camera_service]
    }

    # ---- 特效节点（全屏样例通过/不通过）----
    fx_pass = make_effect("样例通过", 27888, full_screen=True)
    fx_fail = make_effect("样例不通过", 27887, full_screen=True)

    # ---- 音频 ----
    music_bgm = make_music("轻松休闲4", BGM_ASSET)
    snd_ok = make_sound("结算效果-成功", 28966)
    snd_fail = make_sound("结算效果-失败", 28965)
    snd_item = make_sound("点击道具", 28967)

    # ---- 组装 Scene ----
    scene_children = [
        services_folder,
        root_bs,
        control,
        hero1,  # 升级特效挂载已作为 hero1 子节点跟随
        hero2,
        hero3,
        lvl_ui,
        dialog_ui,
        fx_pass,
        fx_fail,
        music_bgm,
        snd_ok,
        snd_fail,
        snd_item
    ]

    scene = {
        "type": "Scene",
        "id": new_uuid(),
        "props": {
            "Name": "Scene",
            "EditMode": 0,
            "BoundsCenter": ["0", "2.833", "0"],
            "BoundsSize": ["16", "7.67", "12"],
            "AssetId": SCENE_ASSET_ID
        },
        "props2": {
            "variable": {"type": "Simple", "value": "0"},
            "#EVENT": {
                "type": "SimpleList",
                "value": [
                    "CMD_NewMessage", "传递失败", "初始化", "展示关卡效果",
                    "传递成功", "大升级", "小升级", "完成展示",
                    "闪烁升级1", "闪烁升级2", "闪烁升级3", "开始变大"
                ]
            },
            "err_msg": {"type": "Simple", "value": "0"},
            "*OJ-输入信息": {"type": "Simple", "value": ""},
            "*OJ-执行结果": {"type": "Simple", "value": ""},
            "cmd": {"type": "Simple", "value": "0"},
            "state": {"type": "Simple", "value": "0"},
            "*OJ-Judge": {"type": "Simple", "value": "0"},
            "输入元素": {"type": "Simple", "value": "0"},
            "n": {"type": "Simple", "value": "0"},
            "cin_cut": {"type": "SimpleList", "value": []},
            "输出元素": {"type": "Simple", "value": "0"},
            "n1": {"type": "Simple", "value": "0"},
            "space-flag": {"type": "Simple", "value": "0"},
            "cout_cut": {"type": "SimpleList", "value": []},
            "i": {"type": "Simple", "value": "0"}
        },
        "children": scene_children
    }

    # ---- 最终 WS 文件 ----
    ts = int(time.time() * 1000)

    # assets (UIPackageObject)
    assets = {
        "type": "Folder",
        "id": new_uuid(),
        "props": {"Name": "assets", "EditMode": 0},
        "children": [
            {"type": "UIPackageObject", "id": new_uuid(),
             "props": {"Name": "Basic", "EditMode": 0, "AssetId": 27561}},
            {"type": "UIPackageObject", "id": new_uuid(),
             "props": {"Name": "Icons", "EditMode": 0, "AssetId": 27562}}
        ]
    }

    agents = {
        "type": "Folder",
        "id": new_uuid(),
        "props": {"Name": "agents", "EditMode": 0}
    }

    # res 数组：所有引用的 AssetId
    res_ids = sorted(set([
        27561, 27562,                    # UI 包
        SCENE_ASSET_ID,                  # 场景
        PLACEHOLDER_ASSET,               # control / 特效挂载
        HERO1_ASSET, HERO2_ASSET, HERO3_ASSET,  # 主角3形态
        UPGRADE_EFFECT,                  # 升级特效
        27887, 27888,                    # 全屏特效
        BGM_ASSET,                       # BGM
        28965, 28966, 28967              # 音效
    ]))

    ws_data = {
        "name": "Project_0",
        "desc": "",
        "icon": "",
        "author": "",
        "created": ts,
        "modified": ts,
        "type": 3,
        "version": 3,
        "stageType": 0,
        "scene": scene,
        "agents": agents,
        "assets": assets,
        "res": res_ids,
        "showmyblock": True,
        "dialogues": {"DialogueGroups": []},
        "editorScene": {
            "cameras": [{
                "name": "default",
                "position": ["0", "20", "0"],
                "rotation": ["0.7071068", "0", "0", "0.7071068"],
                "fov": 30.0
            }]
        },
        "projectMode": 2
    }

    return ws_data, ts


def build_solution(ws_uuid_filename, solution_uid, ts):
    cam_service_uuid = new_uuid()
    cam_script1_uuid = new_uuid()
    cam_script2_uuid = new_uuid()

    # 摄像机的全局 BlockScript - 与 services 下的 CameraService 一致就行
    cam_global_bs1 = {
        "type": "BlockScript",
        "id": cam_script1_uuid,
        "props": {"Name": "BlockScript", "EditMode": 0},
        "uiState": {
            "pos": ["510", "848"],
            "scroll": ["722", "746"],
            "scale": "1"
        }
    }
    cam_global_bs2 = {
        "type": "BlockScript",
        "id": cam_script2_uuid,
        "props": {"Name": "BlockScript", "EditMode": 0},
        "uiState": {
            "pos": ["0", "0"],
            "scroll": ["0", "0"],
            "scale": "1"
        }
    }

    project_uuid = new_uuid_dash()

    return {
        "init": new_uuid_dash(),
        "name": LEVEL_NAME,
        "author": "",
        "modified": ts,
        "version": 1,
        "projects": [{
            "file": f"pangu3d/universe/develop/{solution_uid}/{ws_uuid_filename}.ws",
            "icon": f"pangu3d/universe/develop/{solution_uid}/{new_uuid_dash()}.png",
            "name": "Project_0",
            "uuid": project_uuid
        }],
        "globals": [{
            "refs": [project_uuid],
            "obj": {
                "type": "CameraService",
                "id": cam_service_uuid,
                "props": {"Name": "Camera", "EditMode": 0, "Current": "CamEdit"},
                "children": [cam_global_bs1, cam_global_bs2]
            }
        }]
    }


def main():
    print("=== 生成关卡：5级角色升级 ===")

    # 生成 WS
    ws_data, ts = build_level()
    ws_filename = new_uuid_dash()
    solution_uid = new_solution_uid()

    # 生成 solution.json 和 export_info.json
    solution_data = build_solution(ws_filename, solution_uid, ts)
    export_info = {"solutionUid": solution_uid}

    # 打包目录
    with tempfile.TemporaryDirectory() as tmp:
        ws_path = os.path.join(tmp, f"{ws_filename}.ws")
        with open(ws_path, 'w', encoding='utf-8') as f:
            json.dump(ws_data, f, ensure_ascii=False, separators=(',', ':'))
        print(f"[OK] WS 文件: {os.path.getsize(ws_path)} bytes")

        sol_path = os.path.join(tmp, "solution.json")
        with open(sol_path, 'w', encoding='utf-8') as f:
            json.dump(solution_data, f, ensure_ascii=False, indent=2)
        print(f"[OK] solution.json: {os.path.getsize(sol_path)} bytes")

        exp_path = os.path.join(tmp, "export_info.json")
        with open(exp_path, 'w', encoding='utf-8') as f:
            json.dump(export_info, f, ensure_ascii=False)
        print(f"[OK] export_info.json: {os.path.getsize(exp_path)} bytes")

        # 打包为 zip
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_zip = os.path.join(OUTPUT_DIR, OUTPUT_NAME)
        # 不覆盖旧文件：如果存在，加时间戳后缀
        if os.path.exists(out_zip):
            base, ext = os.path.splitext(OUTPUT_NAME)
            stamp = time.strftime("%Y%m%d-%H%M%S")
            out_zip = os.path.join(OUTPUT_DIR, f"{base}-{stamp}{ext}")

        with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for fn in [f"{ws_filename}.ws", "solution.json", "export_info.json"]:
                zf.write(os.path.join(tmp, fn), fn)

        print(f"[OK] 输出 zip: {out_zip}  ({os.path.getsize(out_zip)} bytes)")

    print("\n=== 完成 ===")


if __name__ == "__main__":
    main()
