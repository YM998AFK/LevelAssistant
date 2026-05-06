"""
Definition snapshot loading and optional C# source extraction helpers.

The MCP runtime loads committed snapshots from script_definition_data.py so it
never depends on files outside mcp/hetu_mcp. The C# extraction code in this file
is kept for explicit regeneration/maintenance workflows only.
"""

from __future__ import annotations

import copy
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from definitions.script_definition_data import SCRIPT_BLOCK_DEFINITIONS, SCRIPT_WORKSPACE_DEFINITIONS


_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT_BLOCK_ROOT: Optional[Path] = None

_CATEGORY_NAME_MAP = {
    "Events": "events",
    "Motion": "motion",
    "Looks": "looks",
    "Sound": "sound",
    "Control": "control",
    "Sensing": "sensing",
    "Operators": "operators",
    "Variables": "variables",
    "MyBlocks": "myblocks",
    "Music": "music",
    "Magic": "magic",
    "Physics": "physics",
    "Stage": "stage",
    "Experiment": "experiment",
}

_PARAMETER_NAME_OVERRIDES = {
    "BeFixedSetting": ["state"],
    "AnchorTo": ["target", "space", "offset_mode", "bone"],
    "BroadcastMessage": ["message"],
    "BroadcastMessageAndWait": ["message"],
    "CameraFollow": ["target", "x", "y", "z"],
    "CameraLookAt2": ["source", "target"],
    "CameraLookAtPos": ["x", "y", "z"],
    "CameraLookAtWithOffset": ["target", "x", "y", "z"],
    "ChangeCameraFOV": ["delta"],
    "ChangeLabel": ["text", "font_size", "text_color", "stroke_color", "shadow_color"],
    "ChangePosX": ["delta"],
    "ChangePosY": ["delta"],
    "ChangePosZ": ["delta"],
    "CollideSetting": ["state"],
    "CompleteQuest": ["animation"],
    "CostumeOp": ["property"],
    "CreateCloneOf": ["target"],
    "EndRun": ["result", "message"],
    "FallSetting": ["state"],
    "FollowAndKeepDistance": ["target", "distance"],
    "GetCurrentDate": ["part"],
    "GetPropertyOf": ["property", "target"],
    "GlideSecsToPosition2D": ["seconds", "x", "y"],
    "GlideSecsToPosition3D": ["seconds", "x", "y", "z"],
    "GlideSecsToPosition3DAndSetRotation": [
        "seconds",
        "x",
        "y",
        "z",
        "direction",
        "pitch",
        "curve",
    ],
    "GlideSecsToTarget": ["seconds", "target"],
    "GlideStepsInSecs": ["steps", "seconds"],
    "GotoPosition2D": ["x", "y"],
    "GotoPosition3D": ["x", "y", "z"],
    "GotoProject": ["project"],
    "HideQuest": ["animation"],
    "HideVar": ["variable"],
    "IncVar": ["variable", "delta"],
    "IsGreator": ["val1", "val2"],
    "IsKeyPressed": ["key"],
    "ListAdd": ["item", "list"],
    "ListContainsItem": ["list", "item"],
    "ListDelete": ["index", "list"],
    "ListDeleteALl": ["list"],
    "ListGetItemAt": ["index", "list"],
    "ListGetItemIndex": ["item", "list"],
    "ListGetLength": ["list"],
    "ListHide": ["list"],
    "ListInsertAt": ["item", "index", "list"],
    "ListReplaceItemAt": ["index", "list", "value"],
    "ListShow": ["list"],
    "MathFunc": ["function", "value"],
    "Mod": ["dividend", "divisor"],
    "PickRandom": ["from", "to"],
    "PlayAnimation": ["animation"],
    "PlayAnimationAndWait": ["animation", "timeout"],
    "PlayAnimationUntil": ["animation", "state"],
    "PlayAnimationUntilAndWait": ["animation", "state", "timeout"],
    "PlayBGM": ["music", "volume"],
    "PlayDialogueGroup": ["dialogue_group"],
    "PlayEmotionAnimation": ["animation", "loop"],
    "PlayInstrument": ["note", "beats"],
    "PlayTransitEffect": ["out_transition", "in_transition"],
    "PlayVideo": ["video", "mode"],
    "PlayWindowedVideo": ["video", "anchor", "x", "y"],
    "RaycastTest": ["dx", "dy", "dz"],
    "Round": ["value"],
    "SaySeconds": ["message", "seconds"],
    "Set3DSettings": ["min_distance", "max_distance", "doppler"],
    "SetCameraFOV": ["fov"],
    "SetCameraDamping": ["mode", "x", "y", "z"],
    "SetDialogueCamera": ["target"],
    "SetDialoguePlayMode": ["mode"],
    "SetDialogueStyle": ["style"],
    "SetDialogueTypingSpeed": ["speed"],
    "SetInstrumentPitch": ["tempo"],
    "SetPosX": ["x"],
    "SetPosY": ["y"],
    "SetPosZ": ["z"],
    "SetQuestStyle": ["style"],
    "SetQuestText": ["text"],
    "SetSpeedMul": ["ratio"],
    "SetVar": ["variable", "value"],
    "ShowLabel": ["text"],
    "ShowQuest": ["animation"],
    "ShowSpriteName": ["visibility"],
    "ShowVar": ["variable"],
    "StartWalk": ["mode"],
    "StopScript": ["scope"],
    "StrContains": ["text", "substring"],
    "StrJoin": ["text1", "text2"],
    "StrLength": ["text"],
    "StrLetterOf": ["index", "text"],
    "StopWalk": ["target"],
    "Think": ["message"],
    "ThinkForSeconds": ["message", "seconds"],
    "ThinkSeconds": ["message", "seconds"],
    "TransitProject": ["project", "out_transition", "in_transition"],
    "TransitToCameraPreset": ["camera_preset", "out_transition", "in_transition"],
    "TurnDown": ["degrees"],
    "TurnToAngleInSecs": ["direction", "seconds"],
    "TurnToTargetInSecs": ["target", "seconds"],
    "TurnUp": ["degrees"],
    "WhenCollisionDetected": ["target"],
    "WhenLoudnessOrTimer": ["source", "threshold"],
    "WhenReceiveMessage": ["message"],
    "WhenThisSpriteClicked": ["target"],
}

