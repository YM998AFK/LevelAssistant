"""
Validation and query operations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from definitions.block_models import (
    collect_block_object_type_errors,
    get_block_type_info,
    validate_block_value_entry,
    validate_block_structure,
)
from definitions.resource_definitions import ensure_resource_data, is_valid_resource_id
from definitions.workspace_schema import (
    collect_declared_myblocks,
    collect_module_entries,
    collect_project_policy_errors,
    collect_script_contexts,
    collect_script_entries,
    describe_property_value_error,
    get_embedded_block,
    get_module_documentation as build_module_documentation,
    get_module_type_info,
    get_project_policy,
    get_scene_element_block_support_info,
    is_module_node,
    is_workspace_project,
    iter_child_blocks,
    iter_param_entries,
    iter_workspace_heads,
    validate_module_data,
    validate_project_root,
    walk_blocks,
)

_MYBLOCK_COLUMN_TYPES = {"Label", "FixedDroplist", "Logical", "Variable"}


def validate_block(block: Dict[str, Any]) -> Dict[str, Any]:
    warnings = _collect_block_warnings(block, "block")
    is_valid, error_message = validate_block_structure(
        block,
        allow_unsupported_defines=True,
    )

    result = {
        "valid": is_valid,
        "error": error_message if not is_valid else None,
        "warning_count": len(warnings),
        "warnings": warnings,
    }

    if is_valid:
        define = block.get("define", "")
        block_info = get_block_type_info(define)
        result["block_type"] = (
            block_info.get("type").value if block_info and block_info.get("type") else "Unknown"
        )
        result["category"] = (
            block_info.get("category").value if block_info and block_info.get("category") else "Unknown"
        )

    return result


def get_modules(workspace_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for path, module in collect_module_entries(workspace_data):
        props = module.get("props", {})
        module_info = get_module_type_info(module.get("type", ""))
        scene_element_support = get_scene_element_block_support_info(module.get("type", ""))
        results.append(
            {
                "type": module.get("type", "Unknown"),
                "id": module.get("id", ""),
                "name": props.get("Name", "") if isinstance(props, dict) else "",
                "path": path,
                "child_count": len(module.get("children", [])) if isinstance(module.get("children"), list) else 0,
                "kind": module_info.get("kind", "unknown") if module_info else "unknown",
                "source": module_info.get("source", "unknown") if module_info else "unknown",
                "scene_element_block_target_types": (
                    scene_element_support["target_types"] if scene_element_support else []
                ),
                "scene_element_supported_block_count": (
                    scene_element_support["supported_block_count"] if scene_element_support else None
                ),
            }
        )

    return results


def validate_module(module: Dict[str, Any]) -> Dict[str, Any]:
    errors, warnings = validate_module_data(module, "module")
    module_info = get_module_type_info(module.get("type", "")) if isinstance(module, dict) else None
    scene_element_support = (
        get_scene_element_block_support_info(module.get("type", ""))
        if isinstance(module, dict)
        else None
    )
    return {
        "valid": len(errors) == 0,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "module_type": module.get("type", "Unknown") if isinstance(module, dict) else "Unknown",
        "kind": module_info.get("kind", "unknown") if module_info else "unknown",
        "scene_element_block_target_types": (
            scene_element_support["target_types"] if scene_element_support else []
        ),
        "scene_element_supported_block_count": (
            scene_element_support["supported_block_count"] if scene_element_support else None
        ),
    }


def find_modules_by_type(workspace_data: Dict[str, Any], module_type: str) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for path, module in collect_module_entries(workspace_data):
        if module.get("type") != module_type:
            continue

        props = module.get("props", {})
        results.append(
            {
                "path": path,
                "module": module,
                "id": module.get("id", ""),
                "name": props.get("Name", "") if isinstance(props, dict) else "",
            }
        )

    return results


def get_module_documentation(module_type: str) -> str:
    return build_module_documentation(module_type)


def _collect_declared_myblock_names(workspace_data: Dict[str, Any]) -> set[str]:
    return set(collect_declared_myblocks(workspace_data).keys())


def _describe_block_warning(
    define: Any,
    path: str,
    allowed_custom_defines: set[str] | None = None,
) -> str | None:
    if not isinstance(define, str) or not define:
        return None

    if get_block_type_info(define):
        return None

    if define.endswith("/myblockdefine"):
        if allowed_custom_defines is not None and define not in allowed_custom_defines:
            return f"{path} references undefined myblock: {define}"
        return None

    return f"{path} uses unsupported block define: {define}"


def _collect_block_warnings(
    block: Dict[str, Any],
    path: str,
    allowed_custom_defines: set[str] | None = None,
) -> List[str]:
    warnings: List[str] = []
    walked: List[tuple[str, Dict[str, Any]]] = []
    walk_blocks(block, path, walked)

    for block_path, current_block in walked:
        warning = _describe_block_warning(
            current_block.get("define"),
            block_path,
            allowed_custom_defines,
        )
        if warning:
            warnings.append(warning)

    return warnings


def find_blocks_by_type(workspace_data: Dict[str, Any], block_define: str) -> List[Dict[str, Any]]:
    results = []

    for source, head_path, head in iter_workspace_heads(workspace_data):
        walked: List[tuple[str, Dict[str, Any]]] = []
        walk_blocks(head, head_path, walked)
        for path, block in walked:
            if block.get("define") == block_define:
                results.append(
                    {
                        "source": source,
                        "path": path,
                        "block": block,
                        "has_next": bool(block.get("next")),
                    }
                )

    return results


def get_block_documentation(block_define: str) -> str:
    block_info = get_block_type_info(block_define)

    if not block_info:
        return f"# {block_define}\n\nBlock definition not found.\n"

    doc = f"# {block_define}\n\n"
    doc += f"**Type**: {block_info.get('type').value if block_info.get('type') else 'Unknown'}\n\n"
    doc += f"**Category**: {block_info.get('category').value if block_info.get('category') else 'Unknown'}\n\n"
    doc += f"**Description**: {block_info.get('description', '')}\n\n"
    allowed_object_types = block_info.get("object_types")
    if allowed_object_types:
        doc += f"**Allowed Object Types**: {', '.join(allowed_object_types)}\n\n"

    return_type = block_info.get("return_type")
    doc += f"**Return Type**: {return_type if return_type else 'None'}\n\n"

    parameters = block_info.get("parameters", [])
    if parameters:
        doc += "## Parameters\n\n"
        for index, param in enumerate(parameters, start=1):
            doc += f"### {index}. {param.get('name', f'param{index - 1}')}\n\n"
            doc += f"- Type: {param.get('type', 'any')}\n"
            if param.get("default", "") != "":
                doc += f"- Default: `{param.get('default')}`\n"
            doc += f"- Embeddable: {bool(param.get('embeddable', True))}\n"
            if param.get("options"):
                doc += f"- Options: {', '.join(str(option) for option in param['options'])}\n"
            doc += "\n"
    else:
        doc += "## Parameters\n\nNone\n\n"

    if block_info.get("has_branch"):
        doc += f"## Branches\n\n{block_info.get('branch_count', 1)}\n\n"

    doc += "## Example\n\n```json\n"
    doc += "{\n"
    doc += f'  "define": "{block_define}"'
    if parameters:
        doc += ',\n  "sections": [\n    {\n      "params": [\n'
        for param in parameters:
            default_value = str(param.get("default", ""))
            doc += f'        {{"type": "var", "val": "{default_value}"}},\n'
        doc = doc.rstrip(",\n") + "\n"
        doc += "      ]\n    }\n  ]"
    doc += "\n}\n```\n"
    return doc


def analyze_workspace_statistics(workspace_data: Dict[str, Any]) -> Dict[str, Any]:
    stats = {
        "script_count": 0,
        "fragment_count": 0,
        "block_count": 0,
        "block_types": {},
        "myblock_count": 0,
        "trigger_count": 0,
        "max_chain_length": 0,
        "categories": {},
        "module_count": 0,
        "module_types": {},
        "module_kinds": {},
    }

    module_entries = collect_module_entries(workspace_data)
    stats["module_count"] = len(module_entries)
    for _, module in module_entries:
        module_type = module.get("type", "Unknown")
        stats["module_types"][module_type] = stats["module_types"].get(module_type, 0) + 1
        module_info = get_module_type_info(module_type)
        kind = module_info.get("kind", "unknown") if module_info else "unknown"
        stats["module_kinds"][kind] = stats["module_kinds"].get(kind, 0) + 1

    def count_blocks(block: Dict[str, Any], chain_length: int = 0) -> int:
        if not block:
            return chain_length

        stats["block_count"] += 1
        chain_length += 1

        define = block.get("define", "Unknown")
        stats["block_types"][define] = stats["block_types"].get(define, 0) + 1

        block_info = get_block_type_info(define)
        if block_info:
            category = block_info.get("category")
            if category:
                stats["categories"][category.value] = stats["categories"].get(category.value, 0) + 1

            block_type = block_info.get("type")
            if block_type and block_type.value == "Trigger":
                stats["trigger_count"] += 1

        for section in block.get("sections", []):
            for entry_type, _, entry in iter_param_entries(section):
                nested = get_embedded_block(entry_type, entry)
                if nested:
                    count_blocks(nested, 0)

            for _, _, child in iter_child_blocks(section):
                count_blocks(child, 0)

        next_block = block.get("next")
        if isinstance(next_block, dict):
            chain_length = count_blocks(next_block, chain_length)

        return chain_length

    script_entries = collect_script_entries(workspace_data)
    stats["script_count"] = len(script_entries)

    for _, script in script_entries:
        fragments = script.get("fragments", [])
        stats["fragment_count"] += len(fragments)
        stats["myblock_count"] += len(script.get("myblocks", []))

    for _, _, head in iter_workspace_heads(workspace_data):
        chain_length = count_blocks(head, 0)
        stats["max_chain_length"] = max(stats["max_chain_length"], chain_length)

    return stats


def _iter_module_roots(workspace_data: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
    roots: List[Tuple[str, Dict[str, Any]]] = []

    if is_module_node(workspace_data):
        roots.append(("root", workspace_data))
        return roots

    if is_workspace_project(workspace_data):
        for key in ("scene", "agents", "assets"):
            module = workspace_data.get(key)
            if is_module_node(module):
                roots.append((key, module))

    return roots


def _validate_fragment_like(
    path: str,
    fragment: Any,
    errors: List[str],
    warnings: List[str],
    declared_myblocks: set[str],
    owner_type: str | None = None,
    owner_block_types: List[str] | None = None,
    project_policy: Dict[str, Any] | None = None,
) -> None:
    if not isinstance(fragment, dict):
        errors.append(f"{path} must be a dictionary")
        return

    if "pos" not in fragment:
        errors.append(f"{path} missing 'pos' field")
    else:
        error = describe_property_value_error(f"{path}.pos", fragment["pos"], "vector2")
        if error:
            errors.append(error)

    if "head" not in fragment:
        errors.append(f"{path} missing 'head' field")
        return

    warnings.extend(
        _collect_block_warnings(
            fragment["head"],
            f"{path}.head",
            declared_myblocks,
        )
    )
    is_valid, error_msg = validate_block_structure(
        fragment["head"],
        allowed_custom_defines=declared_myblocks,
        allow_unsupported_defines=True,
    )
    if not is_valid:
        errors.append(f"{path}.head validation failed: {error_msg}")
        return

    errors.extend(
        collect_block_object_type_errors(
            fragment["head"],
            owner_block_types if owner_block_types else owner_type,
            f"{path}.head",
            owner_label=owner_type,
        )
    )
    if project_policy:
        errors.extend(
            collect_project_policy_errors(
                fragment["head"],
                project_policy,
                f"{path}.head",
            )
        )


def _validate_blockscript_ui_state(path: str, script: Any, errors: List[str]) -> None:
    if not isinstance(script, dict) or "uiState" not in script:
        return

    ui_state = script["uiState"]
    if not isinstance(ui_state, dict):
        errors.append(f"{path}.uiState must be a dictionary")
        return

    for key in ("pos", "scroll"):
        if key in ui_state:
            error = describe_property_value_error(f"{path}.uiState.{key}", ui_state[key], "vector2")
            if error:
                errors.append(error)

    if "scale" in ui_state:
        error = describe_property_value_error(f"{path}.uiState.scale", ui_state["scale"], "float")
        if error:
            errors.append(error)


def _validate_myblock_columns(path: str, myblock: Dict[str, Any], errors: List[str]) -> None:
    if "columns" not in myblock:
        return

    columns = myblock["columns"]
    if not isinstance(columns, list):
        errors.append(f"{path}.columns must be a list")
        return

    for index, column in enumerate(columns):
        column_path = f"{path}.columns[{index}]"
        if not isinstance(column, dict):
            errors.append(f"{column_path} must be a dictionary")
            continue

        column_type = column.get("type")
        if not isinstance(column_type, str) or not column_type:
            errors.append(f"{column_path}.type must be a non-empty string")
        elif column_type not in _MYBLOCK_COLUMN_TYPES:
            errors.append(
                f"{column_path}.type must be one of {', '.join(sorted(_MYBLOCK_COLUMN_TYPES))}"
            )

        if "data" not in column:
            errors.append(f"{column_path} missing required field: data")
            continue

        data = column["data"]
        data_path = f"{column_path}.data"
        if not isinstance(data, dict):
            errors.append(f"{data_path} must be a dictionary")
            continue

        entry_error = validate_block_value_entry(data, data_path, "val")
        if entry_error:
            errors.append(entry_error)


def _validate_block_whitelist(
    whitelist: Any,
    path: str,
    errors: List[str],
    warnings: List[str],
    declared_myblocks: set[str],
    project_policy: Dict[str, Any] | None = None,
) -> None:
    if not isinstance(whitelist, list):
        errors.append(f"{path} must be a list")
        return

    for index, block in enumerate(whitelist):
        block_path = f"{path}[{index}]"
        if not isinstance(block, dict):
            errors.append(f"{block_path} must be a dictionary")
            continue

        warnings.extend(_collect_block_warnings(block, block_path, declared_myblocks))
        is_valid, error_msg = validate_block_structure(
            block,
            allowed_custom_defines=declared_myblocks,
            allow_unsupported_defines=True,
        )
        if not is_valid:
            errors.append(f"{block_path} validation failed: {error_msg}")
            continue

        if project_policy:
            errors.extend(collect_project_policy_errors(block, project_policy, block_path))


def _validate_workspace_resources(workspace_data: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
    if "res" not in workspace_data or not isinstance(workspace_data.get("res"), list):
        return

    try:
        ensure_resource_data()
    except Exception as exc:
        errors.append(f"workspace.res resource validation unavailable: {exc}")
        return

    seen: set[int] = set()
    for index, resource_id in enumerate(workspace_data["res"]):
        if not isinstance(resource_id, int) or isinstance(resource_id, bool):
            continue
        if resource_id in seen:
            warnings.append(f"workspace.res[{index}] duplicates resource id: {resource_id}")
            continue
        seen.add(resource_id)
        if not is_valid_resource_id(resource_id):
            errors.append(f"workspace.res[{index}] references unknown resource id: {resource_id}")


def validate_workspace(workspace_data: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    declared_myblocks = _collect_declared_myblock_names(workspace_data)
    project_policy = get_project_policy(workspace_data)

    if not (
        is_workspace_project(workspace_data)
        or is_module_node(workspace_data)
        or bool(collect_script_entries(workspace_data))
    ):
        errors.append("Workspace must be a BlockScript, serialized module, or full .ws project tree")

    if is_workspace_project(workspace_data):
        project_errors, project_warnings = validate_project_root(workspace_data)
        errors.extend(project_errors)
        warnings.extend(project_warnings)
        _validate_workspace_resources(workspace_data, errors, warnings)

        if "whitelist" in workspace_data:
            _validate_block_whitelist(
                workspace_data.get("whitelist"),
                "workspace.whitelist",
                errors,
                warnings,
                declared_myblocks,
                project_policy,
            )

    for root_path, module in _iter_module_roots(workspace_data):
        module_errors, module_warnings = validate_module_data(module, root_path)
        errors.extend(module_errors)
        warnings.extend(module_warnings)

    script_contexts = collect_script_contexts(workspace_data)
    for context in script_contexts:
        source = context["source"]
        script = context["script"]
        script_path = context.get("script_path") or source
        owner_type = context.get("owner_type")
        owner_block_types = context.get("owner_block_types")
        fragments = script.get("fragments", [])
        if "fragments" not in script:
            warnings.append(f"{source}: no fragments found in script")
        elif not isinstance(fragments, list):
            errors.append(f"{script_path}.fragments must be a list")
            fragments = []

        _validate_blockscript_ui_state(script_path, script, errors)

        for index, fragment in enumerate(fragments):
            _validate_fragment_like(
                f"{source}.fragments[{index}]",
                fragment,
                errors,
                warnings,
                declared_myblocks,
                owner_type,
                owner_block_types,
                project_policy,
            )

        myblocks = script.get("myblocks", [])
        if "myblocks" in script and not isinstance(myblocks, list):
            errors.append(f"{script_path}.myblocks must be a list")
            myblocks = []

        for index, myblock in enumerate(myblocks):
            myblock_path = f"{source}.myblocks[{index}]"
            if not isinstance(myblock, dict):
                errors.append(f"{myblock_path} must be a dictionary")
                continue

            if "name" not in myblock:
                errors.append(f"{source}.myblocks[{index}] missing 'name' field")
            elif not isinstance(myblock["name"], str):
                errors.append(f"{source}.myblocks[{index}].name must be a string")
            if "displayName" not in myblock:
                warnings.append(f"{source}.myblocks[{index}] missing 'displayName' field")
            elif not isinstance(myblock["displayName"], str):
                errors.append(f"{source}.myblocks[{index}].displayName must be a string")
            elif project_policy.get("is_end_user_mode"):
                if project_policy.get("show_myblock") is False:
                    errors.append(
                        f"{source}.myblocks[{index}] is not allowed in end-user mode because showmyblock=false"
                    )
                elif isinstance(myblock.get("displayName"), str) and myblock.get("displayName", "").startswith("#"):
                    errors.append(
                        f"{source}.myblocks[{index}] is hidden in end-user mode because displayName starts with '#'"
                    )
            if "wrapBlockName" in myblock and not isinstance(myblock["wrapBlockName"], str):
                errors.append(f"{source}.myblocks[{index}].wrapBlockName must be a string")
            if "yield" in myblock and not isinstance(myblock["yield"], bool):
                errors.append(f"{source}.myblocks[{index}].yield must be a boolean")
            _validate_myblock_columns(myblock_path, myblock, errors)
            if "fragment" not in myblock:
                warnings.append(f"{source}.myblocks[{index}] missing 'fragment' field")
            else:
                myblock_name = myblock.get("name")
                head = myblock["fragment"].get("head") if isinstance(myblock["fragment"], dict) else None
                if isinstance(myblock_name, str) and myblock_name and isinstance(head, dict):
                    head_define = head.get("define")
                    if head_define != myblock_name:
                        errors.append(
                            f"{source}.myblocks[{index}].fragment.head.define must match myblock name "
                            f"{myblock_name}"
                        )
                _validate_fragment_like(
                    f"{source}.myblocks[{index}].fragment",
                    myblock["fragment"],
                    errors,
                    warnings,
                    declared_myblocks,
                    owner_type,
                    owner_block_types,
                    project_policy,
                )

    deduped_errors = list(dict.fromkeys(errors))
    deduped_warnings = list(dict.fromkeys(warnings))

    return {
        "valid": len(deduped_errors) == 0,
        "error_count": len(deduped_errors),
        "warning_count": len(deduped_warnings),
        "errors": deduped_errors,
        "warnings": deduped_warnings,
    }
