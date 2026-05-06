#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建汉诺塔挑战工作区 (.ws)。

用法：
  python scripts/_build_hanoi.py

输出：
  output/new/汉诺塔挑战_workdir/<uuid>.ws
  output/new/汉诺塔挑战_workdir/solution.json   (updated)
  output/new/汉诺塔挑战_workdir/export_info.json (updated)

关键坐标系：
  Position[0]=前后(X), [1]=高度(Y), [2]=左右(Z)
  GlideSecsToPosition3D(sec, x, y, z) 单位：米

积木参数规范（来自 params_registry.json）：
  IsEqual / IsGreator  → 3 params [a, {}, b]（中间空占位）
  ListDeleteALl        → 1 param  [listname]（注意拼写 AaL）
  ListGetItemAt        → 2 params [index, listname]
  ListGetLength        → 1 param  [listname]
  GlideSecsToPosition3D → 4 params [sec,x,y,z]
  IfElse               → section[0] has 1 param (condition)
"""
from __future__ import annotations

import glob
import json
import os
import sys
import uuid
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKDIR = ROOT / "output" / "new" / "汉诺塔挑战_workdir"

# 新建 UUID，用于 .ws 文件名、solution.init、export_info.solutionUid
NEW_WS_UUID_HEX = uuid.uuid4().hex          # e.g. "a1b2c3..."
WS_FILENAME     = NEW_WS_UUID_HEX + ".ws"   # e.g. "a1b2c3....ws"
WS_PATH         = WORKDIR / WS_FILENAME
# solution.init 和 export_info.solutionUid 必须相同（N11 规则）
SOLUTION_UID    = str(uuid.uuid4())          # e.g. "xxxxxxxx-xxxx-..."


# ============================================================
# 积木辅助函数
# ============================================================

def lit(val: str | int | float) -> dict:
    """固定字面量 param"""
    return {"type": "var", "val": str(val)}


def var_ref(name: str) -> dict:
    """读取变量（Variable 积木），用于 [值] 槽位"""
    return {"type": "block", "val": {
        "define": "Variable",
        "sections": [{"params": [{"type": "var", "val": name, "name": name}]}]
    }}


def setvar(name: str, val_param: dict) -> dict:
    return {"define": "SetVar", "sections": [{"params": [
        {"type": "var", "val": name, "name": name}, val_param
    ]}]}


def incvar(name: str, delta_str: str) -> dict:
    return {"define": "IncVar", "sections": [{"params": [
        {"type": "var", "val": name, "name": name}, lit(delta_str)
    ]}]}


def listdeleteall(listname: str) -> dict:
    # 生产拼写是 ListDeleteALl（注意末尾大写 L）
    return {"define": "ListDeleteALl", "sections": [{"params": [
        {"type": "var", "val": listname, "name": listname}
    ]}]}


def listadd(item_param: dict, listname: str) -> dict:
    return {"define": "ListAdd", "sections": [{"params": [
        item_param, {"type": "var", "val": listname, "name": listname}
    ]}]}


def listdelete(idx_param: dict, listname: str) -> dict:
    return {"define": "ListDelete", "sections": [{"params": [
        idx_param, {"type": "var", "val": listname, "name": listname}
    ]}]}


def listgetlength(listname: str) -> dict:
    return {"define": "ListGetLength", "sections": [{"params": [
        {"type": "var", "val": listname, "name": listname}
    ]}]}


def listgetitem(idx_param: dict, listname: str) -> dict:
    return {"define": "ListGetItemAt", "sections": [{"params": [
        idx_param, {"type": "var", "val": listname, "name": listname}
    ]}]}


def equalto(a: dict, b: dict) -> dict:
    # IsEqual 是 [O] 运算符类型，需要中间 {} 占位 → 3 params
    return {"define": "IsEqual", "sections": [{"params": [a, {}, b]}]}


def isgreater(a: dict, b: dict) -> dict:
    # IsGreator（注意拼写），[O] 运算符类型，中间 {} 占位 → 3 params
    return {"define": "IsGreator", "sections": [{"params": [a, {}, b]}]}


def ifelse(cond: dict, then_list: list, else_list: list | None = None) -> dict:
    # IfElse 有 2 个 sections：[0] 条件+then，[1] 空params+else
    return {"define": "IfElse", "sections": [
        {"params": [cond], "children": then_list},
        {"params": [], "children": else_list or []}
    ]}


def broadcast(msg: str) -> dict:
    return {"define": "BroadcastMessage", "sections": [{"params": [lit(msg)]}]}


def broadcast_wait(msg: str) -> dict:
    return {"define": "BroadcastMessageAndWait", "sections": [{"params": [lit(msg)]}]}


def glide(sec: str, x_param: dict, y_param: dict, z_param: dict) -> dict:
    # GlideSecsToPosition3D 4 params: [sec, x, y, z]，单位米
    return {"define": "GlideSecsToPosition3D", "sections": [{"params": [
        lit(sec), x_param, y_param, z_param
    ]}]}


def camera_follow(target: str, dist: str, offset_y: str, height: str) -> dict:
    # CameraFollow 4 params: [target, distance, offsetY, height]，单位厘米
    return {"define": "CameraFollow", "sections": [{"params": [
        lit(target), lit(dist), lit(offset_y), lit(height)
    ]}]}


def point_in_dir(deg: str) -> dict:
    # PointInDirection [S] 型：第1 param 是 {} self 占位 → 2 params
    return {"define": "PointInDirection", "sections": [{"params": [{}, lit(deg)]}]}


def point_in_pitch(deg: str) -> dict:
    # PointInPitch [S] 型：同上 → 2 params
    return {"define": "PointInPitch", "sections": [{"params": [{}, lit(deg)]}]}


def set_camera_fov(deg: str) -> dict:
    return {"define": "SetCameraFOV", "sections": [{"params": [lit(deg)]}]}


# ============================================================
# Fragment 构建辅助
# ============================================================

def make_fragment(hat_define: str, hat_params: list, children: list) -> dict:
    """在 ws 文件格式中构建一个 fragment。"""
    section: dict = {}
    if hat_params:
        section["params"] = hat_params
    if children:
        section["children"] = children
    return {
        "pos": ["100", "100"],
        "head": {
            "define": hat_define,
            "sections": [section if (hat_params or children) else {}]
        }
    }


# ============================================================
# 游戏逻辑积木
# ============================================================

def get_stack_len(col_var: str, result_var: str) -> dict:
    """根据列名变量（A/B/C）取栈长度，存入 result_var。"""
    return ifelse(equalto(var_ref(col_var), lit("A")),
        [setvar(result_var, {"type": "block", "val": listgetlength("stackA")})],
        [ifelse(equalto(var_ref(col_var), lit("B")),
            [setvar(result_var, {"type": "block", "val": listgetlength("stackB")})],
            [setvar(result_var, {"type": "block", "val": listgetlength("stackC")})]
        )]
    )


def get_stack_top(col_var: str, len_var: str, result_var: str) -> dict:
    """根据列名变量取栈顶元素（索引=len_var），存入 result_var。"""
    return ifelse(equalto(var_ref(col_var), lit("A")),
        [setvar(result_var, {"type": "block", "val": listgetitem(var_ref(len_var), "stackA")})],
        [ifelse(equalto(var_ref(col_var), lit("B")),
            [setvar(result_var, {"type": "block", "val": listgetitem(var_ref(len_var), "stackB")})],
            [setvar(result_var, {"type": "block", "val": listgetitem(var_ref(len_var), "stackC")})]
        )]
    )


def delete_stack_top(col_var: str, len_var: str) -> dict:
    """根据列名变量删除栈顶（索引=len_var）。"""
    return ifelse(equalto(var_ref(col_var), lit("A")),
        [listdelete(var_ref(len_var), "stackA")],
        [ifelse(equalto(var_ref(col_var), lit("B")),
            [listdelete(var_ref(len_var), "stackB")],
            [listdelete(var_ref(len_var), "stackC")]
        )]
    )


def add_to_stack(col_var: str, item_param: dict) -> dict:
    """根据列名变量向栈末尾添加元素。"""
    return ifelse(equalto(var_ref(col_var), lit("A")),
        [listadd(item_param, "stackA")],
        [ifelse(equalto(var_ref(col_var), lit("B")),
            [listadd(item_param, "stackB")],
            [listadd(item_param, "stackC")]
        )]
    )


def set_z_for_col(col_var: str, z_var: str) -> dict:
    """根据列名变量设置 z 坐标（A=-2.5, B=0, C=2.5）。"""
    return ifelse(equalto(var_ref(col_var), lit("A")),
        [setvar(z_var, lit("-2.5"))],
        [ifelse(equalto(var_ref(col_var), lit("B")),
            [setvar(z_var, lit("0"))],
            [setvar(z_var, lit("2.5"))]
        )]
    )


def make_slot_to_h() -> dict:
    """dest_slot（1-6）→ final_h（目标高度）映射。"""
    return ifelse(equalto(var_ref("dest_slot"), lit("1")),
        [setvar("final_h", lit("0.355"))],
        [ifelse(equalto(var_ref("dest_slot"), lit("2")),
            [setvar("final_h", lit("0.610"))],
            [ifelse(equalto(var_ref("dest_slot"), lit("3")),
                [setvar("final_h", lit("0.865"))],
                [ifelse(equalto(var_ref("dest_slot"), lit("4")),
                    [setvar("final_h", lit("1.120"))],
                    [ifelse(equalto(var_ref("dest_slot"), lit("5")),
                        [setvar("final_h", lit("1.375"))],
                        [setvar("final_h", lit("1.630"))]
                    )]
                )]
            )]
        )]
    )


def build_valid_move_seq() -> list:
    """有效移动时执行的积木序列。"""
    return [
        # moving_disc = src_top（记录当前要移动的盘子编号）
        setvar("moving_disc", var_ref("src_top")),
        # dest_slot = dest_len + 1（目标位置在目标栈的第几槽）
        setvar("dest_slot", var_ref("dest_len")),
        incvar("dest_slot", "1"),
        # 计算动画坐标
        set_z_for_col("sel",     "src_z"),
        set_z_for_col("clicked", "dest_z"),
        make_slot_to_h(),
        # 更新栈数据
        delete_stack_top("sel",     "src_len"),
        add_to_stack("clicked", var_ref("moving_disc")),
        incvar("move_count", "1"),
        # 播放动画并等待
        broadcast_wait("do_anim"),
        setvar("sel", lit("")),
        # 胜利检测：stackC 长度 == 6
        ifelse(
            equalto({"type": "block", "val": listgetlength("stackC")}, lit("6")),
            [broadcast("game_win")],
            []
        )
    ]


# ============================================================
# Fragment 构建
# ============================================================

def build_frag_game_start() -> dict:
    """ctrl_game: WhenGameStarts → 初始化游戏逻辑变量（相机块移到 CameraService）"""
    children = [
        # 初始化三个栈（A柱从底到顶：6,5,4,3,2,1）
        listdeleteall("stackA"),
        listdeleteall("stackB"),
        listdeleteall("stackC"),
        listadd(lit("6"), "stackA"),
        listadd(lit("5"), "stackA"),
        listadd(lit("4"), "stackA"),
        listadd(lit("3"), "stackA"),
        listadd(lit("2"), "stackA"),
        listadd(lit("1"), "stackA"),
        # 初始化控制变量
        setvar("sel",        lit("")),
        setvar("move_count", lit("0")),
        setvar("h_lift",     lit("2.5")),
    ]
    return make_fragment("WhenGameStarts", [], children)


def build_frag_camera_start() -> dict:
    """CameraService: WhenGameStarts → 相机设置（CameraFollow 只能在 CameraService）"""
    children = [
        set_camera_fov("25"),
        point_in_dir("-90"),
        point_in_pitch("90"),
        camera_follow("ctrl_cam", "1600", "0", "0"),
    ]
    return make_fragment("WhenGameStarts", [], children)


def build_frag_do_click() -> dict:
    """ctrl_game: WhenReceiveMessage(do_click) → 完整汉诺塔逻辑"""
    valid_move_seq = build_valid_move_seq()
    children = [
        ifelse(
            # 情况1：当前没有选中的柱子
            equalto(var_ref("sel"), lit("")),
            [
                # 尝试选中 clicked 柱（非空才能选）
                get_stack_len("clicked", "src_len"),
                ifelse(
                    isgreater(var_ref("src_len"), lit("0")),
                    [setvar("sel", var_ref("clicked"))],
                    []
                )
            ],
            # 情况2：已经有选中的柱子
            [ifelse(
                # 情况2a：点击同一柱子 → 取消选中
                equalto(var_ref("clicked"), var_ref("sel")),
                [setvar("sel", lit(""))],
                # 情况2b：点击不同柱子 → 尝试移动
                [
                    get_stack_len("sel",     "src_len"),
                    get_stack_len("clicked", "dest_len"),
                    get_stack_top("sel",     "src_len",  "src_top"),
                    # 如果目标栈非空，取顶部盘号；否则设为7（任何盘都能移入空栈）
                    ifelse(
                        isgreater(var_ref("dest_len"), lit("0")),
                        [get_stack_top("clicked", "dest_len", "dest_top")],
                        [setvar("dest_top", lit("7"))]
                    ),
                    # 合法性校验：dest_top > src_top（更大的盘才能压在下面）
                    ifelse(
                        isgreater(var_ref("dest_top"), var_ref("src_top")),
                        valid_move_seq,
                        [setvar("sel", lit(""))]  # 非法移动：重置选中
                    )
                ]
            )]
        )
    ]
    return make_fragment("WhenReceiveMessage", [lit("do_click")], children)


def build_frag_game_win() -> dict:
    """ctrl_game: WhenReceiveMessage(game_win) → 胜利处理（空体）"""
    return make_fragment("WhenReceiveMessage", [lit("game_win")], [])


def build_frag_base_click(col_letter: str) -> dict:
    """底座A/B/C 点击 → 设置 clicked 并广播 do_click"""
    children = [
        setvar("clicked", lit(col_letter)),
        broadcast_wait("do_click")
    ]
    return make_fragment("WhenThisSpriteClicked", [lit("this sprite")], children)


def build_frag_disc_anim(disc_num: str) -> dict:
    """盘x: WhenReceiveMessage(do_anim) → 执行三段滑动动画"""
    children = [
        ifelse(
            equalto(var_ref("moving_disc"), lit(disc_num)),
            [
                # Step1: 升起到 h_lift 高度
                glide("0.4", lit("0"), var_ref("h_lift"),  var_ref("src_z")),
                # Step2: 横移到目标柱上方
                glide("0.4", lit("0"), var_ref("h_lift"),  var_ref("dest_z")),
                # Step3: 落下到目标位置
                glide("0.4", lit("0"), var_ref("final_h"), var_ref("dest_z")),
            ],
            []
        )
    ]
    return make_fragment("WhenReceiveMessage", [lit("do_anim")], children)


# ============================================================
# 场景节点构建
# ============================================================

def gen_id() -> str:
    return uuid.uuid4().hex


def make_blockscript(fragments: list) -> dict:
    return {
        "type": "BlockScript",
        "id": gen_id(),
        "props": {"Name": "BlockScript", "EditMode": 0},
        "fragments": fragments
    }


def make_meshpart(
    name: str, asset_id: int, position: list,
    size: list = None, visible: bool = True,
    anchor: str = None, fragments: list = None
) -> dict:
    props: dict = {
        "Name":     name,
        "EditMode": 0,
        "AssetId":  asset_id,
        "Position": position,
        "Visible":  visible
    }
    if size is not None:
        # Size 是 vector3（非均匀缩放），Scale 是单 float（均匀缩放）
        props["Size"] = size
    if anchor is not None:
        props["Anchor"] = anchor

    node = {
        "type":     "MeshPart",
        "id":       gen_id(),
        "props":    props,
        "children": []
    }
    if fragments:
        node["children"].append(make_blockscript(fragments))
    return node


# ============================================================
# 构建完整 workspace
# ============================================================

def build_workspace() -> dict:
    # --- props2（全局变量）---
    props2 = {
        "#EVENT": {
            "type": "SimpleList",
            "value": ["do_click", "do_anim", "game_win"]
        },
        "stackA":       {"type": "SimpleList", "value": []},
        "stackB":       {"type": "SimpleList", "value": []},
        "stackC":       {"type": "SimpleList", "value": []},
        "sel":          {"type": "Simple", "value": ""},
        "clicked":      {"type": "Simple", "value": ""},
        "src_len":      {"type": "Simple", "value": "0"},
        "dest_len":     {"type": "Simple", "value": "0"},
        "src_top":      {"type": "Simple", "value": "0"},
        "dest_top":     {"type": "Simple", "value": "0"},
        "moving_disc":  {"type": "Simple", "value": "0"},
        "dest_slot":    {"type": "Simple", "value": "0"},
        "move_count":   {"type": "Simple", "value": "0"},
        "src_z":        {"type": "Simple", "value": "0"},
        "dest_z":       {"type": "Simple", "value": "0"},
        "final_h":      {"type": "Simple", "value": "0"},
        "h_lift":       {"type": "Simple", "value": "2.5"},
    }

    # --- services 文件夹 ---
    services_folder = {
        "type": "Folder",
        "id":   gen_id(),
        "props": {"Name": "services", "EditMode": 0},
        "children": [
            {
                "type":  "BlockService",
                "id":    gen_id(),
                "props": {
                    "Name":     "Blocks",
                    "EditMode": 0,
                    "Modules":  [
                        "motion", "looks", "events", "control", "sound",
                        "sensing", "operators", "variable", "myblocks",
                        "music", "magic", "physics", "stage", "ui", "animation"
                    ]
                }
            },
            {
                "type":  "SkyboxService",
                "id":    gen_id(),
                "props": {
                    "Name":         "Skybox",
                    "EditMode":     0,
                    "TimeOfDay":    "0",
                    "AmbientColor": "#00000000",
                    "SunSize":      "0.2",
                    "SunColor":     "#00000000",
                    "SunBrightness":"0.5",
                    "MoonSize":     "0.2",
                    "MoonColor":    "#00000000",
                    "MoonBrightness":"0.2",
                    "StarCount":    3000
                }
            },
            {
                "type":  "CameraService",
                "id":    gen_id(),
                "props": {"Name": "Camera", "EditMode": 0, "Current": "Camera45"},
                "children": [
                    {
                        "type":      "BlockScript",
                        "id":        gen_id(),
                        "props":     {"Name": "BlockScript", "EditMode": 0},
                        "fragments": [build_frag_camera_start()]
                    }
                ]
            }
        ]
    }

    # --- ctrl_cam（不可见，相机跟随目标，垂直居中 y=1.15）---
    ctrl_cam = make_meshpart("ctrl_cam", 10548, [0, 1.15, 0], visible=False)

    # --- ctrl_game（不可见，携带游戏逻辑脚本）---
    ctrl_game = make_meshpart(
        "ctrl_game", 10548, [0, 0.27, 3], visible=False,
        fragments=[
            build_frag_game_start(),
            build_frag_do_click(),
            build_frag_game_win(),
        ]
    )

    # --- 三根柱子（AssetId=13355，Size=vector3 指定非均匀尺寸）---
    col_A = make_meshpart("柱A", 13355, [0.3, 0.27, -2.5], size=[0.15, 0.3, 0.15])
    col_B = make_meshpart("柱B", 13355, [0.3, 0.27,  0.0], size=[0.15, 0.3, 0.15])
    col_C = make_meshpart("柱C", 13355, [0.3, 0.27,  2.5], size=[0.15, 0.3, 0.15])

    # --- 三个底座（AssetId=17955，可点击）---
    base_A = make_meshpart("底座A", 17955, [0, 0.27, -2.5],
                           size=[0.3, 0.1, 1.8], anchor="bottom",
                           fragments=[build_frag_base_click("A")])
    base_B = make_meshpart("底座B", 17955, [0, 0.27,  0.0],
                           size=[0.3, 0.1, 1.8], anchor="bottom",
                           fragments=[build_frag_base_click("B")])
    base_C = make_meshpart("底座C", 17955, [0, 0.27,  2.5],
                           size=[0.3, 0.1, 1.8], anchor="bottom",
                           fragments=[build_frag_base_click("C")])

    # --- 6 个盘子（从大到小，初始全在 A 柱）---
    disc_specs = [
        # (名称, 位置,              尺寸(Size),          编号)
        ("盘6", [0, 0.355, -2.5], [0.3, 0.3, 1.7], "6"),
        ("盘5", [0, 0.610, -2.5], [0.3, 0.3, 1.4], "5"),
        ("盘4", [0, 0.865, -2.5], [0.3, 0.3, 1.1], "4"),
        ("盘3", [0, 1.120, -2.5], [0.3, 0.3, 0.8], "3"),
        ("盘2", [0, 1.375, -2.5], [0.3, 0.3, 0.6], "2"),
        ("盘1", [0, 1.630, -2.5], [0.3, 0.3, 0.4], "1"),
    ]
    discs = [
        make_meshpart(name, 17955, pos, size=sz, anchor="bottom",
                      fragments=[build_frag_disc_anim(num)])
        for name, pos, sz, num in disc_specs
    ]

    now_ts = int(datetime.now().timestamp())
    return {
        "name":      "汉诺塔挑战",
        "desc":      "",
        "icon":      "",
        "author":    "",
        "created":   now_ts,
        "modified":  now_ts,
        "type":      3,
        "version":   3,
        "stageType": 0,
        "scene": {
            "type": "Scene",
            "id":   gen_id(),
            "props": {
                "Name":        "Scene",
                "EditMode":    0,
                "BoundsCenter": ["0", "1.5", "0"],
                "BoundsSize":   ["6", "4", "8"],
                "AssetId":     28746
            },
            "props2":   props2,
            "children": [
                services_folder,
                ctrl_cam,
                ctrl_game,
                col_A, col_B, col_C,
                base_A, base_B, base_C,
                *discs
            ]
        }
    }


# ============================================================
# Main
# ============================================================

def main() -> None:
    WORKDIR.mkdir(parents=True, exist_ok=True)

    # 删除旧 .ws 文件
    for old_ws in WORKDIR.glob("*.ws"):
        old_ws.unlink()
        print(f"[build] Removed old: {old_ws.name}")

    # 构建并写入 workspace
    ws_data = build_workspace()
    WS_PATH.write_text(
        json.dumps(ws_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"[build] Workspace saved: {WS_FILENAME}")

    # 更新 solution.json（确保 init == SOLUTION_UID，且 N11 UUID 匹配）
    sol_path = WORKDIR / "solution.json"
    if sol_path.exists():
        sol = json.loads(sol_path.read_text(encoding="utf-8"))
    else:
        sol = {"projects": [{}]}
    sol["init"]     = SOLUTION_UID
    sol["name"]     = "汉诺塔挑战"
    sol["modified"] = int(datetime.now().timestamp())
    if sol.get("projects"):
        proj = sol["projects"][0]
        # 参考包的 solutionUid 作为 path 前缀
        proj["file"] = f"pangu3d/universe/develop/611146016258785288/{WS_FILENAME}"
        proj["name"] = "汉诺塔挑战"
    sol_path.write_text(json.dumps(sol, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[build] solution.json updated: init={SOLUTION_UID}")

    # 更新 export_info.json（solutionUid 必须等于 solution.init）
    ei_path = WORKDIR / "export_info.json"
    if ei_path.exists():
        ei = json.loads(ei_path.read_text(encoding="utf-8"))
    else:
        ei = {}
    ei["solutionUid"] = SOLUTION_UID
    ei_path.write_text(json.dumps(ei, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[build] export_info.json updated: solutionUid={SOLUTION_UID}")

    # 统计信息
    n_children = len(ws_data["scene"]["children"])
    print(f"[build] Scene children: {n_children}")
    print(f"[build] Done! WS path: {WS_PATH}")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