_RETURN_TYPE_OVERRIDES = {
    "Add": "number",
    "Answer": "mixed",
    "CostumeOp": "mixed",
    "DistanceTo": "number",
    "Divide": "number",
    "GetCloneId": "number",
    "GetCurrentDate": "number",
    "GetDaysSince2000": "number",
    "GetDirection": "number",
    "GetInstrumentPitch": "number",
    "GetLoudness": "number",
    "GetPitch": "number",
    "GetPosX": "number",
    "GetPosY": "number",
    "GetPosZ": "number",
    "GetPropertyOf": "mixed",
    "GetSpriteName": "string",
    "GetTimer": "number",
    "GetUserName": "string",
    "GetVolume": "number",
    "ListGetItemAt": "mixed",
    "ListGetItemIndex": "number",
    "ListGetLength": "number",
    "ListVariable": "mixed",
    "MathFunc": "number",
    "Mod": "number",
    "MouseX": "number",
    "MouseY": "number",
    "Multiply": "number",
    "PickRandom": "number",
    "Round": "number",
    "SelectedMenuItem": "string",
    "SelectedMenuItemIndex": "number",
    "SizeOp": "number",
    "StrJoin": "string",
    "StrLength": "number",
    "StrLetterOf": "string",
    "Subtract": "number",
    "Variable": "mixed",
    "XPosOfSubLabel": "number",
    "YPosOfSubLabel": "number",
}

_ALIAS_DEFINITIONS = {
    "ChangePlaySpeed": "ChangeInstrumentPitch",
    "GetDistanceTo": "DistanceTo",
    "GetPlaySpeed": "GetInstrumentPitch",
    "IsGreater": "IsGreator",
    "SayForSeconds": "SaySeconds",
    "SetPlaySpeed": "SetInstrumentPitch",
    "ThinkForSeconds": "ThinkSeconds",
    "WhenClicked": "WhenThisSpriteClicked",
}

_DROPDOWN_NAME_HINTS = {
    "anchorbone": "bone",
    "animation": "animation",
    "camera": "target",
    "cameracurve": "curve",
    "camerapreset": "camera_preset",
    "clone": "target",
    "collisiondetection": "target",
    "currentdate": "part",
    "dialoguegroup": "dialogue_group",
    "dialoguestyle": "style",
    "distance": "target",
    "drum": "drum",
    "emotionanimation": "animation",
    "goto": "target",
    "instrument": "instrument",
    "labeltarget": "label",
    "listcombo": "list",
    "mathfunc": "function",
    "message": "message",
    "mouseortarget": "target",
    "onlytarget": "target",
    "pictures": "costume",
    "project": "project",
    "property": "property",
    "questhideanim": "animation",
    "questshowanim": "animation",
    "queststyle": "style",
    "rotationstyle": "rotation_style",
    "selfortarget": "target",
    "sound": "sound",
    "spritetarget": "target",
    "target": "target",
    "transition": "transition",
    "variablecombo": "variable",
    "video": "video",
}


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def _strip_generic(type_name: str) -> str:
    return re.sub(r"<.*>", "", type_name).split(".")[-1]


