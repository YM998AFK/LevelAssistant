"""
Block operations.
"""

import copy
from typing import Any, Dict, List, Optional, Union

from definitions.block_models import BlockType, get_block_type_info
from definitions.workspace_schema import iter_param_entries

from .workspace_operations import append_section_child, set_param_value


def _block_allows_child_sections(block_info: Optional[Dict[str, Any]]) -> bool:
    if not block_info:
        return False

    if block_info.get("has_branch"):
        return True

    return block_info.get("type") == BlockType.TRIGGER


def create_block(
    block_define: str,
    parameters: Optional[Dict[str, Any]] = None,
    position: Optional[List[str]] = None,
) -> Dict[str, Any]:
    block_info = get_block_type_info(block_define)
    if not block_info:
        raise ValueError(f"Unknown block define: {block_define}")

    block: Dict[str, Any] = {"define": block_define}
    param_defs = block_info.get("parameters", [])
    first_section: Dict[str, Any] = {}

    if param_defs:
        first_section["params"] = []
        for param_def in param_defs:
            param_name = param_def.get("name")
            default_value = param_def.get("default", "")
            param_value = parameters.get(param_name, default_value) if parameters else default_value

            if isinstance(param_value, dict):
                first_section["params"].append({"type": "block", "val": param_value})
            elif isinstance(param_value, list):
                # 保持 JSON 数组原样写入，不转 str
                first_section["params"].append({"type": "var", "val": param_value})
            else:
                value_type = "var"
                if param_def.get("type") == "boolean":
                    value_type = "boolean"
                first_section["params"].append({"type": value_type, "val": str(param_value)})

    if _block_allows_child_sections(block_info):
        first_section["children"] = []

    if first_section:
        block["sections"] = [first_section]

    if block_info.get("has_branch"):
        branch_count = block_info.get("branch_count", 1)
        block.setdefault("sections", [])
        for _ in range(1, branch_count):
            block["sections"].append({"children": []})

    if position:
        block["_position"] = position

    return block


def get_block_info(block: Dict[str, Any]) -> Dict[str, Any]:
    define = block.get("define", "")
    block_def = get_block_type_info(define)

    info = {
        "define": define,
        "type": block_def.get("type").value if block_def and block_def.get("type") else "Unknown",
        "category": block_def.get("category").value if block_def and block_def.get("category") else "Unknown",
        "description": block_def.get("description", "") if block_def else "",
        "return_type": block_def.get("return_type") if block_def else None,
        "has_next": "next" in block,
        "has_branches": bool(block_def and block_def.get("has_branch")),
        "parameter_count": 0,
        "parameters": [],
    }

    sections = block.get("sections", [])
    if sections:
        first_section = sections[0]
        for entry_type, _, entry in iter_param_entries(first_section):
            if entry.get("type") != "label":
                value = entry.get("value") if entry_type == "columns" else entry.get("val")
                info["parameters"].append({"type": entry.get("type", "value"), "value": value})
                info["parameter_count"] += 1

    return info


def modify_block_parameter(
    block: Dict[str, Any],
    parameter_index: int,
    value: Union[str, int, float, Dict[str, Any]],
) -> Dict[str, Any]:
    updated_block = copy.deepcopy(block)
    sections = updated_block.get("sections", [])
    if not sections:
        raise ValueError("Block has no sections")

    param_idx = 0
    for entry_type, _, entry in iter_param_entries(sections[0]):
        if entry.get("type") != "label":
            if param_idx == parameter_index:
                set_param_value(entry_type, entry, value)
                return updated_block
            param_idx += 1

    raise IndexError(f"Parameter index {parameter_index} out of range")


def append_block(block: Dict[str, Any], new_block: Dict[str, Any]) -> Dict[str, Any]:
    updated_block = copy.deepcopy(block)
    block_info = get_block_type_info(updated_block.get("define", ""))

    for section in updated_block.get("sections", []):
        if "children" in section or "child" in section:
            append_section_child(section, new_block)
            return updated_block

    if _block_allows_child_sections(block_info):
        sections = updated_block.setdefault("sections", [])
        if not sections:
            sections.append({})

        target_section = sections[0]
        target_section.setdefault("children", [])
        append_section_child(target_section, new_block)
        return updated_block

    current = updated_block
    while "next" in current and current["next"]:
        current = current["next"]
    current["next"] = copy.deepcopy(new_block)
    return updated_block


def insert_block_child(
    block: Dict[str, Any],
    section_index: int,
    child_block: Dict[str, Any],
) -> Dict[str, Any]:
    updated_block = copy.deepcopy(block)
    block_info = get_block_type_info(updated_block.get("define", ""))
    sections = updated_block.setdefault("sections", [])

    if not sections and section_index == 0 and (_block_allows_child_sections(block_info) or not block_info):
        sections.append({})

    if section_index < 0 or section_index >= len(sections):
        raise IndexError(f"Section index {section_index} out of range")

    target_section = sections[section_index]
    if "children" not in target_section and "child" not in target_section:
        if block_info and not _block_allows_child_sections(block_info):
            raise ValueError(f"Block {updated_block.get('define', '')} does not support child blocks")
        target_section["children"] = []

    append_section_child(target_section, child_block)
    return updated_block
