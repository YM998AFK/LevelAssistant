from __future__ import annotations

import asyncio
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SERVER_PY = PACKAGE_ROOT / "server.py"
REFERENCE_ROOT = ROOT / "reference"
OUTPUT_DIR = ROOT / "output"
STATS_OUTPUT_MD = OUTPUT_DIR / "REFERENCE_WS_MCP_REPORT.md"
SCREENPLAY_OUTPUT_MD = OUTPUT_DIR / "REFERENCE_WS_SCREENPLAY.md"
LEGACY_REPORT_MD = REFERENCE_ROOT / "REFERENCE_WS_MCP_REPORT.md"

BLOCK_DEFINES = [
    "PlayDialogueGroup",
    "WhenReceiveMessage",
    "BroadcastMessage",
    "BroadcastMessageAndWait",
    "TransitToCameraPreset",
    "GlideSecsToPosition3DAndSetRotation",
    "SetCameraFOV",
    "ChangeCameraFOV",
    "CameraFollow",
    "CameraLookAt",
    "SetQuestText",
    "SetQuestStyle",
    "ShowQuest",
    "HideQuest",
    "CompleteQuest",
]

TRIGGER_DEFINES = {
    "WhenGameStarts",
    "WhenReceiveMessage",
    "WhenClicked",
    "WhenTapped",
}

CAMERA_ACTION_DEFINES = {
    "TransitToCameraPreset",
    "GlideSecsToPosition3DAndSetRotation",
    "SetCameraFOV",
    "ChangeCameraFOV",
    "CameraFollow",
    "CameraLookAt",
}


def text_from_result(result: Any) -> str:
    return "".join(item.text for item in result.content if getattr(item, "type", None) == "text")


async def call_json(session: ClientSession, tool: str, args: dict[str, Any]) -> Any:
    result = await session.call_tool(tool, args)
    return json.loads(text_from_result(result))


def shorten(text: str, limit: int = 36) -> str:
    normalized = " ".join(str(text).split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1] + "…"


def strip_markup(text: str) -> str:
    raw = re.sub(r"\{[^{}]+\}", "", str(text))
    return " ".join(raw.split())