def _find_braced_block(text: str, start_index: int) -> Tuple[Optional[str], int]:
    open_index = text.find("{", start_index)
    if open_index == -1:
        return None, -1

    depth = 0
    for index in range(open_index, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[open_index + 1 : index], index + 1

    return None, -1


def _extract_chain_tokens(text: str) -> List[Tuple[str, str]]:
    tokens: List[Tuple[str, str]] = []
    index = 0

    while index < len(text):
        match = re.search(
            r"\.(AddLabel|AddVariable|AddFixedDroplist|AddLogical)\(",
            text[index:],
        )
        if not match:
            break

        kind = match.group(1)
        arg_start = index + match.end()
        depth = 1
        cursor = arg_start

        while cursor < len(text) and depth > 0:
            if text[cursor] == "(":
                depth += 1
            elif text[cursor] == ")":
                depth -= 1
            cursor += 1

        tokens.append((kind, text[arg_start : cursor - 1].strip()))
        index = cursor

    return tokens


def _normalize_on_create_body(body: str) -> str:
    if "I18N.Language" not in body:
        return body

    else_match = re.search(r"else\s*\{", body)
    if else_match:
        else_body, _ = _find_braced_block(body, else_match.start())
        if else_body is not None:
            return else_body

    return body


def _parse_literal_options(arg: str) -> Optional[List[str]]:
    match = re.search(r"new(?:\s+string)?\[\]\s*\{(.*?)\}", arg, re.S)
    if not match:
        return None

    options = re.findall(r'"([^"]+)"', match.group(1))
    return options or None


def _infer_name_from_dropdown(arg: str) -> Optional[str]:
    match = re.search(r"new\s+(?:Instructions\.)?(\w+)", arg)
    if not match:
        return None

    dropdown_name = match.group(1).lower()
    for needle, name in _DROPDOWN_NAME_HINTS.items():
        if needle in dropdown_name:
            return name

    return None


def _infer_name_from_labels(labels: str) -> Optional[str]:
    labels = labels.lower()
    if "x:" in labels:
        return "x"
    if "y:" in labels:
        return "y"
    if "z:" in labels:
        return "z"
    if "direction" in labels:
        return "direction"
    if "pitch" in labels:
        return "pitch"
    if "seconds" in labels or "secs" in labels:
        return "seconds"
    if "beats" in labels:
        return "beats"
    if "volume" in labels:
        return "volume"
    if "tempo" in labels:
        return "tempo"
    if "size" in labels:
        return "size"
    if "brightness" in labels:
        return "brightness"
    if "transparency" in labels:
        return "transparency"
    if "ratio" in labels:
        return "ratio"
    if "speed" in labels:
        return "speed"
    if "fov" in labels:
        return "fov"
    if "letter" in labels or "item" in labels:
        return "index"
    if "question" in labels:
        return "question"
    if "name" in labels:
        return "name"
    return None


def _infer_parameter_name(
    block_name: str,
    param_index: int,
    kind: str,
    arg: str,
    prev_label: str,
    next_label: str,
    used_names: Dict[str, int],
) -> str:
    override_names = _PARAMETER_NAME_OVERRIDES.get(block_name, [])
    if param_index < len(override_names):
        return override_names[param_index]

    if kind == "AddLogical":
        candidate = "condition"
    else:
        candidate = _infer_name_from_dropdown(arg)
        if candidate is None:
            candidate = _infer_name_from_labels(" ".join(part for part in (prev_label, next_label) if part))

    if candidate is None:
        candidate = f"param{param_index + 1}"

    used_count = used_names.get(candidate, 0)
    used_names[candidate] = used_count + 1
    if used_count:
        return f"{candidate}_{used_count + 1}"
    return candidate


def _infer_parameter_spec(
    block_name: str,
    param_index: int,
    kind: str,
    arg: str,
    prev_label: str,
    next_label: str,
    used_names: Dict[str, int],
) -> Dict[str, Any]:
    options = _parse_literal_options(arg)
    embeddable = kind not in {"AddFixedDroplist"} and not arg.startswith("new ")
    default_value: Optional[str] = None

    if kind == "AddLogical":
        param_type = "boolean"
        embeddable = True
    elif options and set(options) <= {"true", "false"}:
        param_type = "boolean"
        embeddable = False
        default_value = options[0]
    else:
        literal_match = re.search(r'"([^"]*)"', arg)
        default_value = literal_match.group(1) if literal_match else None

        if any(
            popup in arg
            for popup in (
                "VariablePopupType.NumericKeypad",
                "VariablePopupType.Compass",
                "VariablePopupType.CompassPitch",
                "VariablePopupType.PianoKeyborad",
            )
        ):
            param_type = "number"
        elif default_value is not None and re.fullmatch(r"-?\d+(?:\.\d+)?", default_value):
            param_type = "number"
        else:
            param_type = "string"

    spec = {
        "name": _infer_parameter_name(
            block_name,
            param_index,
            kind,
            arg,
            prev_label,
            next_label,
            used_names,
        ),
        "type": param_type,
        "embeddable": embeddable,
    }

    if default_value not in (None, ""):
        spec["default"] = default_value
    if options:
        spec["options"] = options

    return spec


def _build_parameter_specs(block_name: str, tokens: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
    specs: List[Dict[str, Any]] = []
    used_names: Dict[str, int] = {}

    for token_index, (kind, arg) in enumerate(tokens):
        if kind not in {"AddVariable", "AddFixedDroplist", "AddLogical"}:
            continue

        prev_label = ""
        next_label = ""

        for index in range(token_index - 1, -1, -1):
            if tokens[index][0] == "AddLabel":
                prev_label = tokens[index][1]
                break
            if tokens[index][0] in {"AddVariable", "AddFixedDroplist", "AddLogical"}:
                break

        for index in range(token_index + 1, len(tokens)):
            if tokens[index][0] == "AddLabel":
                next_label = tokens[index][1]
                break
            if tokens[index][0] in {"AddVariable", "AddFixedDroplist", "AddLogical"}:
                break

        specs.append(
            _infer_parameter_spec(
                block_name,
                len(specs),
                kind,
                arg,
                prev_label,
                next_label,
                used_names,
            )
        )

    return specs


def _parse_block_names(block_root: Path) -> Dict[str, str]:
    block_names_path = block_root / "BlockNames.cs"
    if not block_names_path.exists():
        return {}

    text = block_names_path.read_text(encoding="utf-8", errors="ignore")
    return dict(re.findall(r'public const string\s+(\w+)\s*=\s*"([^"]+)";', text))


def _split_top_level_commas(text: str) -> List[str]:
    parts: List[str] = []
    current: List[str] = []
    depth_paren = 0
    depth_brace = 0

    for char in text:
        if char == "," and depth_paren == 0 and depth_brace == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue

        current.append(char)
        if char == "(":
            depth_paren += 1
        elif char == ")" and depth_paren > 0:
            depth_paren -= 1
        elif char == "{":
            depth_brace += 1
        elif char == "}" and depth_brace > 0:
            depth_brace -= 1

    part = "".join(current).strip()
    if part:
        parts.append(part)
    return parts


def _extract_type_names(text: str) -> List[str]:
    names: List[str] = []
    for raw_name in re.findall(r"typeof\(([^)]+)\)", text):
        type_name = _strip_generic(raw_name.split(".")[-1].strip())
        if type_name and type_name not in names:
            names.append(type_name)
    return names


def _parse_register_limit_bindings(body: str) -> Dict[str, List[str]]:
    bindings: Dict[str, List[str]] = {}
    pattern = re.compile(
        r"Type\[\]\s+(\w+)\s*=\s*new\s+Type\[\]\s*\{(?P<body>.*?)\};",
        re.S,
    )

    for match in pattern.finditer(body):
        bindings[match.group(1)] = _extract_type_names(match.group("body"))

    return bindings


def _resolve_register_object_types(
    arg_text: str,
    limit_bindings: Dict[str, List[str]],
) -> Optional[List[str]]:
    arg_text = arg_text.strip()
    if not arg_text:
        return None

    if arg_text.startswith(","):
        arg_text = arg_text[1:].strip()
    if not arg_text:
        return None

    resolved: List[str] = []
    for part in _split_top_level_commas(arg_text):
        if re.fullmatch(r"\w+", part):
            for type_name in limit_bindings.get(part, []):
                if type_name not in resolved:
                    resolved.append(type_name)
            continue

        for type_name in _extract_type_names(part):
            if type_name not in resolved:
                resolved.append(type_name)

    return resolved or None


def _parse_registered_defines(block_root: Path) -> Dict[str, Dict[str, Any]]:
    registered: Dict[str, Dict[str, Any]] = {}
    modules_root = block_root / "Modules" / "Internal"
    if not modules_root.exists():
        return registered

    for path in sorted(modules_root.glob("*.cs")):
        text = _strip_comments(path.read_text(encoding="utf-8", errors="ignore"))
        match = re.search(
            r"class\s+\w+\s*:\s*BlockModule.*?public override string Category => BlockCatalogs\.(\w+);",
            text,
            re.S,
        )
        if not match:
            continue

        category_name = _CATEGORY_NAME_MAP.get(match.group(1))
        if category_name is None:
            continue

        register_all_body = text
        register_all_match = re.search(r"RegisterAll\s*\(\s*BlockService\s+service\s*\)", text)
        if register_all_match:
            body, _ = _find_braced_block(text, register_all_match.start())
            if body is not None:
                register_all_body = body

        limit_bindings = _parse_register_limit_bindings(register_all_body)
        for register_match in re.finditer(
            r"\bRegister<(?P<define>[^>]+)>\(service(?P<args>.*?)\);",
            register_all_body,
            re.S,
        ):
            define_class = _strip_generic(register_match.group("define"))
            registered[define_class] = {
                "category": category_name,
                "object_types": _resolve_register_object_types(
                    register_match.group("args"),
                    limit_bindings,
                ),
            }

    return registered


def _parse_instruction_classes(block_root: Path) -> Dict[str, Dict[str, Any]]:
    instructions_root = block_root / "Instructions"
    classes: Dict[str, Dict[str, Any]] = {}
    if not instructions_root.exists():
        return classes

    class_pattern = re.compile(
        r"(?:public\s+|sealed\s+|abstract\s+|internal\s+|protected\s+|private\s+)*"
        r"class\s+(\w+)(?:<[^>]+>)?\s*:\s*([^\s{]+)"
    )

    for path in sorted(instructions_root.rglob("*.cs")):
        text = _strip_comments(path.read_text(encoding="utf-8", errors="ignore"))
        cursor = 0

        while True:
            match = class_pattern.search(text, cursor)
            if not match:
                break

            class_name = match.group(1)
            body, end = _find_braced_block(text, match.start())
            if body is None:
                break

            classes[class_name] = {
                "base": _strip_generic(match.group(2)),
                "is_logical": bool(
                    re.search(r"override\s+bool\s+IsLogical\s*=>\s*true", body)
                    or re.search(
                        r"override\s+bool\s+IsLogical\s*\{.*?return\s+true\s*;",
                        body,
                        re.S,
                    )
                ),
                "has_branch": bool(
                    re.search(r"override\s+bool\s+HasBranch\s*=>\s*true", body)
                    or re.search(
                        r"override\s+bool\s+HasBranch\s*\{.*?return\s+true\s*;",
                        body,
                        re.S,
                    )
                ),
            }
            cursor = end

    return classes


def _resolve_instruction_type(
    instruction_name: str,
    classes: Dict[str, Dict[str, Any]],
) -> Tuple[str, bool]:
    current = _strip_generic(instruction_name)
    logical = False
    has_branch = False
    seen = set()

    while current and current not in seen:
        seen.add(current)
        info = classes.get(current)
        if info is None:
            return "Statement", False

        logical = logical or info["is_logical"]
        has_branch = has_branch or info["has_branch"]
        base = info["base"]

        if base == "Trigger":
            return "Trigger", False
        if base == "Statement":
            return ("BranchStatement" if has_branch else "Statement"), has_branch
        if base == "Operation":
            return ("LogicalOperator" if logical else "Operator"), False

        current = base

    return "Statement", False


@lru_cache(maxsize=1)
def load_script_block_definitions(root: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    block_root = root or _SCRIPT_BLOCK_ROOT
    if block_root is None or not block_root.exists():
        return {}

    block_names = _parse_block_names(block_root)
    registered_defines = _parse_registered_defines(block_root)
    instruction_classes = _parse_instruction_classes(block_root)
    definitions: Dict[str, Dict[str, Any]] = {}

    define_pattern = re.compile(
        r"(?:public\s+|sealed\s+|abstract\s+|internal\s+|private\s+)*"
        r"class\s+(\w+)(?:<[^>]+>)?\s*:\s*BlockDefineImpl<(?:Instructions\.)?([^\s>]+)>"
    )

    defines_root = block_root / "Defines"
    if not defines_root.exists():
        return {}

    for path in sorted(defines_root.glob("*.cs")):
        text = _strip_comments(path.read_text(encoding="utf-8", errors="ignore"))
        cursor = 0

        while True:
            match = define_pattern.search(text, cursor)
            if not match:
                break

            define_class = match.group(1)
            body, end = _find_braced_block(text, match.start())
            if body is None:
                break
            cursor = end

            registration = registered_defines.get(define_class)
            if registration is None:
                continue
            category_name = registration["category"]

            name_match = re.search(
                r'override\s+string\s+Name\s*=>\s*(?:BlockNames\.(\w+)|"([^"]+)");',
                body,
            )
            if not name_match:
                continue

            const_name = name_match.group(1)
            block_name = (
                block_names.get(const_name, const_name) if const_name else name_match.group(2)
            )
            on_create_match = re.search(r"OnCreate\s*\(\s*Block\s+block\s*\)", body)
            on_create_body = ""
            if on_create_match:
                on_create_body, _ = _find_braced_block(body, on_create_match.start())
                on_create_body = _normalize_on_create_body(on_create_body or "")

            tokens = _extract_chain_tokens(on_create_body)
            block_type, has_branch = _resolve_instruction_type(
                match.group(2),
                instruction_classes,
            )

            definition: Dict[str, Any] = {
                "category": category_name,
                "type": block_type,
                "description": "",
                "parameters": _build_parameter_specs(block_name, tokens),
                "return_type": None,
            }
            if registration.get("object_types") is not None:
                definition["object_types"] = copy.deepcopy(registration["object_types"])

            if block_type == "LogicalOperator":
                definition["return_type"] = "boolean"
            elif block_type == "Operator":
                definition["return_type"] = _RETURN_TYPE_OVERRIDES.get(block_name, "mixed")

            if has_branch:
                definition["has_branch"] = True
                definition["branch_count"] = 1 + on_create_body.count("block.NewSection(")

            definitions[block_name] = definition

    for alias, target in _ALIAS_DEFINITIONS.items():
        target_definition = definitions.get(target)
        if target_definition is not None:
            definitions[alias] = dict(target_definition)

    return definitions


_SCRIPT_ROOT: Optional[Path] = None

_PROPERTY_TYPE_MAP = {
    "StringProperty": "string",
    "BoolProperty": "boolean",
    "IntProperty": "integer",
    "FloatProperty": "float",
    "Vector2Property": "vector2",
    "Vector3Property": "vector3",
    "QuaternionProperty": "quaternion",
    "ColorProperty": "color",
    "ObjectProperty": "object_ref",
    "SimpleProperty": "simple",
    "SimpleListProperty": "simple_list",
}

_CLASS_PATTERN = re.compile(
    r"(?P<attrs>(?:\s*\[[^\]]+\]\s*)*)"
    r"(?:(?:public|protected|internal|private|sealed|abstract|partial|static)\s+)*"
    r"class\s+(?P<name>\w+)(?:<[^>]+>)?\s*(?::\s*(?P<bases>[^{]+))?"
)

_PROPERTY_DECL_PATTERN = re.compile(
    r"(?:(?:public|protected|internal|private)\s+)*"
    r"(?:readonly\s+)?"
    r"(?P<ptype>\w+Property)\s+(?P<field>\w+)\s*=\s*new\s*\(\s*\"(?P<name>[^\"]+)\"",
    re.S,
)

_PROPERTY_ASSIGN_PATTERN = re.compile(
    r"(?:this\.)?(?P<field>\w+)\s*=\s*new\s+(?P<ptype>\w+Property)\s*\(\s*\"(?P<name>[^\"]+)\"",
    re.S,
)

_REGISTER_PROPERTY_PATTERN = re.compile(
    r"RegisterProperty\([^,]+,\s*(?:this\.)?(?P<field>\w+)\s*\)"
)

_NON_SERIALIZABLE_PATTERN = re.compile(
    r"(?:this\.)?(?P<field>\w+)\.serializable\s*=\s*false"
)

_CUSTOM_PROPERTY_PATTERNS = (
    ("simple", re.compile(r'AddSimpleCustomProperty\(\s*"([^"]+)"')),
    ("simple_list", re.compile(r'AddSimpleListCustomProperty\(\s*"([^"]+)"')),
    (
        "typed",
        re.compile(r'AddCustomProperty\(\s*"([^"]+)"\s*,\s*ValueType\.(\w+)'),
    ),
)

_VALUE_TYPE_NAME_MAP = {
    "String": "string",
    "Boolean": "boolean",
    "Int": "integer",
    "Float": "float",
    "Vector2": "vector2",
    "Vector3": "vector3",
    "Quaternion": "quaternion",
    "Color": "color",
    "Object": "object_ref",
    "Simple": "simple",
    "SimpleList": "simple_list",
}

_COMPAT_MODULE_DEFINITIONS = {
    "UIView": {
        "base": "UIObject",
        "kind": "ui",
        "description": "Compat definition inferred from serialized .ws UI view objects.",
        "properties": [
            {"name": "Type", "type": "string", "serializable": True},
            {"name": "Anchor", "type": "boolean", "serializable": True},
            {"name": "Package", "type": "string", "serializable": True},
            {"name": "View", "type": "string", "serializable": True},
            {"name": "Disable", "type": "boolean", "serializable": True},
            {"name": "Transparency", "type": "float", "serializable": True},
            {"name": "Title", "type": "string", "serializable": True},
            {"name": "Icon", "type": "string", "serializable": True},
            {"name": "Value", "type": "float", "serializable": True},
            {"name": "MaxValue", "type": "float", "serializable": True},
        ],
        "known_custom_properties": [],
        "source": "compat-fallback",
    },
    "UIPackageObject": {
        "base": "Object",
        "kind": "asset",
        "description": "Compat definition inferred from serialized .ws UI package assets.",
        "properties": [
            {"name": "Name", "type": "string", "serializable": True},
            {"name": "EditMode", "type": "integer", "serializable": True},
            {"name": "AssetId", "type": "integer", "serializable": True},
        ],
        "known_custom_properties": [],
        "source": "compat-fallback",
    },
}


def _normalize_base_name(base_name: str) -> str:
    base_name = base_name.strip()
    if not base_name:
        return ""
    return _strip_generic(base_name.split()[-1].split(".")[-1])


def _parse_creation_attribute(attrs: str) -> Optional[Dict[str, Any]]:
    service_match = re.search(
        r'CreationService\(\s*"(?P<name>[^"]+)"\s*,\s*(?P<container>true|false)',
        attrs,
    )
    if service_match:
        return {
            "attribute": "CreationService",
            "service_name": service_match.group("name"),
            "is_container": service_match.group("container") == "true",
        }

    object_match = re.search(
        r"CreationObject\(\s*(?P<container>true|false)",
        attrs,
    )
    if object_match:
        return {
            "attribute": "CreationObject",
            "is_container": object_match.group("container") == "true",
        }

    return None


def _merge_property_field(
    fields: Dict[str, Dict[str, Any]],
    field_name: str,
    property_type: str,
    property_name: str,
) -> None:
    fields[field_name] = {
        "field": field_name,
        "property_class": property_type,
        "name": property_name,
        "type": _PROPERTY_TYPE_MAP.get(property_type, "unknown"),
    }


def _parse_property_fields(body: str) -> Dict[str, Dict[str, Any]]:
    fields: Dict[str, Dict[str, Any]] = {}

    for match in _PROPERTY_DECL_PATTERN.finditer(body):
        _merge_property_field(
            fields,
            match.group("field"),
            match.group("ptype"),
            match.group("name"),
        )

    for match in _PROPERTY_ASSIGN_PATTERN.finditer(body):
        _merge_property_field(
            fields,
            match.group("field"),
            match.group("ptype"),
            match.group("name"),
        )

    return fields


def _parse_known_custom_properties(body: str) -> List[Dict[str, Any]]:
    properties: List[Dict[str, Any]] = []
    seen = set()

    for kind, pattern in _CUSTOM_PROPERTY_PATTERNS:
        for match in pattern.finditer(body):
            if kind == "typed":
                name = match.group(1)
                value_type = match.group(2)
                property_type = _VALUE_TYPE_NAME_MAP.get(value_type, "unknown")
            else:
                name = match.group(1)
                property_type = kind

            if name in seen:
                continue

            seen.add(name)
            properties.append(
                {
                    "name": name,
                    "type": property_type,
                    "serializable": True,
                    "custom": True,
                }
            )

    return properties


def _merge_class_info(existing: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(existing)

    if not merged.get("base") and incoming.get("base"):
        merged["base"] = incoming["base"]

    if not merged.get("direct_attribute") and incoming.get("direct_attribute"):
        merged["direct_attribute"] = incoming["direct_attribute"]

    merged.setdefault("files", [])
    for file_name in incoming.get("files", []):
        if file_name not in merged["files"]:
            merged["files"].append(file_name)

    merged.setdefault("property_fields", {}).update(incoming.get("property_fields", {}))

    merged.setdefault("registered_fields", [])
    for field_name in incoming.get("registered_fields", []):
        if field_name not in merged["registered_fields"]:
            merged["registered_fields"].append(field_name)

    merged.setdefault("non_serializable_fields", set()).update(
        incoming.get("non_serializable_fields", set())
    )

    merged.setdefault("known_custom_properties", [])
    known_custom_names = {item["name"] for item in merged["known_custom_properties"]}
    for item in incoming.get("known_custom_properties", []):
        if item["name"] not in known_custom_names:
            known_custom_names.add(item["name"])
            merged["known_custom_properties"].append(item)

    return merged


def _parse_script_classes(root: Path) -> Dict[str, Dict[str, Any]]:
    classes: Dict[str, Dict[str, Any]] = {}

    for path in sorted(root.rglob("*.cs")):
        text = _strip_comments(path.read_text(encoding="utf-8", errors="ignore"))
        cursor = 0

        while True:
            match = _CLASS_PATTERN.search(text, cursor)
            if not match:
                break

            body, end = _find_braced_block(text, match.start())
            if body is None:
                break

            cursor = end
            name = match.group("name")
            bases_text = match.group("bases") or ""
            bases = [_normalize_base_name(base) for base in bases_text.split(",") if base.strip()]
            class_info = {
                "name": name,
                "base": bases[0] if bases else None,
                "direct_attribute": _parse_creation_attribute(match.group("attrs") or ""),
                "files": [str(path.relative_to(root))],
                "property_fields": _parse_property_fields(body),
                "registered_fields": [
                    match_.group("field") for match_ in _REGISTER_PROPERTY_PATTERN.finditer(body)
                ],
                "non_serializable_fields": {
                    match_.group("field") for match_ in _NON_SERIALIZABLE_PATTERN.finditer(body)
                },
                "known_custom_properties": _parse_known_custom_properties(body),
            }

            existing = classes.get(name)
            classes[name] = (
                _merge_class_info(existing, class_info) if existing is not None else class_info
            )

    return classes


def _resolve_creation_attribute(
    class_name: str,
    classes: Dict[str, Dict[str, Any]],
    cache: Dict[str, Optional[Dict[str, Any]]],
) -> Optional[Dict[str, Any]]:
    if class_name in cache:
        return cache[class_name]

    class_info = classes.get(class_name)
    if class_info is None:
        cache[class_name] = None
        return None

    attribute = class_info.get("direct_attribute")
    if attribute:
        cache[class_name] = dict(attribute)
        return cache[class_name]

    base_name = class_info.get("base")
    if base_name:
        inherited = _resolve_creation_attribute(base_name, classes, cache)
        if inherited:
            cache[class_name] = dict(inherited)
            return cache[class_name]

    cache[class_name] = None
    return None


def _build_lineage(class_name: str, classes: Dict[str, Dict[str, Any]]) -> List[str]:
    lineage: List[str] = []
    seen = set()
    current = class_name

    while current and current not in seen:
        seen.add(current)
        lineage.append(current)
        current = classes.get(current, {}).get("base")

    return lineage


def _infer_module_kind(class_name: str, lineage: List[str], attribute: Dict[str, Any]) -> str:
    if "BaseScript" in lineage:
        return "script"
    if attribute.get("attribute") == "CreationService" or "Service" in lineage:
        return "service"
    if "UIObject" in lineage:
        return "ui"
    if "SceneObject" in lineage:
        return "scene"
    if class_name in {"Picture", "Sound", "Music", "Video", "Effect", "UIPackageObject"}:
        return "asset"
    return "object"


def _build_properties(
    class_name: str,
    classes: Dict[str, Dict[str, Any]],
    cache: Dict[str, List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    if class_name in cache:
        return cache[class_name]

    class_info = classes.get(class_name)
    if class_info is None:
        cache[class_name] = []
        return []

    properties: List[Dict[str, Any]] = []
    base_name = class_info.get("base")
    if base_name:
        properties.extend(copy.deepcopy(_build_properties(base_name, classes, cache)))

    properties_by_name = {item["name"]: item for item in properties}
    field_map = class_info.get("property_fields", {})
    non_serializable_fields = class_info.get("non_serializable_fields", set())

    for field_name in class_info.get("registered_fields", []):
        field_info = field_map.get(field_name)
        if not field_info:
            continue

        property_name = field_info["name"]
        property_entry = {
            "field": field_name,
            "name": property_name,
            "type": field_info["type"],
            "property_class": field_info["property_class"],
            "serializable": field_name not in non_serializable_fields,
        }

        if property_name in properties_by_name:
            properties_by_name[property_name].update(property_entry)
        else:
            properties.append(property_entry)
            properties_by_name[property_name] = property_entry

    cache[class_name] = properties
    return cache[class_name]


def _merge_compat_properties(
    base_properties: List[Dict[str, Any]],
    compat_properties: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    merged = copy.deepcopy(base_properties)
    names = {prop["name"] for prop in merged}

    for prop in compat_properties:
        if prop["name"] in names:
            continue
        names.add(prop["name"])
        merged.append(copy.deepcopy(prop))

    return merged


@lru_cache(maxsize=1)
def load_script_workspace_definitions(root: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    script_root = root or _SCRIPT_ROOT
    if script_root is None or not script_root.exists():
        return {}

    classes = _parse_script_classes(script_root)
    attribute_cache: Dict[str, Optional[Dict[str, Any]]] = {}
    property_cache: Dict[str, List[Dict[str, Any]]] = {}
    definitions: Dict[str, Dict[str, Any]] = {}

    for class_name, class_info in classes.items():
        attribute = _resolve_creation_attribute(class_name, classes, attribute_cache)
        if not attribute:
            continue

        lineage = _build_lineage(class_name, classes)
        properties = copy.deepcopy(_build_properties(class_name, classes, property_cache))
        known_custom_properties = copy.deepcopy(class_info.get("known_custom_properties", []))
        definitions[class_name] = {
            "name": class_name,
            "base": class_info.get("base"),
            "lineage": lineage,
            "kind": _infer_module_kind(class_name, lineage, attribute),
            "is_service": attribute.get("attribute") == "CreationService",
            "is_container": bool(attribute.get("is_container", False)),
            "properties": properties,
            "property_names": [prop["name"] for prop in properties],
            "known_custom_properties": known_custom_properties,
            "files": copy.deepcopy(class_info.get("files", [])),
            "source": "script",
        }

    for module_name, compat in _COMPAT_MODULE_DEFINITIONS.items():
        if module_name in definitions:
            continue

        base_name = compat.get("base")
        base_definition = definitions.get(base_name, {})
        base_properties = base_definition.get("properties", [])
        properties = _merge_compat_properties(base_properties, compat.get("properties", []))
        lineage = [module_name]
        if base_name:
            lineage.extend(base_definition.get("lineage", [base_name]))

        definitions[module_name] = {
            "name": module_name,
            "base": base_name,
            "lineage": lineage,
            "kind": compat.get("kind", "object"),
            "is_service": False,
            "is_container": bool(base_definition.get("is_container", False)),
            "properties": properties,
            "property_names": [prop["name"] for prop in properties],
            "known_custom_properties": copy.deepcopy(compat.get("known_custom_properties", [])),
            "files": [],
            "source": compat.get("source", "compat-fallback"),
            "description": compat.get("description", ""),
        }

    return definitions


# Keep the extraction implementations available for explicit maintenance calls,
# but make the default runtime path use committed internal snapshots only.
_extract_script_block_definitions_from_source = load_script_block_definitions
_extract_script_workspace_definitions_from_source = load_script_workspace_definitions


@lru_cache(maxsize=1)
def load_script_block_definitions(root: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    if root is not None:
        return _extract_script_block_definitions_from_source(root)
    return copy.deepcopy(SCRIPT_BLOCK_DEFINITIONS)


@lru_cache(maxsize=1)
def load_script_workspace_definitions(root: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    if root is not None:
        return _extract_script_workspace_definitions_from_source(root)
    return copy.deepcopy(SCRIPT_WORKSPACE_DEFINITIONS)
