"""
Workspace-level BlockScript operations.
"""

from __future__ import annotations

import copy
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from definitions.block_models import collect_block_object_type_errors, validate_block_structure
from definitions.workspace_schema import (
    collect_project_policy_errors,
    collect_script_entries,
    get_project_policy,
    iter_workspace_heads,
    resolve_script_context,
    resolve_script,
    walk_blocks,
)


def _resolve_workspace_path(file_path: str, workspace_root: Optional[Path] = None) -> Path:
    if workspace_root:
        root = workspace_root.resolve()
        full_path = (root / file_path).resolve()
        if full_path != root and root not in full_path.parents:
            raise ValueError(f"Path escapes workspace root: {file_path}")
        return full_path
    return Path(file_path).resolve()


def clone_workspace(workspace_data: Dict[str, Any]) -> Dict[str, Any]:
    return copy.deepcopy(workspace_data)


def set_param_value(entry_type: str, entry: Dict[str, Any], value: Any) -> None:
    if entry_type == "columns":
        if isinstance(value, dict):
            entry["type"] = "block"
            entry["value"] = value
        elif isinstance(value, list):
            # 保持 JSON 数组原样写入，不转 str（str([...]) 会产生 Python repr 格式字符串）
            entry["value"] = value
        else:
            entry["value"] = str(value)
        return

    if isinstance(value, dict):
        entry["type"] = "block"
        entry["val"] = value
    elif isinstance(value, list):
        # 保持 JSON 数组原样写入，不转 str
        entry["val"] = value
    else:
        entry["type"] = entry.get("type", "var")
        entry["val"] = str(value)


def append_section_child(section: Dict[str, Any], child_block: Dict[str, Any]) -> None:
    if "children" in section:
        section.setdefault("children", []).append(copy.deepcopy(child_block))
        return

    if section.get("child"):
        current = section["child"]
        while isinstance(current, dict) and current.get("next"):
            current = current["next"]
        current["next"] = copy.deepcopy(child_block)
        return

    if "params" in section:
        section["children"] = [copy.deepcopy(child_block)]
    else:
        section["child"] = copy.deepcopy(child_block)


async def load_workspace_file(file_path: str, workspace_root: Optional[Path] = None) -> Dict[str, Any]:
    full_path = _resolve_workspace_path(file_path, workspace_root)

    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {full_path}")

    if full_path.suffix != ".ws":
        raise ValueError(f"Not a .ws file: {full_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "success": True,
        "file_path": str(full_path),
        "data": data,
    }


async def save_workspace_file(
    file_path: str,
    content: Dict[str, Any],
    workspace_root: Optional[Path] = None,
    create_backup: bool = True,
    validate_before_save: bool = True,
) -> str:
    full_path = _resolve_workspace_path(file_path, workspace_root)
    full_path.parent.mkdir(parents=True, exist_ok=True)

    if validate_before_save:
        from handlers.validation_operations import validate_workspace

        validation = validate_workspace(content)
        if not validation.get("valid", False):
            errors = validation.get("errors", [])
            preview = "; ".join(str(error) for error in errors[:5])
            if len(errors) > 5:
                preview += f"; ... {len(errors) - 5} more"
            raise ValueError(f"Workspace validation failed before save: {preview}")

    if create_backup and full_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = full_path.with_suffix(f".backup_{timestamp}.ws")
        shutil.copy2(full_path, backup_path)

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    return f"File saved successfully: {full_path}"


def get_fragments(workspace_data: Dict[str, object]) -> List[Dict[str, object]]:
    result: List[Dict[str, object]] = []
    for source, script in collect_script_entries(workspace_data):
        for index, fragment in enumerate(script.get("fragments", [])):
            result.append(
                {
                    "index": index,
                    "source": source,
                    "position": fragment.get("pos", ["0", "0"]),
                    "head_define": fragment.get("head", {}).get("define", "Unknown"),
                    "has_next": "next" in fragment.get("head", {}),
                }
            )
    return result


