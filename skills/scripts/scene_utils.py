"""
scene_utils.py - 场景树工具（MCP 覆盖不到的 .ws 场景节点操作）

背景（2026-04-23）：
  hetu-mcp 的操作粒度在 BlockScript 内部（fragment / myblock / block），
  对 **场景树节点**（Character / MeshPart / Effect / Folder 的 `children` / `props`）
  它不管。本模块封装这些典型操作。

设计约定：
  - 所有函数都是 **纯函数**：返回一个新的 data 对象，不会原地修改入参。
    用法统一写 `data = scene_utils.xxx(data, ...)`，和 MCP 的函数式 API 风格一致。
  - **坐标单位：米**（与 JSON .ws 存储一致；编辑器 UI 的 "厘米" 是显示层 × 100）。
    详见 `.cursor/skills/level-common/presets.md` 零节"字段单位对照表"。

提供的函数：
  - find_node(data, name, type=None)           # 树搜索
  - set_character_position(data, name, x,y,z)  # 改位置（米）
  - set_character_scale(data, name, scale)     # 改缩放倍数
  - set_character_size(data, name, w,h,d)      # 改尺寸（米）
  - attach_effect(data, character_name, effect_props)  # 给角色挂 Effect 子节点
  - duplicate_character(data, src_name, new_name, new_pos=None)
  - hide_node(data, name) / show_node(data, name)      # 改 Visible
  - set_node_prop(data, name, key, value)      # 通用改 props 字段
"""
from __future__ import annotations

import copy
import uuid
from typing import Any, Callable, Optional


Data = dict[str, Any]


def _scene(data: Data) -> Data:
    if "scene" not in data:
        raise ValueError("data.scene not found. Did you pass the full .ws dict?")
    return data["scene"]


def _walk(node: Data, fn: Callable[[Data], None]) -> None:
    if isinstance(node, dict):
        fn(node)
        for c in node.get("children", []) or []:
            _walk(c, fn)


def find_node(data: Data, name: str, type: Optional[str] = None) -> Optional[Data]:
    """在 scene 树里按 Name 查找节点。返回**原始引用**（未复制）。若要修改请走 copy."""
    found = [None]

    def visit(n: Data) -> None:
        if found[0] is not None:
            return
        props = n.get("props") or {}
        if props.get("Name") == name and (type is None or n.get("type") == type):
            found[0] = n

    _walk(_scene(data), visit)
    return found[0]


def _ensure_str_xyz(x, y, z) -> list[str]:
    return [str(x), str(y), str(z)]


def set_character_position(data: Data, name: str, x: float, y: float, z: float) -> Data:
    """
    设置角色/物件的 Position（单位：米）。

    返回新的 data（deep copy 后修改）。
    """
    data = copy.deepcopy(data)
    n = find_node(data, name)
    if n is None:
        raise ValueError(f"node not found: {name}")
    props = n.setdefault("props", {})
    props["Position"] = _ensure_str_xyz(x, y, z)
    return data


def set_character_scale(data: Data, name: str, scale: float) -> Data:
    """设置 Scale（倍数，1.0 = 原始）。同时更新 Scale 字段（若缺则创建）。"""
    data = copy.deepcopy(data)
    n = find_node(data, name)
    if n is None:
        raise ValueError(f"node not found: {name}")
    n.setdefault("props", {})["Scale"] = [str(scale), str(scale), str(scale)]
    return data


def set_character_size(data: Data, name: str, w: float, h: float, d: float) -> Data:
    """设置 Size（单位：米）。"""
    data = copy.deepcopy(data)
    n = find_node(data, name)
    if n is None:
        raise ValueError(f"node not found: {name}")
    n.setdefault("props", {})["Size"] = _ensure_str_xyz(w, h, d)
    return data


def set_node_prop(data: Data, name: str, key: str, value: Any) -> Data:
    """通用：设置 props 里的任意字段。"""
    data = copy.deepcopy(data)
    n = find_node(data, name)
    if n is None:
        raise ValueError(f"node not found: {name}")
    n.setdefault("props", {})[key] = value
    return data


def hide_node(data: Data, name: str) -> Data:
    return set_node_prop(data, name, "Visible", False)


def show_node(data: Data, name: str) -> Data:
    return set_node_prop(data, name, "Visible", True)


def attach_effect(
    data: Data,
    character_name: str,
    effect_name: str,
    asset_id: str | int,
    visible: bool = True,
    loop: bool = False,
    extra_props: Optional[dict] = None,
) -> Data:
    """
    给指定角色挂一个 Effect 子节点。Effect 的 Name 将成为角色可用的动画名，
    后续用 `PlayAnimation(effect_name)` 触发。

    Effect 典型 props:
      Name / AssetId / Visible / Loop / Scale
    """
    data = copy.deepcopy(data)
    n = find_node(data, character_name)
    if n is None:
        raise ValueError(f"character not found: {character_name}")
    props = {
        "Name":    effect_name,
        "AssetId": str(asset_id),
        "Visible": bool(visible),
        "Loop":    bool(loop),
    }
    if extra_props:
        props.update(extra_props)
    effect_node = {
        "type":     "Effect",
        "id":       str(uuid.uuid4()),
        "props":    props,
        "children": [],
    }
    n.setdefault("children", []).append(effect_node)
    return data


def duplicate_character(
    data: Data,
    src_name: str,
    new_name: str,
    new_pos: Optional[tuple[float, float, float]] = None,
) -> Data:
    """
    深拷贝一个角色节点，改 Name / id / （可选）Position。

    常用于"同款物资箱 5 个、I-II-III-IV-V"这类结构化复制。
    """
    data = copy.deepcopy(data)
    src = find_node(data, src_name)
    if src is None:
        raise ValueError(f"source character not found: {src_name}")
    dup = copy.deepcopy(src)
    dup["id"] = str(uuid.uuid4())
    dup.setdefault("props", {})["Name"] = new_name
    if new_pos is not None:
        dup["props"]["Position"] = _ensure_str_xyz(*new_pos)

    scene = _scene(data)
    parent_children = scene.setdefault("children", [])

    def find_parent(container: Data, target_id: str) -> Optional[list]:
        kids = container.get("children", []) or []
        for k in kids:
            if k.get("id") == target_id:
                return kids
            if isinstance(k, dict):
                hit = find_parent(k, target_id)
                if hit is not None:
                    return hit
        return None

    siblings = find_parent(scene, src["id"]) or parent_children
    siblings.append(dup)
    return data


def remove_node(data: Data, name: str) -> Data:
    """从 scene 树里移除第一个匹配 Name 的节点。"""
    data = copy.deepcopy(data)

    def prune(container: Data) -> bool:
        kids = container.get("children", []) or []
        for i, k in enumerate(list(kids)):
            props = k.get("props") or {}
            if props.get("Name") == name:
                del kids[i]
                return True
            if prune(k):
                return True
        return False

    prune(_scene(data))
    return data


def list_characters(data: Data) -> list[dict]:
    """返回 scene 内所有 Character 的 (name, position, scale)，调试用。"""
    out: list[dict] = []

    def visit(n: Data) -> None:
        if n.get("type") == "Character":
            p = n.get("props", {})
            out.append({
                "name":     p.get("Name"),
                "position": p.get("Position"),
                "scale":    p.get("Scale"),
                "size":     p.get("Size"),
            })

    _walk(_scene(data), visit)
    return out