def unique_preserve(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def block_param_value(block: dict[str, Any], index: int, section_index: int = 0) -> str:
    sections = block.get("sections", [])
    if not isinstance(sections, list) or len(sections) <= section_index:
        return ""

    section = sections[section_index]
    if not isinstance(section, dict):
        return ""

    params = section.get("params", [])
    if not isinstance(params, list) or len(params) <= index:
        return ""

    entry = params[index]
    if not isinstance(entry, dict):
        return ""

    value = entry.get("val")
    if isinstance(value, dict):
        return value.get("define", "")
    if value is None:
        return ""
    return str(value)


def walk_module_tree(workspace_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    scripts: dict[str, dict[str, Any]] = {}

    def walk(node: Any, path: str, parent: dict[str, Any] | None) -> None:
        if not isinstance(node, dict):
            return

        if node.get("type") == "BlockScript" or any(
            key in node for key in ("fragments", "myblocks", "uiState")
        ):
            script_id = str(node.get("id", path))
            owner = parent or {}
            owner_props = owner.get("props", {}) if isinstance(owner.get("props"), dict) else {}
            fragments = node.get("fragments", [])
            fragment_map = {
                index: fragment
                for index, fragment in enumerate(fragments)
                if isinstance(fragment, dict)
            }
            scripts[script_id] = {
                "source": script_id,
                "script": node,
                "path": path,
                "owner_type": owner.get("type", "Unknown"),
                "owner_id": owner.get("id", ""),
                "owner_name": owner_props.get("Name", ""),
                "fragments": fragment_map,
                "fragment_meta": {
                    index: describe_fragment(fragment)
                    for index, fragment in fragment_map.items()
                },
            }
            return

        children = node.get("children", [])
        if isinstance(children, list):
            for index, child in enumerate(children):
                walk(child, f"{path}.children[{index}]", node)

    for root_key in ("scene", "agents", "assets"):
        root_node = workspace_data.get(root_key)
        if isinstance(root_node, dict):
            walk(root_node, root_key, None)

    return scripts


def describe_fragment(fragment: dict[str, Any]) -> dict[str, str]:
    head = fragment.get("head", {})
    if not isinstance(head, dict):
        return {"head_define": "Unknown", "trigger": "Unknown"}

    head_define = str(head.get("define", "Unknown"))
    if head_define == "WhenReceiveMessage":
        trigger = f"WhenReceiveMessage({block_param_value(head, 0)})"
    elif head_define == "WhenGameStarts":
        trigger = "WhenGameStarts"
    elif head_define == "WhenClicked":
        trigger = "WhenClicked"
    elif head_define == "WhenTapped":
        trigger = "WhenTapped"
    else:
        trigger = head_define

    return {
        "head_define": head_define,
        "trigger": trigger,
    }


def owner_label(script_context: dict[str, Any] | None) -> str:
    if not script_context:
        return "Unknown owner"
    owner_type = script_context.get("owner_type") or "Unknown"
    owner_name = script_context.get("owner_name") or "(unnamed)"
    return f"{owner_type}:{owner_name}"


def owner_human_label(script_context: dict[str, Any] | None) -> str:
    if not script_context:
        return "未知对象"
    owner_type = script_context.get("owner_type") or "Unknown"
    owner_name = script_context.get("owner_name") or "(unnamed)"
    return f"{owner_type}《{owner_name}》"


def extract_fragment_index(path: str) -> int | None:
    match = re.search(r"\.fragments\[(\d+)\]\.head", path)
    if not match:
        return None
    return int(match.group(1))


def resolve_hit_fragment(
    hit: dict[str, Any],
    scripts: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any] | None, int | None, dict[str, Any] | None]:
    source = str(hit.get("source", ""))
    script_context = scripts.get(source)
    fragment_index = extract_fragment_index(str(hit.get("path", "")))
    fragment = None
    if script_context is not None and fragment_index is not None:
        fragment = script_context.get("fragments", {}).get(fragment_index)
    return script_context, fragment_index, fragment


def hit_context(hit: dict[str, Any], scripts: dict[str, dict[str, Any]]) -> str:
    script_context, fragment_index, _ = resolve_hit_fragment(hit, scripts)
    fragment_meta = {}
    if script_context is not None and fragment_index is not None:
        fragment_meta = script_context.get("fragment_meta", {}).get(fragment_index, {})
    trigger = fragment_meta.get("trigger", "")
    if trigger:
        return f"{owner_label(script_context)} via {trigger}"
    return owner_label(script_context)


def flatten_next_chain(block: dict[str, Any]) -> list[dict[str, Any]]:
    chain: list[dict[str, Any]] = []
    current: Any = block
    while isinstance(current, dict):
        chain.append(current)
        current = current.get("next")
    return chain


def fragment_action_blocks(fragment: dict[str, Any]) -> list[dict[str, Any]]:
    head = fragment.get("head", {})
    if not isinstance(head, dict):
        return []

    head_define = head.get("define")
    if head_define in TRIGGER_DEFINES:
        actions: list[dict[str, Any]] = []
        for section in head.get("sections", []):
            if not isinstance(section, dict):
                continue
            children = section.get("children", [])
            if not isinstance(children, list):
                continue
            for child in children:
                if isinstance(child, dict):
                    actions.extend(flatten_next_chain(child))
        return actions

    return flatten_next_chain(head)


def describe_camera_action(block: dict[str, Any]) -> str:
    define = str(block.get("define", ""))
    if define == "GlideSecsToPosition3DAndSetRotation":
        secs = block_param_value(block, 0)
        x = block_param_value(block, 1)
        y = block_param_value(block, 2)
        z = block_param_value(block, 3)
        return f"镜头在 {secs} 秒内移动到 ({x}, {y}, {z})"
    if define == "SetCameraFOV":
        return f"设置镜头 FOV 为 {block_param_value(block, 0)}"
    if define == "ChangeCameraFOV":
        return f"调整镜头 FOV {block_param_value(block, 0)}"
    if define == "CameraFollow":
        target = block_param_value(block, 0)
        return f"镜头跟随 {target}"
    if define == "CameraLookAt":
        target = block_param_value(block, 0)
        return f"镜头看向 {target}"
    return define


def summarize_fragment_actions(fragment: dict[str, Any]) -> dict[str, Any]:
    summary = {
        "dialogue_groups": [],
        "transits": [],
        "camera_actions": [],
        "broadcasts": [],
        "broadcast_waits": [],
        "defines": [],
    }

    for block in fragment_action_blocks(fragment):
        define = str(block.get("define", ""))
        if not define:
            continue

        summary["defines"].append(define)

        if define == "PlayDialogueGroup":
            summary["dialogue_groups"].append(block_param_value(block, 0))
        elif define == "TransitToCameraPreset":
            summary["transits"].append(
                {
                    "preset": block_param_value(block, 0),
                    "transition": block_param_value(block, 1) or "none",
                    "easing": block_param_value(block, 2) or "none",
                }
            )
        elif define in CAMERA_ACTION_DEFINES - {"TransitToCameraPreset"}:
            summary["camera_actions"].append(describe_camera_action(block))
        elif define == "BroadcastMessage":
            message = block_param_value(block, 0)
            if message:
                summary["broadcasts"].append(message)
        elif define == "BroadcastMessageAndWait":
            message = block_param_value(block, 0)
            if message:
                summary["broadcast_waits"].append(message)

    return summary


def flatten_define_chain(block: dict[str, Any], limit: int = 8) -> list[str]:
    defines: list[str] = []
    current: Any = block
    while isinstance(current, dict) and len(defines) < limit:
        define = current.get("define")
        if isinstance(define, str) and define:
            defines.append(define)

        sections = current.get("sections", [])
        if isinstance(sections, list):
            for section in sections:
                if not isinstance(section, dict):
                    continue
                children = section.get("children", [])
                if isinstance(children, list):
                    for child in children:
                        if isinstance(child, dict):
                            child_define = child.get("define")
                            if isinstance(child_define, str) and child_define:
                                defines.append(child_define)
                                if len(defines) >= limit:
                                    return defines[:limit]

        current = current.get("next")
    return defines[:limit]


def collect_dialogues(workspace_data: dict[str, Any]) -> list[dict[str, Any]]:
    dialogues = workspace_data.get("dialogues", {}).get("DialogueGroups", [])
    if isinstance(dialogues, list):
        return [group for group in dialogues if isinstance(group, dict)]
    return []


def dialogue_map(dialogues: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for group in dialogues:
        name = group.get("name")
        if isinstance(name, str) and name:
            result[name] = group
    return result


def collect_dialogue_speakers(dialogues: list[dict[str, Any]]) -> list[str]:
    speakers: list[str] = []
    for group in dialogues:
        items = group.get("items", [])
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            speaker = item.get("who")
            if isinstance(speaker, str) and speaker:
                speakers.append(speaker)
    return unique_preserve(speakers)


def collect_quests(workspace_data: dict[str, Any]) -> list[dict[str, str]]:
    quests: list[dict[str, str]] = []

    def walk(node: Any) -> None:
        if not isinstance(node, dict):
            return
        if node.get("type") == "QuestObject":
            props = node.get("props", {}) if isinstance(node.get("props"), dict) else {}
            quests.append(
                {
                    "name": str(props.get("Name", "(unnamed)")),
                    "title": str(props.get("Title", "")),
                    "style": str(props.get("StyleName", "")),
                    "content": str(props.get("Content", "")),
                }
            )

        children = node.get("children", [])
        if isinstance(children, list):
            for child in children:
                walk(child)

    for root_key in ("scene", "agents", "assets"):
        root = workspace_data.get(root_key)
        if isinstance(root, dict):
            walk(root)

    return quests


def collect_scene_event_names(workspace_data: dict[str, Any]) -> list[str]:
    scene = workspace_data.get("scene", {})
    if not isinstance(scene, dict):
        return []
    props2 = scene.get("props2", {})
    if not isinstance(props2, dict):
        return []
    event_meta = props2.get("#EVENT", {})
    if not isinstance(event_meta, dict):
        return []
    values = event_meta.get("value", [])
    if not isinstance(values, list):
        return []
    return [str(value) for value in values if value not in ("", None)]


def collect_dialogue_beats(
    scripts: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    beats: list[dict[str, Any]] = []
    used_groups: list[str] = []

    for script_context in scripts.values():
        for fragment_index in sorted(script_context.get("fragments", {})):
            fragment = script_context["fragments"][fragment_index]
            summary = summarize_fragment_actions(fragment)
            if not summary["dialogue_groups"]:
                continue

            meta = script_context.get("fragment_meta", {}).get(fragment_index, {})
            beats.append(
                {
                    "owner": owner_human_label(script_context),
                    "trigger": meta.get("trigger", "Unknown"),
                    "dialogue_groups": summary["dialogue_groups"],
                    "transits": summary["transits"],
                    "camera_actions": summary["camera_actions"],
                    "broadcasts": summary["broadcasts"],
                    "broadcast_waits": summary["broadcast_waits"],
                }
            )
            used_groups.extend(summary["dialogue_groups"])

    return beats, used_groups


def collect_camera_only_beats(
    scripts: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    beats: list[dict[str, Any]] = []

    for script_context in scripts.values():
        for fragment_index in sorted(script_context.get("fragments", {})):
            fragment = script_context["fragments"][fragment_index]
            summary = summarize_fragment_actions(fragment)
            if summary["dialogue_groups"]:
                continue
            if not summary["transits"] and not summary["camera_actions"]:
                continue

            meta = script_context.get("fragment_meta", {}).get(fragment_index, {})
            beats.append(
                {
                    "owner": owner_human_label(script_context),
                    "trigger": meta.get("trigger", "Unknown"),
                    "transits": summary["transits"],
                    "camera_actions": summary["camera_actions"],
                    "broadcasts": summary["broadcasts"],
                    "broadcast_waits": summary["broadcast_waits"],
                }
            )

    return beats


def summarize_dialogues(dialogues: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for group in dialogues:
        items = group.get("items", [])
        branches = group.get("branches", [])
        speakers = unique_preserve(
            [
                str(item.get("who", ""))
                for item in items
                if isinstance(item, dict) and isinstance(item.get("who"), str) and item.get("who")
            ]
        )
        preview = ""
        if isinstance(items, list) and items:
            first = items[0]
            if isinstance(first, dict):
                preview = shorten(strip_markup(str(first.get("content", ""))), 40)

        line = (
            f"- `{group.get('name', '(unnamed)')}`: {len(items) if isinstance(items, list) else 0} 句对白，"
            f"角色 {', '.join(speakers) if speakers else '未标注'}，"
            f"分支 {len(branches) if isinstance(branches, list) else 0}"
        )
        if preview:
            line += f"，首句「{preview}」"
        lines.append(line)
    return lines


def summarize_dialogue_uses(
    play_hits: list[dict[str, Any]],
    scripts: dict[str, dict[str, Any]],
) -> list[str]:
    usage_by_group: dict[str, list[str]] = defaultdict(list)
    for hit in play_hits:
        block = hit.get("block", {})
        if not isinstance(block, dict):
            continue
        group_name = block_param_value(block, 0) or "(empty)"
        usage_by_group[group_name].append(hit_context(hit, scripts))

    lines: list[str] = []
    for group_name in sorted(usage_by_group):
        contexts = unique_preserve(usage_by_group[group_name])
        lines.append(f"- `{group_name}`: {'; '.join(contexts)}")
    return lines


def summarize_camera_presets(cameras: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for camera in cameras:
        if not isinstance(camera, dict):
            continue
        position = camera.get("position", [])
        pos_text = ", ".join(str(value) for value in position[:3]) if isinstance(position, list) else ""
        line = f"- `{camera.get('name', '(unnamed)')}`: FOV {camera.get('fov', '')}"
        if pos_text:
            line += f"，位置 [{pos_text}]"
        lines.append(line)
    return lines


def summarize_camera_transits(
    hits: list[dict[str, Any]],
    scripts: dict[str, dict[str, Any]],
) -> list[str]:
    lines: list[str] = []
    for hit in hits:
        block = hit.get("block", {})
        if not isinstance(block, dict):
            continue
        preset = block_param_value(block, 0) or "(empty)"
        transition = block_param_value(block, 1) or "none"
        easing = block_param_value(block, 2) or "none"
        lines.append(
            f"- `{preset}`: {hit_context(hit, scripts)}，transition={transition}，easing={easing}"
        )
    return lines


def summarize_camera_myblocks(
    myblocks: list[dict[str, Any]],
    scripts: dict[str, dict[str, Any]],
) -> list[str]:
    del myblocks
    lines: list[str] = []
    for script_context in scripts.values():
        if script_context.get("owner_type") != "CameraService":
            continue
        script = script_context.get("script", {})
        if not isinstance(script, dict):
            continue

        for myblock in script.get("myblocks", []):
            if not isinstance(myblock, dict):
                continue
            fragment = myblock.get("fragment", {})
            head = fragment.get("head", {}) if isinstance(fragment, dict) else {}
            chain = " -> ".join(flatten_define_chain(head))
            lines.append(
                f"- `{myblock.get('displayName') or myblock.get('name')}`: {chain or '(empty)'}"
            )

    return lines


def summarize_direct_camera_actions(
    hits_by_define: dict[str, list[dict[str, Any]]],
    scripts: dict[str, dict[str, Any]],
) -> list[str]:
    lines: list[str] = []
    for define in sorted(CAMERA_ACTION_DEFINES - {"TransitToCameraPreset"}):
        hits = hits_by_define.get(define, [])
        if not hits:
            continue
        contexts = unique_preserve([hit_context(hit, scripts) for hit in hits])
        lines.append(f"- `{define}`: {len(hits)} 次，出现在 {'; '.join(contexts[:6])}")
    return lines


def summarize_quests(quests: list[dict[str, str]]) -> list[str]:
    lines: list[str] = []
    for quest in quests:
        lines.append(
            f"- `{quest['name']}`: 标题「{quest['title']}」，样式 `{quest['style']}`，内容「{shorten(quest['content'], 48)}」"
        )
    return lines


def summarize_quest_actions(
    hits_by_define: dict[str, list[dict[str, Any]]],
    scripts: dict[str, dict[str, Any]],
) -> list[str]:
    lines: list[str] = []
    for define in ("SetQuestText", "SetQuestStyle", "ShowQuest", "HideQuest", "CompleteQuest"):
        hits = hits_by_define.get(define, [])
        if not hits:
            continue
        contexts = unique_preserve([hit_context(hit, scripts) for hit in hits])
        lines.append(f"- `{define}`: {len(hits)} 次，出现在 {'; '.join(contexts[:6])}")
    return lines


def summarize_message_graph(
    when_hits: list[dict[str, Any]],
    broadcast_hits: list[dict[str, Any]],
    broadcast_wait_hits: list[dict[str, Any]],
    scripts: dict[str, dict[str, Any]],
) -> list[str]:
    receivers: dict[str, list[str]] = defaultdict(list)
    broadcasters: dict[str, list[str]] = defaultdict(list)

    for hit in when_hits:
        block = hit.get("block", {})
        if not isinstance(block, dict):
            continue
        message = block_param_value(block, 0)
        if not message:
            continue
        receivers[message].append(hit_context(hit, scripts))

    for bucket_name, hits in (
        ("BroadcastMessage", broadcast_hits),
        ("BroadcastMessageAndWait", broadcast_wait_hits),
    ):
        for hit in hits:
            block = hit.get("block", {})
            if not isinstance(block, dict):
                continue
            message = block_param_value(block, 0)
            if not message:
                continue
            broadcasters[message].append(f"{hit_context(hit, scripts)} via {bucket_name}")

    all_messages = sorted(set(receivers) | set(broadcasters))
    lines: list[str] = []
    for message in all_messages:
        senders = ", ".join(unique_preserve(broadcasters.get(message, []))) or "无"
        listeners = ", ".join(unique_preserve(receivers.get(message, []))) or "无"
        lines.append(f"- `{message}`: 广播方 {senders}；接收方 {listeners}")
    return lines


def summarize_scene_elements(stats: dict[str, Any]) -> list[str]:
    module_types = stats.get("module_types", {})
    if not isinstance(module_types, dict):
        return []

    lines: list[str] = []
    for module_type, count in sorted(module_types.items()):
        if module_type in {
            "Folder",
            "BlockScript",
            "Picture",
            "Effect",
            "Sound",
            "Music",
            "BlockService",
            "SkyboxService",
        }:
            continue
        lines.append(f"- `{module_type}`: {count}")
    return lines


def scene_element_sentence(stats: dict[str, Any]) -> str:
    module_types = stats.get("module_types", {})
    if not isinstance(module_types, dict):
        return "未识别到场景元素。"

    parts: list[str] = []
    for module_type, count in sorted(module_types.items()):
        if module_type in {
            "Folder",
            "BlockScript",
            "Picture",
            "Effect",
            "Sound",
            "Music",
            "BlockService",
            "SkyboxService",
        }:
            continue
        parts.append(f"{module_type} x{count}")

    if not parts:
        return "未识别到场景元素。"
    return "、".join(parts)


def render_dialogue_group(group: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    items = group.get("items", [])
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue
            speaker = str(item.get("who", "") or "旁白")
            content = strip_markup(str(item.get("content", "")))
            if not content:
                continue
            lines.append(f"{speaker}: {content}")

    if not lines:
        lines.append("（该对白组没有可读对白内容）")

    menu = group.get("menu", [])
    if isinstance(menu, list) and menu:
        menu_items = [str(item) for item in menu if item not in ("", None)]
        if menu_items:
            lines.append(f"可选项: {', '.join(menu_items)}")

    branches = group.get("branches", [])
    if isinstance(branches, list) and branches:
        lines.append(f"分支数: {len(branches)}")

    return lines


def format_transits_for_screenplay(transits: list[dict[str, str]]) -> str:
    parts: list[str] = []
    for transit in transits:
        preset = transit.get("preset", "")
        transition = transit.get("transition", "none")
        easing = transit.get("easing", "none")
        parts.append(f"切到 `{preset}`（transition={transition}, easing={easing}）")
    return "；".join(parts)


def build_workspace_report(analysis: dict[str, Any]) -> str:
    workspace = analysis["workspace"]
    validate = analysis["validate"]
    stats = analysis["stats"]
    modules = analysis["modules"]
    myblocks = analysis["myblocks"]
    hits_by_define = analysis["hits_by_define"]
    scripts = analysis["scripts"]
    dialogues = analysis["dialogues"]
    cameras = analysis["cameras"]
    scene_events = analysis["scene_events"]
    quests = analysis["quests"]
    relative_file = analysis["relative_file"]
    project_name = analysis["project_name"]

    sections = [
        f"## {Path(relative_file).stem} | {project_name}",
        "",
        f"- 文件: `{relative_file}`",
        f"- 校验: `valid={validate.get('valid')}`，错误 {validate.get('error_count', 0)}，警告 {validate.get('warning_count', 0)}",
        f"- 工程类型: `type={workspace.get('type')}`，`projectMode={workspace.get('projectMode')}`，`showmyblock={workspace.get('showmyblock', True)}`",
        f"- 模块总数: {stats.get('module_count', 0)}，脚本数: {stats.get('script_count', 0)}，片段数: {stats.get('fragment_count', 0)}，Block 数: {stats.get('block_count', 0)}",
        f"- 资源引用数: {len(workspace.get('res', [])) if isinstance(workspace.get('res'), list) else 0}",
        "",
        "### 场景元素",
        "",
    ]

    scene_lines = summarize_scene_elements(stats)
    sections.extend(scene_lines or ["- 未识别到可摘要的场景元素"])

    sections.extend(
        [
            "",
            "### 剧情 / 对白",
            "",
            f"- 对白组数量: {len(dialogues)}",
        ]
    )
    sections.extend(summarize_dialogues(dialogues) or ["- 未配置对白组"])

    sections.extend(
        [
            "",
            "### 对白调用",
            "",
        ]
    )
    sections.extend(
        summarize_dialogue_uses(hits_by_define["PlayDialogueGroup"], scripts)
        or ["- 未发现 `PlayDialogueGroup` 调用"]
    )

    sections.extend(
        [
            "",
            "### 任务配置",
            "",
        ]
    )
    sections.extend(summarize_quests(quests) or ["- 未发现 `QuestObject`"])

    quest_action_lines = summarize_quest_actions(hits_by_define, scripts)
    if quest_action_lines:
        sections.extend(["", "任务相关脚本操作:"])
        sections.extend(quest_action_lines)

    sections.extend(
        [
            "",
            "### 分镜 / 相机",
            "",
            f"- 预设镜头数量: {len(cameras)}",
        ]
    )
    sections.extend(summarize_camera_presets(cameras) or ["- 未配置 editorScene 摄像机预设"])

    sections.extend(["", "实际调用的镜头预设:"])
    sections.extend(
        summarize_camera_transits(hits_by_define["TransitToCameraPreset"], scripts)
        or ["- 未发现 `TransitToCameraPreset` 调用"]
    )

    sections.extend(["", "相机脚本中的 myblock 分镜封装:"])
    sections.extend(summarize_camera_myblocks(myblocks, scripts) or ["- 未发现 CameraService 下的 myblock 分镜"])

    sections.extend(["", "相机相关直接操作:"])
    sections.extend(summarize_direct_camera_actions(hits_by_define, scripts) or ["- 未发现额外相机动作块"])

    sections.extend(
        [
            "",
            "### 消息 / 事件流",
            "",
        ]
    )
    if scene_events:
        sections.append(f"- Scene `#EVENT` 列表: {', '.join(scene_events)}")
    else:
        sections.append("- Scene 未配置 `#EVENT` 列表")

    sections.extend(
        summarize_message_graph(
            hits_by_define["WhenReceiveMessage"],
            hits_by_define["BroadcastMessage"],
            hits_by_define["BroadcastMessageAndWait"],
            scripts,
        )
        or ["- 未发现消息广播 / 接收链路"]
    )

    sections.extend(
        [
            "",
            f"- MCP `get_modules` 返回模块数: {len(modules)}",
            f"- MCP `get_myblocks` 返回 myblock 数: {len(myblocks)}",
            "",
        ]
    )
    return "\n".join(sections)


def build_workspace_screenplay(analysis: dict[str, Any]) -> str:
    relative_file = analysis["relative_file"]
    project_name = analysis["project_name"]
    stats = analysis["stats"]
    dialogues = analysis["dialogues"]
    dialogue_groups = analysis["dialogue_groups"]
    dialogue_beats = analysis["dialogue_beats"]
    used_dialogue_groups = analysis["used_dialogue_groups"]
    camera_beats = analysis["camera_beats"]
    quests = analysis["quests"]
    cameras = analysis["cameras"]
    scene_events = analysis["scene_events"]

    speakers = collect_dialogue_speakers(dialogues)
    unused_groups = [name for name in dialogue_groups if name not in set(used_dialogue_groups)]

    sections = [
        f"## {Path(relative_file).stem} | {project_name}",
        "",
        f"源文件: `{relative_file}`",
        "",
        "### 故事概览",
        "",
        f"这是一个包含 {len(dialogues)} 个对白组、{len(cameras)} 个镜头预设的工程。",
        f"主要可见场景元素包括: {scene_element_sentence(stats)}",
        f"主要对白角色: {', '.join(speakers) if speakers else '未识别'}。",
        f"场景事件数量: {len(scene_events)}。",
    ]

    if quests:
        quest_summary = "；".join(
            f"任务《{quest['title'] or quest['name']}》: {shorten(quest['content'], 60)}" for quest in quests
        )
        sections.append(f"任务线: {quest_summary}")
    else:
        sections.append("任务线: 当前工程没有独立 QuestObject。")

    if cameras:
        camera_names = ", ".join(str(camera.get("name", "(unnamed)")) for camera in cameras[:12])
        if len(cameras) > 12:
            camera_names += f" 等 {len(cameras)} 个镜头预设"
        sections.append(f"镜头预设: {camera_names}")

    sections.extend(
        [
            "",
            "说明: 下述分场按资源中片段出现顺序整理，适合快速阅读剧情、对白和镜头线索，不保证严格等同运行时顺序。",
            "",
            "### 分场剧本",
            "",
        ]
    )

    if dialogue_beats:
        for index, beat in enumerate(dialogue_beats, start=1):
            title = " / ".join(beat["dialogue_groups"])
            sections.extend(
                [
                    f"#### 场次 {index}: {title}",
                    "",
                    f"触发: {beat['owner']} / {beat['trigger']}",
                ]
            )

            if beat["transits"]:
                sections.append(f"镜头: {format_transits_for_screenplay(beat['transits'])}")
            if beat["camera_actions"]:
                sections.append(f"相机动作: {'；'.join(unique_preserve(beat['camera_actions']))}")
            if beat["broadcasts"] or beat["broadcast_waits"]:
                event_parts: list[str] = []
                if beat["broadcasts"]:
                    event_parts.append("广播 " + "、".join(f"`{name}`" for name in unique_preserve(beat["broadcasts"])))
                if beat["broadcast_waits"]:
                    event_parts.append(
                        "广播并等待 "
                        + "、".join(f"`{name}`" for name in unique_preserve(beat["broadcast_waits"]))
                    )
                sections.append(f"后续事件: {'；'.join(event_parts)}")

            sections.extend(["", "对白:"])
            for group_name in beat["dialogue_groups"]:
                group = dialogue_groups.get(group_name)
                sections.append(f"【{group_name}】")
                if group is None:
                    sections.append("（未在 dialogues.DialogueGroups 中找到该对白组定义）")
                    continue
                sections.extend(render_dialogue_group(group))
                sections.append("")
    else:
        sections.append("当前工程没有 `PlayDialogueGroup` 调用，无法从脚本中还原出对话驱动的剧情分场。")
        sections.append("")
        if dialogues:
            sections.append("现有对白组内容:")
            sections.append("")
            for group in dialogues:
                sections.append(f"【{group.get('name', '(unnamed)')}】")
                sections.extend(render_dialogue_group(group))
                sections.append("")

    sections.extend(["### 镜头补充", ""])
    if camera_beats:
        for index, beat in enumerate(camera_beats, start=1):
            sections.append(f"#### 镜头片段 {index}")
            sections.append("")
            sections.append(f"触发: {beat['owner']} / {beat['trigger']}")
            if beat["transits"]:
                sections.append(f"镜头: {format_transits_for_screenplay(beat['transits'])}")
            if beat["camera_actions"]:
                sections.append(f"相机动作: {'；'.join(unique_preserve(beat['camera_actions']))}")
            if beat["broadcasts"] or beat["broadcast_waits"]:
                event_parts = []
                if beat["broadcasts"]:
                    event_parts.append("广播 " + "、".join(f"`{name}`" for name in unique_preserve(beat["broadcasts"])))
                if beat["broadcast_waits"]:
                    event_parts.append(
                        "广播并等待 "
                        + "、".join(f"`{name}`" for name in unique_preserve(beat["broadcast_waits"]))
                    )
                sections.append(f"后续事件: {'；'.join(event_parts)}")
            sections.append("")
    else:
        sections.append("没有额外的纯镜头片段。")
        sections.append("")

    sections.extend(["### 任务与事件提示", ""])
    if quests:
        for quest in quests:
            sections.append(
                f"任务《{quest['title'] or quest['name']}》采用样式 `{quest['style']}`，说明为「{quest['content']}」。"
            )
    else:
        sections.append("没有单独的 QuestObject 任务面板。")

    if scene_events:
        sections.append(f"Scene `#EVENT` 中声明的事件有: {', '.join(scene_events)}")
    else:
        sections.append("Scene 没有配置 `#EVENT` 列表。")

    if unused_groups:
        sections.append(
            "未直接被 `PlayDialogueGroup` 调用的对白组: " + ", ".join(f"`{name}`" for name in unused_groups)
        )

    sections.append("")
    return "\n".join(sections)


async def analyze_workspace(session: ClientSession, relative_file: str) -> dict[str, Any]:
    workspace_payload = await call_json(session, "load_workspace_file", {"file_path": relative_file})
    workspace = workspace_payload["data"]
    validate = await call_json(session, "validate_workspace", {"workspace_data": workspace})
    stats = await call_json(session, "analyze_workspace_statistics", {"workspace_data": workspace})
    modules = await call_json(session, "get_modules", {"workspace_data": workspace})
    myblocks = await call_json(session, "get_myblocks", {"workspace_data": workspace})

    hits_by_define: dict[str, list[dict[str, Any]]] = {}
    for define in BLOCK_DEFINES:
        hits_by_define[define] = await call_json(
            session,
            "find_blocks_by_type",
            {"workspace_data": workspace, "block_define": define},
        )

    scripts = walk_module_tree(workspace)
    dialogues = collect_dialogues(workspace)
    dialogue_groups = dialogue_map(dialogues)
    quests = collect_quests(workspace)
    cameras = workspace.get("editorScene", {}).get("cameras", [])
    if not isinstance(cameras, list):
        cameras = []
    scene_events = collect_scene_event_names(workspace)
    dialogue_beats, used_dialogue_groups = collect_dialogue_beats(scripts)
    camera_beats = collect_camera_only_beats(scripts)
    project_name = str(workspace.get("name", "") or Path(relative_file).stem)

    return {
        "relative_file": relative_file,
        "project_name": project_name,
        "workspace": workspace,
        "validate": validate,
        "stats": stats,
        "modules": modules,
        "myblocks": myblocks,
        "hits_by_define": hits_by_define,
        "scripts": scripts,
        "dialogues": dialogues,
        "dialogue_groups": dialogue_groups,
        "quests": quests,
        "cameras": cameras,
        "scene_events": scene_events,
        "dialogue_beats": dialogue_beats,
        "used_dialogue_groups": used_dialogue_groups,
        "camera_beats": camera_beats,
    }


async def main() -> int:
    ws_files = sorted(path.relative_to(ROOT).as_posix() for path in REFERENCE_ROOT.rglob("*.ws"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    server = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PY), str(ROOT)],
    )

    stats_sections = [
        "# Reference `.ws` MCP 结构化报告",
        "",
        "- 生成方式: 通过当前 `mcp/hetu_mcp/server.py` 的 stdio MCP 工具链加载和分析",
        f"- 参考文件数: {len(ws_files)}",
        f"- 输出位置: `{STATS_OUTPUT_MD.relative_to(ROOT).as_posix()}`",
        "",
    ]

    screenplay_sections = [
        "# Reference `.ws` 人类可读剧本",
        "",
        "- 生成方式: 通过当前 `mcp/hetu_mcp/server.py` 的 stdio MCP 工具链加载和分析",
        f"- 参考文件数: {len(ws_files)}",
        f"- 输出位置: `{SCREENPLAY_OUTPUT_MD.relative_to(ROOT).as_posix()}`",
        "",
    ]

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            for relative_file in ws_files:
                analysis = await analyze_workspace(session, relative_file)
                stats_sections.append(build_workspace_report(analysis))
                screenplay_sections.append(build_workspace_screenplay(analysis))

    STATS_OUTPUT_MD.write_text("\n".join(stats_sections), encoding="utf-8")
    SCREENPLAY_OUTPUT_MD.write_text("\n".join(screenplay_sections), encoding="utf-8")

    if LEGACY_REPORT_MD.exists():
        LEGACY_REPORT_MD.unlink()

    print(f"stats_written: {STATS_OUTPUT_MD}")
    print(f"screenplay_written: {SCREENPLAY_OUTPUT_MD}")
    print(f"workspace_count: {len(ws_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
