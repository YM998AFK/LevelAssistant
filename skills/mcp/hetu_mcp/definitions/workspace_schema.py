"""
Workspace/module definitions and validation helpers for .ws project trees.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple
import re

from definitions.block_models import get_block_type_info
from definitions.script_definitions import load_script_workspace_definitions


MODULE_DEFINITIONS = load_script_workspace_definitions()

SCENE_ELEMENT_BLOCK_SUPPORT_SOURCE = "mcp-internal:definitions/workspace_schema.py"

SCENE_ELEMENT_BLOCK_TARGET_TYPES: Dict[str, List[str]] = {
    "Scene": ["Scene"],
    "CameraService": ["CameraService"],
    "ImageSet": ["ImageSet"],
    # Sprite3DAPI validates MeshPart blocks against the Part target type.
    "MeshPart": ["Part"],
    "Avatar": ["Avatar"],
    "Character": ["Character"],
    "PartSet": ["PartSet"],
    "QuestObject": ["QuestObject"],
    "Quad": ["Quad"],
}

SCENE_ELEMENT_SUPPORTED_BLOCK_COUNTS: Dict[str, int] = {
    "Scene": 14,
    "CameraService": 45,
    "ImageSet": 59,
    "MeshPart": 73,
    "Avatar": 45,
    "Character": 53,
    "PartSet": 71,
    "QuestObject": 5,
    "Quad": 63,
}

_CUSTOM_VALUE_TYPES = {
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

_PROJECT_KNOWN_FIELDS = {
    "name",
    "desc",
    "icon",
    "author",
    "created",
    "modified",
    "type",
    "version",
    "stageType",
    "scene",
    "agents",
    "assets",
    "res",
    "showmyblock",
    "whitelist",
    "operationUIs",
    "dialogues",
    "editorScene",
    "sceneData",
    "projectMode",
}

_END_USER_PROJECT_TYPES = {0, 2, 4}
_END_USER_HIDDEN_CATEGORIES = {"magic", "experiment"}

# Accept plain decimal strings and scientific notation emitted by real `.ws` data.
_NUMERIC_RE = re.compile(r"^-?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?$")


def get_module_type_info(type_name: str) -> Optional[Dict[str, Any]]:
    return MODULE_DEFINITIONS.get(type_name)


def get_scene_element_block_target_types(type_name: Optional[str]) -> List[str]:
    if not isinstance(type_name, str) or not type_name:
        return []

    target_types = SCENE_ELEMENT_BLOCK_TARGET_TYPES.get(type_name)
    if target_types is None:
        return [type_name]
    return list(target_types)


def get_scene_element_block_support_info(type_name: str) -> Optional[Dict[str, Any]]:
    target_types = SCENE_ELEMENT_BLOCK_TARGET_TYPES.get(type_name)
    if target_types is None:
        return None

    return {
        "scene_element_type": type_name,
        "target_types": list(target_types),
        "supported_block_count": SCENE_ELEMENT_SUPPORTED_BLOCK_COUNTS.get(type_name, 0),
        "source": SCENE_ELEMENT_BLOCK_SUPPORT_SOURCE,
    }


def get_scene_element_block_support_matrix() -> Dict[str, Dict[str, Any]]:
    return {
        type_name: support_info
        for type_name in SCENE_ELEMENT_BLOCK_TARGET_TYPES
        if (support_info := get_scene_element_block_support_info(type_name)) is not None
    }


def looks_like_project_workspace(node: Any) -> bool:
    return isinstance(node, dict) and any(
        key in node
        for key in ("scene", "agents", "assets", "res", "dialogues", "editorScene", "projectMode")
    )


def looks_like_module_node(node: Any) -> bool:
    return isinstance(node, dict) and isinstance(node.get("type"), str) and (
        isinstance(node.get("props"), dict)
        or node.get("type") == "BlockScript"
        or "children" in node
        or "fragments" in node
        or "myblocks" in node
    )


def is_blockscript(node: Any) -> bool:
    return isinstance(node, dict) and (
        node.get("type") == "BlockScript"
        or "fragments" in node
        or "myblocks" in node
        or "uiState" in node
    )


def is_workspace_project(node: Any) -> bool:
    return looks_like_project_workspace(node)


def is_module_node(node: Any) -> bool:
    return isinstance(node, dict) and isinstance(node.get("type"), str) and (
        isinstance(node.get("props"), dict)
        or "children" in node
        or is_blockscript(node)
    )


def collect_blockscripts(node: Any) -> List[Dict[str, Any]]:
    blockscripts: List[Dict[str, Any]] = []

    def walk(current: Any) -> None:
        if isinstance(current, dict):
            if is_blockscript(current):
                blockscripts.append(current)
            for value in current.values():
                walk(value)
        elif isinstance(current, list):
            for item in current:
                walk(item)

    walk(node)
    deduped: List[Dict[str, Any]] = []
    seen_ids = set()
    for script in blockscripts:
        marker = id(script)
        if marker not in seen_ids:
            seen_ids.add(marker)
            deduped.append(script)
    return deduped


def get_script_id(script: Dict[str, Any], fallback: str = "root") -> str:
    return script.get("id", fallback)


def resolve_script(
    workspace_data: Dict[str, Any],
    script_id: Optional[str] = None,
    purpose: str = "operation",
) -> Dict[str, Any]:
    if is_blockscript(workspace_data):
        resolved_id = get_script_id(workspace_data)
        if script_id and script_id not in {"root", resolved_id}:
            raise ValueError(f"script_id '{script_id}' does not match the provided BlockScript")
        return workspace_data

    scripts = collect_blockscripts(workspace_data)
    if not scripts:
        raise ValueError(f"No BlockScript found for {purpose}")

    if script_id:
        for script in scripts:
            if get_script_id(script) == script_id:
                return script
        raise ValueError(f"BlockScript not found: {script_id}")

    if len(scripts) == 1:
        return scripts[0]

    raise ValueError(
        f"script_id is required for {purpose} because the workspace contains {len(scripts)} BlockScript nodes"
    )


def collect_script_entries(workspace_data: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
    if is_blockscript(workspace_data):
        return [(get_script_id(workspace_data), workspace_data)]
    return [(get_script_id(script), script) for script in collect_blockscripts(workspace_data)]


def collect_declared_myblocks(workspace_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    declared: Dict[str, Dict[str, Any]] = {}

    for source, script in collect_script_entries(workspace_data):
        for myblock in script.get("myblocks", []):
            if not isinstance(myblock, dict):
                continue

            name = myblock.get("name")
            if not isinstance(name, str) or not name:
                continue

            declared[name] = {
                "source": source,
                "displayName": myblock.get("displayName"),
                "myblock": myblock,
            }

    return declared


def resolve_owner_block_types(owner_type: Optional[str]) -> List[str]:
    return get_scene_element_block_target_types(owner_type)


def get_project_policy(workspace_data: Dict[str, Any]) -> Dict[str, Any]:
    if not is_workspace_project(workspace_data):
        return {
            "is_project": False,
            "is_end_user_mode": False,
            "show_myblock": True,
            "whitelist_enabled": False,
            "whitelist_defines": set(),
            "declared_myblocks": {},
        }

    project_type = workspace_data.get("type")
    is_end_user_mode = isinstance(project_type, int) and project_type in _END_USER_PROJECT_TYPES
    whitelist_defines = {
        block.get("define")
        for block in workspace_data.get("whitelist", [])
        if isinstance(block, dict) and isinstance(block.get("define"), str) and block.get("define")
    }

    return {
        "is_project": True,
        "project_type": project_type,
        "is_end_user_mode": is_end_user_mode,
        "show_myblock": workspace_data.get("showmyblock", True),
        "whitelist_enabled": bool(whitelist_defines),
        "whitelist_defines": whitelist_defines,
        "declared_myblocks": collect_declared_myblocks(workspace_data),
    }


def collect_project_policy_errors(
    block: Dict[str, Any],
    project_policy: Dict[str, Any],
    path: str = "block",
) -> List[str]:
    if not project_policy.get("is_end_user_mode"):
        return []

    errors: List[str] = []
    declared_myblocks = project_policy.get("declared_myblocks", {})
    show_myblock = project_policy.get("show_myblock", True)
    whitelist_enabled = project_policy.get("whitelist_enabled", False)
    whitelist_defines = project_policy.get("whitelist_defines", set())

    def walk(current: Any, current_path: str) -> None:
        if not isinstance(current, dict):
            return

        define = current.get("define")
        if not isinstance(define, str) or not define:
            return

        if define.endswith("/myblockdefine"):
            meta = declared_myblocks.get(define, {})
            display_name = meta.get("displayName")
            if show_myblock is False:
                errors.append(
                    f"{current_path} uses custom myblock {define}, which is hidden by showmyblock=false in end-user mode"
                )
            elif isinstance(display_name, str) and display_name.startswith("#"):
                errors.append(
                    f"{current_path} uses custom myblock {define}, which is hidden in end-user mode because displayName starts with '#'"
                )
        else:
            block_info = get_block_type_info(define)
            category = block_info.get("category") if block_info else None
            category_value = category.value if hasattr(category, "value") else None

            if category_value in _END_USER_HIDDEN_CATEGORIES:
                errors.append(
                    f"{current_path} uses {define}, which is hidden in end-user mode because category {category_value} is disabled"
                )
            elif whitelist_enabled and define not in whitelist_defines:
                errors.append(
                    f"{current_path} uses {define}, which is not present in project whitelist for end-user mode"
                )

        sections = current.get("sections", [])
        if isinstance(sections, list):
            for section_index, section in enumerate(sections):
                if not isinstance(section, dict):
                    continue

                params = section.get("params", [])
                if isinstance(params, list):
                    for param_index, entry in enumerate(params):
                        if not isinstance(entry, dict):
                            continue
                        nested = entry.get("val")
                        if isinstance(nested, dict):
                            walk(nested, f"{current_path}.sections[{section_index}].params[{param_index}].val")

                columns = section.get("columns", [])
                if isinstance(columns, list):
                    for column_index, entry in enumerate(columns):
                        if not isinstance(entry, dict):
                            continue
                        nested = entry.get("value")
                        if isinstance(nested, dict):
                            walk(
                                nested,
                                f"{current_path}.sections[{section_index}].columns[{column_index}].value",
                            )

                children = section.get("children", [])
                if isinstance(children, list):
                    for child_index, child in enumerate(children):
                        walk(child, f"{current_path}.sections[{section_index}].children[{child_index}]")

                child = section.get("child")
                if isinstance(child, dict):
                    walk(child, f"{current_path}.sections[{section_index}].child")

        next_block = current.get("next")
        if isinstance(next_block, dict):
            walk(next_block, f"{current_path}.next")

    walk(block, path)
    return errors


def collect_script_contexts(workspace_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    if is_blockscript(workspace_data):
        return [
            {
                "source": get_script_id(workspace_data),
                "script_path": "root",
                "owner_type": None,
                "owner_block_types": [],
                "owner_path": None,
                "script": workspace_data,
            }
        ]

    contexts: List[Dict[str, Any]] = []

    def walk_module(module: Dict[str, Any], path: str) -> None:
        if not is_module_node(module) or is_blockscript(module):
            return

        children = module.get("children", [])
        if not isinstance(children, list):
            return

        owner_type = module.get("type") if isinstance(module.get("type"), str) else None
        owner_block_types = resolve_owner_block_types(owner_type)
        for index, child in enumerate(children):
            child_path = f"{path}.children[{index}]"
            if is_blockscript(child):
                contexts.append(
                    {
                        "source": get_script_id(child, child_path),
                        "script_path": child_path,
                        "owner_type": owner_type,
                        "owner_block_types": owner_block_types,
                        "owner_path": path,
                        "script": child,
                    }
                )
                continue

            if is_module_node(child):
                walk_module(child, child_path)

    if is_module_node(workspace_data):
        walk_module(workspace_data, "root")
        return contexts

    if is_workspace_project(workspace_data):
        for key in ("scene", "agents", "assets"):
            module = workspace_data.get(key)
            if is_module_node(module):
                walk_module(module, key)

    return contexts


def resolve_script_context(
    workspace_data: Dict[str, Any],
    script_id: Optional[str] = None,
    purpose: str = "operation",
) -> Dict[str, Any]:
    contexts = collect_script_contexts(workspace_data)
    if not contexts:
        raise ValueError(f"No BlockScript found for {purpose}")

    if script_id:
        for context in contexts:
            if context["source"] == script_id:
                return context
        raise ValueError(f"BlockScript not found: {script_id}")

    if len(contexts) == 1:
        return contexts[0]

    raise ValueError(
        f"script_id is required for {purpose} because the workspace contains {len(contexts)} BlockScript nodes"
    )


def walk_modules(module: Dict[str, Any], path: str, results: List[Tuple[str, Dict[str, Any]]]) -> None:
    if not is_module_node(module):
        return

    results.append((path, module))
    children = module.get("children", [])
    if not isinstance(children, list):
        return

    for index, child in enumerate(children):
        if is_module_node(child):
            walk_modules(child, f"{path}.children[{index}]", results)


def collect_module_entries(workspace_data: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
    results: List[Tuple[str, Dict[str, Any]]] = []

    if is_module_node(workspace_data):
        walk_modules(workspace_data, "root", results)
        return results

    if is_workspace_project(workspace_data):
        for key in ("scene", "agents", "assets"):
            module = workspace_data.get(key)
            if is_module_node(module):
                walk_modules(module, key, results)

    return results


def iter_script_heads(
    script: Dict[str, Any],
    source: str,
    include_myblocks: bool = True,
) -> Iterator[Tuple[str, str, Dict[str, Any]]]:
    for index, fragment in enumerate(script.get("fragments", [])):
        if not isinstance(fragment, dict):
            continue

        head = fragment.get("head")
        if isinstance(head, dict):
            yield source, f"{source}.fragments[{index}].head", head

    if not include_myblocks:
        return

    for index, myblock in enumerate(script.get("myblocks", [])):
        if not isinstance(myblock, dict):
            continue

        fragment = myblock.get("fragment")
        if not isinstance(fragment, dict):
            continue

        head = fragment.get("head")
        if isinstance(head, dict):
            yield source, f"{source}.myblocks[{index}].fragment.head", head


def iter_workspace_heads(
    workspace_data: Dict[str, Any],
    include_myblocks: bool = True,
) -> Iterator[Tuple[str, str, Dict[str, Any]]]:
    for source, script in collect_script_entries(workspace_data):
        yield from iter_script_heads(script, source, include_myblocks)


def iter_param_entries(section: Dict[str, Any]) -> Iterable[Tuple[str, int, Dict[str, Any]]]:
    for index, entry in enumerate(section.get("columns", [])):
        if isinstance(entry, dict):
            yield "columns", index, entry
    for index, entry in enumerate(section.get("params", [])):
        if isinstance(entry, dict):
            yield "params", index, entry


def get_embedded_block(entry_type: str, entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if entry_type == "columns":
        value = entry.get("value")
        return value if isinstance(value, dict) else None

    if entry.get("type") == "block" and isinstance(entry.get("val"), dict):
        return entry["val"]
    return None


def iter_child_blocks(section: Dict[str, Any]) -> Iterable[Tuple[str, int, Dict[str, Any]]]:
    child = section.get("child")
    if isinstance(child, dict):
        yield "child", 0, child

    for index, child_block in enumerate(section.get("children", [])):
        if isinstance(child_block, dict):
            yield "children", index, child_block


def walk_blocks(block: Dict[str, Any], path: str, results: List[Tuple[str, Dict[str, Any]]]) -> None:
    if not block:
        return

    results.append((path, block))

    sections = block.get("sections", [])
    for section_index, section in enumerate(sections):
        for entry_type, entry_index, entry in iter_param_entries(section):
            nested = get_embedded_block(entry_type, entry)
            if nested:
                key = "value" if entry_type == "columns" else "val"
                walk_blocks(
                    nested,
                    f"{path}.sections[{section_index}].{entry_type}[{entry_index}].{key}",
                    results,
                )

        for child_type, child_index, child in iter_child_blocks(section):
            if child_type == "child":
                child_path = f"{path}.sections[{section_index}].child"
            else:
                child_path = f"{path}.sections[{section_index}].children[{child_index}]"
            walk_blocks(child, child_path, results)

    next_block = block.get("next")
    if isinstance(next_block, dict):
        walk_blocks(next_block, f"{path}.next", results)


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return (_is_integer(value) or isinstance(value, float)) and not isinstance(value, bool)


def _is_numeric_string(value: Any) -> bool:
    return isinstance(value, str) and bool(_NUMERIC_RE.fullmatch(value))


def _json_type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if value is None:
        return "null"
    return type(value).__name__


def _expected_json_type(value_type: str) -> str:
    if value_type == "integer":
        return "integer"
    if value_type == "float":
        return "numeric string"
    if value_type == "vector2":
        return "2-item numeric string array"
    if value_type == "vector3":
        return "3-item numeric string array"
    if value_type == "quaternion":
        return "4-item numeric string array"
    return value_type


def _format_value_for_error(value: Any) -> str:
    text = repr(value)
    if len(text) > 80:
        text = text[:77] + "..."
    return text


def _validate_scalar_sequence(value: Any, length: int) -> bool:
    if not isinstance(value, list) or len(value) != length:
        return False
    return all(_is_numeric_string(item) for item in value)


def _validate_property_value(value: Any, value_type: str) -> bool:
    if value_type == "string":
        return isinstance(value, str)
    if value_type == "boolean":
        return isinstance(value, bool)
    if value_type == "integer":
        return _is_integer(value)
    if value_type == "float":
        return _is_numeric_string(value)
    if value_type == "vector2":
        return _validate_scalar_sequence(value, 2)
    if value_type == "vector3":
        return _validate_scalar_sequence(value, 3)
    if value_type == "quaternion":
        return _validate_scalar_sequence(value, 4)
    if value_type == "color":
        return isinstance(value, str)
    if value_type == "object_ref":
        return isinstance(value, str)
    if value_type == "simple":
        return isinstance(value, (str, int, float, bool))
    if value_type == "simple_list":
        return isinstance(value, list) and all(
            isinstance(item, (str, int, float, bool)) for item in value
        )
    return True


def describe_property_value_error(path: str, value: Any, value_type: str) -> Optional[str]:
    if _validate_property_value(value, value_type):
        return None
    return (
        f"{path} must be {_expected_json_type(value_type)}; "
        f"got {_json_type_name(value)}: {_format_value_for_error(value)}"
    )


def _property_types_by_name(module_info: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {prop["name"]: prop for prop in module_info.get("properties", [])}


def _validate_custom_props(props2: Any, path: str) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(props2, dict):
        return [f"{path} must be an object"], warnings

    for key, entry in props2.items():
        entry_path = f"{path}.{key}"
        if not isinstance(entry, dict):
            errors.append(f"{entry_path} must be an object")
            continue

        value_type_name = entry.get("type")
        if not isinstance(value_type_name, str) or not value_type_name:
            errors.append(f"{entry_path}.type must be a non-empty string")
            continue

        if value_type_name not in _CUSTOM_VALUE_TYPES:
            warnings.append(f"{entry_path}.type uses unknown custom value type: {value_type_name}")
            continue

        if "value" not in entry:
            errors.append(f"{entry_path} missing required field: value")
            continue

        expected_type = _CUSTOM_VALUE_TYPES[value_type_name]
        error = describe_property_value_error(f"{entry_path}.value", entry["value"], expected_type)
        if error:
            errors.append(error)

    return errors, warnings


def validate_module_data(
    module: Any,
    path: str = "module",
    allow_unknown_types: bool = True,
) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    def visit(node: Any, node_path: str) -> None:
        if not isinstance(node, dict):
            errors.append(f"{node_path} must be an object")
            return

        type_name = node.get("type")
        if not isinstance(type_name, str) or not type_name:
            errors.append(f"{node_path}.type must be a non-empty string")
            return

        module_info = get_module_type_info(type_name)
        if module_info is None:
            message = f"{node_path} uses unsupported module type: {type_name}"
            if allow_unknown_types:
                warnings.append(message)
            else:
                errors.append(message)

        if "id" not in node:
            errors.append(f"{node_path} missing required field: id")
        elif not isinstance(node["id"], str) or not node["id"]:
            errors.append(f"{node_path}.id must be a non-empty string")

        props = node.get("props")
        if props is not None and not isinstance(props, dict):
            errors.append(f"{node_path}.props must be an object")
        elif isinstance(props, dict) and module_info is not None:
            property_map = _property_types_by_name(module_info)
            for prop_name, prop_value in props.items():
                prop_info = property_map.get(prop_name)
                if prop_info is None:
                    warnings.append(f"{node_path}.props.{prop_name} is not defined in script metadata")
                    continue

                expected_type = prop_info.get("type", "unknown")
                error = describe_property_value_error(
                    f"{node_path}.props.{prop_name}",
                    prop_value,
                    expected_type,
                )
                if error:
                    errors.append(error)

        props2 = node.get("props2")
        if props2 is not None:
            custom_errors, custom_warnings = _validate_custom_props(props2, f"{node_path}.props2")
            errors.extend(custom_errors)
            warnings.extend(custom_warnings)

        children = node.get("children")
        if children is not None:
            if not isinstance(children, list):
                errors.append(f"{node_path}.children must be a list")
            else:
                for index, child in enumerate(children):
                    visit(child, f"{node_path}.children[{index}]")

    visit(module, path)
    return errors, warnings


def _validate_operation_ui_entry(entry: Any, path: str) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(entry, dict):
        return [f"{path} must be an object"], warnings

    for field in ("id", "param", "def"):
        if field not in entry:
            errors.append(f"{path} missing required field: {field}")
        elif not isinstance(entry[field], str):
            errors.append(f"{path}.{field} must be a string")

    if "pos" not in entry:
        errors.append(f"{path} missing required field: pos")
    elif not _validate_property_value(entry["pos"], "vector2"):
        errors.append(f"{path}.pos must be a 2D vector")

    define_name = entry.get("def")
    if isinstance(define_name, str) and define_name and not get_block_type_info(define_name):
        warnings.append(f"{path}.def uses unsupported block define: {define_name}")

    return errors, warnings


def _validate_dialogue_item(entry: Any, path: str) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(entry, dict):
        return [f"{path} must be an object"], warnings

    for field in ("who", "content", "audio"):
        if field not in entry:
            errors.append(f"{path} missing required field: {field}")
        elif not isinstance(entry[field], str):
            errors.append(f"{path}.{field} must be a string")

    if "autoDelay" not in entry:
        errors.append(f"{path} missing required field: autoDelay")
    elif not _is_number(entry["autoDelay"]):
        errors.append(f"{path}.autoDelay must be a number")

    if "anims" in entry:
        if not isinstance(entry["anims"], list) or not all(
            isinstance(item, str) for item in entry["anims"]
        ):
            errors.append(f"{path}.anims must be a list of strings")

    if "mouthAnim" in entry and not isinstance(entry["mouthAnim"], str):
        errors.append(f"{path}.mouthAnim must be a string")

    return errors, warnings


def _validate_dialogue_group(entry: Any, path: str) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(entry, dict):
        return [f"{path} must be an object"], warnings

    if "name" not in entry or not isinstance(entry["name"], str):
        errors.append(f"{path}.name must be a string")

    if "menu" in entry:
        if not isinstance(entry["menu"], list) or not all(isinstance(item, str) for item in entry["menu"]):
            errors.append(f"{path}.menu must be a list of strings")

    items = entry.get("items")
    if not isinstance(items, list):
        errors.append(f"{path}.items must be a list")
    else:
        for index, item in enumerate(items):
            item_errors, item_warnings = _validate_dialogue_item(item, f"{path}.items[{index}]")
            errors.extend(item_errors)
            warnings.extend(item_warnings)

    if "branches" in entry:
        if not isinstance(entry["branches"], list) or not all(
            isinstance(item, str) for item in entry["branches"]
        ):
            errors.append(f"{path}.branches must be a list of strings")

    if "nextGroup" in entry and not isinstance(entry["nextGroup"], str):
        errors.append(f"{path}.nextGroup must be a string")

    return errors, warnings


def _validate_dialogues(data: Any, path: str) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(data, dict):
        return [f"{path} must be an object"], warnings

    groups = data.get("DialogueGroups")
    if groups is None:
        warnings.append(f"{path} missing DialogueGroups")
        return errors, warnings

    if not isinstance(groups, list):
        errors.append(f"{path}.DialogueGroups must be a list")
        return errors, warnings

    for index, group in enumerate(groups):
        group_errors, group_warnings = _validate_dialogue_group(
            group,
            f"{path}.DialogueGroups[{index}]",
        )
        errors.extend(group_errors)
        warnings.extend(group_warnings)

    return errors, warnings


def _validate_editor_camera(data: Any, path: str) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(data, dict):
        return [f"{path} must be an object"], warnings

    if "name" not in data or not isinstance(data["name"], str):
        errors.append(f"{path}.name must be a string")
    if "position" not in data or not _validate_property_value(data["position"], "vector3"):
        errors.append(f"{path}.position must be a 3D vector")
    if "rotation" not in data or not _validate_property_value(data["rotation"], "quaternion"):
        errors.append(f"{path}.rotation must be a quaternion")
    if "fov" not in data or not _is_number(data["fov"]):
        errors.append(f"{path}.fov must be a number")

    return errors, warnings


def _validate_editor_scene(data: Any, path: str) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(data, dict):
        return [f"{path} must be an object"], warnings

    cameras = data.get("cameras")
    if cameras is not None:
        if not isinstance(cameras, list):
            errors.append(f"{path}.cameras must be a list")
        else:
            for index, camera in enumerate(cameras):
                camera_errors, camera_warnings = _validate_editor_camera(
                    camera,
                    f"{path}.cameras[{index}]",
                )
                errors.extend(camera_errors)
                warnings.extend(camera_warnings)

    edit_camera = data.get("editCamera")
    if edit_camera is not None:
        camera_errors, camera_warnings = _validate_editor_camera(edit_camera, f"{path}.editCamera")
        errors.extend(camera_errors)
        warnings.extend(camera_warnings)

    return errors, warnings


def _validate_scene_data(data: Any, path: str) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(data, dict):
        return [f"{path} must be an object"], warnings

    if "camerapos" not in data or not _validate_property_value(data["camerapos"], "vector3"):
        errors.append(f"{path}.camerapos must be a 3D vector")

    if "camerarot" not in data or not _validate_property_value(data["camerarot"], "quaternion"):
        errors.append(f"{path}.camerarot must be a quaternion")

    return errors, warnings


def validate_project_root(data: Any, path: str = "workspace") -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(data, dict):
        return [f"{path} must be an object"], warnings

    string_fields = ("name", "desc", "icon", "author")
    integer_fields = ("created", "modified", "type", "version", "stageType", "projectMode")

    for field in string_fields:
        if field in data and not isinstance(data[field], str):
            errors.append(f"{path}.{field} must be a string")

    for field in integer_fields:
        if field in data and not _is_integer(data[field]):
            errors.append(f"{path}.{field} must be an integer")

    for field in ("scene", "agents", "assets"):
        if field in data:
            if not looks_like_module_node(data[field]):
                errors.append(f"{path}.{field} must be a serialized module object")
        elif field == "scene":
            errors.append(f"{path} missing required field: scene")

    if "res" in data:
        if not isinstance(data["res"], list) or not all(_is_integer(item) for item in data["res"]):
            errors.append(f"{path}.res must be a list of integers")

    if "showmyblock" in data and not isinstance(data["showmyblock"], bool):
        errors.append(f"{path}.showmyblock must be a boolean")

    if "operationUIs" in data:
        if not isinstance(data["operationUIs"], list):
            errors.append(f"{path}.operationUIs must be a list")
        else:
            for index, entry in enumerate(data["operationUIs"]):
                entry_errors, entry_warnings = _validate_operation_ui_entry(
                    entry,
                    f"{path}.operationUIs[{index}]",
                )
                errors.extend(entry_errors)
                warnings.extend(entry_warnings)

    if "dialogues" in data:
        dialogue_errors, dialogue_warnings = _validate_dialogues(data["dialogues"], f"{path}.dialogues")
        errors.extend(dialogue_errors)
        warnings.extend(dialogue_warnings)

    if "editorScene" in data:
        editor_errors, editor_warnings = _validate_editor_scene(data["editorScene"], f"{path}.editorScene")
        errors.extend(editor_errors)
        warnings.extend(editor_warnings)

    if "sceneData" in data:
        scene_errors, scene_warnings = _validate_scene_data(data["sceneData"], f"{path}.sceneData")
        errors.extend(scene_errors)
        warnings.extend(scene_warnings)

    for key in data.keys():
        if key not in _PROJECT_KNOWN_FIELDS:
            warnings.append(f"{path}.{key} is not part of the known project schema")

    return errors, warnings


def get_module_documentation(type_name: str) -> str:
    module_info = get_module_type_info(type_name)
    if not module_info:
        return f"# {type_name}\n\nModule definition not found.\n"

    doc = f"# {type_name}\n\n"
    doc += f"**Kind**: {module_info.get('kind', 'object')}\n\n"
    doc += f"**Source**: {module_info.get('source', 'script')}\n\n"
    if module_info.get("base"):
        doc += f"**Base**: {module_info['base']}\n\n"
    if module_info.get("description"):
        doc += f"**Description**: {module_info['description']}\n\n"

    properties = module_info.get("properties", [])
    if properties:
        doc += "## Properties\n\n"
        for prop in properties:
            serializable = "yes" if prop.get("serializable", True) else "legacy/derived"
            doc += f"- `{prop['name']}`: {prop.get('type', 'unknown')} ({serializable})\n"
        doc += "\n"
    else:
        doc += "## Properties\n\nNone\n\n"

    custom_props = module_info.get("known_custom_properties", [])
    if custom_props:
        doc += "## Known Custom Properties\n\n"
        for prop in custom_props:
            doc += f"- `{prop['name']}`: {prop.get('type', 'unknown')}\n"
        doc += "\n"

    scene_element_support = get_scene_element_block_support_info(type_name)
    if scene_element_support:
        target_types = ", ".join(f"`{item}`" for item in scene_element_support["target_types"])
        doc += "## Scene Element Block Support\n\n"
        doc += f"- Block target types: {target_types}\n"
        doc += f"- Supported block count: {scene_element_support['supported_block_count']}\n"
        doc += f"- Source: `{scene_element_support['source']}`\n\n"

    doc += "## Example\n\n```json\n"
    doc += "{\n"
    doc += f'  "type": "{type_name}",\n'
    doc += '  "id": "example-id",\n'
    doc += '  "props": {\n'
    if properties:
        for prop in properties[:3]:
            example_value = {
                "string": '"value"',
                "boolean": "true",
                "integer": "0",
                "float": '"0"',
                "vector2": '["0", "0"]',
                "vector3": '["0", "0", "0"]',
                "quaternion": '["0", "0", "0", "1"]',
                "color": '"#FFFFFFFF"',
                "object_ref": '""',
                "simple": '"0"',
                "simple_list": '[]',
            }.get(prop.get("type", "unknown"), "null")
            doc += f'    "{prop["name"]}": {example_value},\n'
        doc = doc.rstrip(",\n") + "\n"
    doc += "  }\n"
    doc += "}\n```\n"

    return doc