def _collect_declared_myblock_names(workspace_data: Dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for _, script in collect_script_entries(workspace_data):
        for myblock in script.get("myblocks", []):
            name = myblock.get("name")
            if isinstance(name, str) and name:
                names.add(name)
    return names


def _list_myblock_parameters(myblock: Dict[str, Any]) -> List[Dict[str, str]]:
    columns = myblock.get("columns", [])
    if isinstance(columns, list) and columns:
        parameters: List[Dict[str, str]] = []
        for column in columns:
            if not isinstance(column, dict):
                continue

            column_type = column.get("type")
            if column_type == "Label":
                continue

            data = column.get("data", {})
            if not isinstance(data, dict):
                data = {}

            parameters.append(
                {
                    "name": data.get("name", "param"),
                    "type": "logical" if column_type == "Logical" else "value",
                }
            )
        return parameters

    legacy_params = myblock.get("params", [])
    if isinstance(legacy_params, list):
        return [
            {
                "name": param.get("name", "param"),
                "type": param.get("type", "value"),
            }
            for param in legacy_params
            if isinstance(param, dict)
        ]

    return []


def _existing_myblock_display_names(script: Dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for myblock in script.get("myblocks", []):
        if not isinstance(myblock, dict):
            continue
        display_name = myblock.get("displayName")
        if isinstance(display_name, str) and display_name:
            names.add(display_name)
    return names


def _make_unique_myblock_name(script: Dict[str, Any], script_id: str, base_name: str) -> str:
    existing = {
        myblock.get("name")
        for myblock in script.get("myblocks", [])
        if isinstance(myblock, dict) and isinstance(myblock.get("name"), str)
    }

    suffix = 0
    while True:
        name_part = base_name if suffix == 0 else f"{base_name}{suffix}"
        candidate = f"{script_id}/{name_part}/myblockdefine"
        if candidate not in existing:
            return candidate
        suffix += 1


def _build_myblock_columns(parameters: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    columns: List[Dict[str, Any]] = []
    for param in parameters:
        name = param.get("name", "param")
        param_type = str(param.get("type", "value")).lower()
        if param_type in {"logical", "bool", "boolean"}:
            columns.append({"type": "Logical", "data": {"name": name}})
        else:
            columns.append({"type": "Variable", "data": {"name": name, "customPopup": 0}})
    return columns


def _ensure_fragment_head_allowed(
    workspace_data: Dict[str, Any],
    script_id: Optional[str],
    head: Dict[str, Any],
    purpose: str,
) -> None:
    declared_myblocks = _collect_declared_myblock_names(workspace_data)
    is_valid, error_message = validate_block_structure(
        head,
        allowed_custom_defines=declared_myblocks,
        allow_unsupported_defines=False,
    )
    if not is_valid:
        raise ValueError(f"{purpose} rejected invalid block head: {error_message}")

    context = resolve_script_context(workspace_data, script_id, purpose)
    owner_type = context.get("owner_type")
    owner_block_types = context.get("owner_block_types")
    errors = collect_block_object_type_errors(
        head,
        owner_block_types if owner_block_types else owner_type,
        "fragment.head",
        owner_label=owner_type,
    )
    if errors:
        raise ValueError(f"{purpose} rejected block head: {errors[0]}")

    project_policy_errors = collect_project_policy_errors(
        head,
        get_project_policy(workspace_data),
        "fragment.head",
    )
    if project_policy_errors:
        raise ValueError(f"{purpose} rejected block head: {project_policy_errors[0]}")


def add_fragment(
    workspace_data: Dict[str, object],
    fragment: Dict[str, object],
    script_id: str | None = None,
) -> Dict[str, object]:
    if "pos" not in fragment:
        raise ValueError("Fragment must have 'pos' field")
    if "head" not in fragment:
        raise ValueError("Fragment must have 'head' field")
    if not isinstance(fragment["head"], dict):
        raise ValueError("Fragment 'head' must be a dictionary")

    updated_data = clone_workspace(workspace_data)
    _ensure_fragment_head_allowed(updated_data, script_id, fragment["head"], "add_fragment")
    target_script = resolve_script(updated_data, script_id, "add_fragment")
    target_script.setdefault("fragments", [])
    target_script["fragments"].append(fragment)
    return updated_data


def remove_fragment(
    workspace_data: Dict[str, object],
    fragment_index: int,
    script_id: str | None = None,
) -> Dict[str, object]:
    target_script = resolve_script(workspace_data, script_id, "remove_fragment")
    fragments = target_script.get("fragments", [])
    if fragment_index < 0 or fragment_index >= len(fragments):
        raise IndexError(f"Fragment index {fragment_index} out of range (0-{len(fragments)-1})")

    updated_data = clone_workspace(workspace_data)
    updated_script = resolve_script(updated_data, script_id, "remove_fragment")
    updated_script["fragments"].pop(fragment_index)
    return updated_data


def update_fragment_position(
    workspace_data: Dict[str, object],
    fragment_index: int,
    position: List[str],
    script_id: str | None = None,
) -> Dict[str, object]:
    target_script = resolve_script(workspace_data, script_id, "update_fragment_position")
    fragments = target_script.get("fragments", [])
    if fragment_index < 0 or fragment_index >= len(fragments):
        raise IndexError(f"Fragment index {fragment_index} out of range")
    if not isinstance(position, list) or len(position) != 2:
        raise ValueError("Position must be a list of 2 strings [x, y]")

    updated_data = clone_workspace(workspace_data)
    updated_script = resolve_script(updated_data, script_id, "update_fragment_position")
    updated_script["fragments"][fragment_index]["pos"] = position
    return updated_data


def create_myblock(
    workspace_data: Dict[str, Any],
    name: str,
    display_name: str,
    parameters: Optional[List[Dict[str, str]]] = None,
    yield_enabled: bool = True,
    script_id: Optional[str] = None,
) -> Dict[str, Any]:
    if parameters is None:
        parameters = []

    updated_data = clone_workspace(workspace_data)
    target_script = resolve_script(updated_data, script_id, "create_myblock")
    project_policy = get_project_policy(updated_data)

    if project_policy.get("is_end_user_mode"):
        if project_policy.get("show_myblock") is False:
            raise ValueError("create_myblock rejected custom blocks because showmyblock=false in end-user mode")
        if display_name.startswith("#"):
            raise ValueError(
                "create_myblock rejected custom block because displayName starting with '#' is hidden in end-user mode"
            )

    resolved_script_id = target_script.get("id", str(uuid.uuid4()))
    if display_name in _existing_myblock_display_names(target_script):
        raise ValueError(f"create_myblock rejected duplicate displayName: {display_name}")

    myblock_name = _make_unique_myblock_name(target_script, resolved_script_id, name)

    myblock_def = {
        "name": myblock_name,
        "displayName": display_name,
        "columns": _build_myblock_columns(parameters),
        "wrapBlockName": "",
    }

    if not yield_enabled:
        myblock_def["yield"] = False

    myblock_def["fragment"] = {
        "pos": ["100", "100"],
        "head": {
            "define": myblock_name,
            "sections": [{"children": []}],
        },
    }

    target_script.setdefault("myblocks", [])
    target_script["myblocks"].append(myblock_def)

    return updated_data


def get_myblocks(workspace_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    result = []
    for source, script in collect_script_entries(workspace_data):
        for myblock in script.get("myblocks", []):
            parameters = _list_myblock_parameters(myblock) if isinstance(myblock, dict) else []
            result.append(
                {
                    "source": source,
                    "name": myblock.get("name", ""),
                    "displayName": myblock.get("displayName", ""),
                    "parameter_count": len(parameters),
                    "parameters": parameters,
                    "yield": myblock.get("yield", True),
                    "has_fragment": "fragment" in myblock,
                }
            )
    return result


def remove_myblock(
    workspace_data: Dict[str, Any],
    myblock_name: str,
    script_id: Optional[str] = None,
) -> Dict[str, Any]:
    updated_data = clone_workspace(workspace_data)
    target_script = resolve_script(updated_data, script_id, "remove_myblock")
    myblocks = target_script.get("myblocks", [])

    for index, myblock in enumerate(myblocks):
        if myblock.get("name") == myblock_name:
            myblocks.pop(index)
            return updated_data

    raise ValueError(f"MyBlock not found: {myblock_name}")


def update_myblock_fragment(
    workspace_data: Dict[str, Any],
    myblock_name: str,
    fragment: Dict[str, Any],
    script_id: Optional[str] = None,
) -> Dict[str, Any]:
    updated_data = clone_workspace(workspace_data)
    if "head" not in fragment or not isinstance(fragment["head"], dict):
        raise ValueError("MyBlock fragment must contain a dictionary 'head'")
    if fragment["head"].get("define") != myblock_name:
        raise ValueError(
            f"update_myblock_fragment rejected fragment head define {fragment['head'].get('define')} "
            f"for myblock {myblock_name}"
        )
    _ensure_fragment_head_allowed(
        updated_data,
        script_id,
        fragment["head"],
        "update_myblock_fragment",
    )
    target_script = resolve_script(updated_data, script_id, "update_myblock_fragment")

    for myblock in target_script.get("myblocks", []):
        if myblock.get("name") == myblock_name:
            myblock["fragment"] = copy.deepcopy(fragment)
            return updated_data

    raise ValueError(f"MyBlock not found: {myblock_name}")


def create_myblock_call(
    myblock_name: str,
    parameter_values: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    if parameter_values is None:
        parameter_values = []

    call_block = {
        "define": myblock_name,
        "sections": [{"params": []}],
    }

    for value in parameter_values:
        if isinstance(value, dict):
            call_block["sections"][0]["params"].append({"type": "block", "val": value})
        else:
            call_block["sections"][0]["params"].append({"type": "var", "val": str(value)})

    return call_block


def find_myblock_usages(workspace_data: Dict[str, Any], myblock_name: str) -> List[Dict[str, Any]]:
    usages = []

    for source, head_path, head in iter_workspace_heads(workspace_data):
        walked: List[tuple[str, Dict[str, Any]]] = []
        walk_blocks(head, head_path, walked)
        for location, block in walked:
            if block.get("define") == myblock_name:
                if location == head_path and ".myblocks[" in head_path:
                    continue
                usages.append(
                    {
                        "source": source,
                        "location": location,
                        "block": block,
                    }
                )

    return usages
