"""
Smoke test for the hetu-mcp server.

This script connects to the local stdio MCP server and exercises the full
public tool surface against reference/smoke/test-api-smoke.ws.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from definitions.block_models import BLOCK_DEFINITIONS
from definitions.workspace_schema import (
    MODULE_DEFINITIONS,
    SCENE_ELEMENT_BLOCK_TARGET_TYPES,
    SCENE_ELEMENT_SUPPORTED_BLOCK_COUNTS,
    get_scene_element_block_support_info,
    get_scene_element_block_target_types,
)


ROOT = Path(__file__).resolve().parents[3]
WORKSPACE_FILE = "reference/smoke/test-api-smoke.ws"
TEMP_FILE = "reference/smoke/test-api-smoke.generated.ws"
SERVER_PY = PACKAGE_ROOT / "server.py"


def registered_source_block_names() -> set[str]:
    block_root = ROOT / "script" / "Hetu" / "Block"
    defines_root = block_root / "Defines"
    modules_root = block_root / "Modules" / "Internal"
    block_names_text = (block_root / "BlockNames.cs").read_text(encoding="utf-8", errors="ignore")
    block_names = {
        const_name: literal
        for const_name, literal in re.findall(
            r'public const string\s+(\w+)\s*=\s*"([^"]+)"',
            block_names_text,
        )
    }

    def strip_comments(text: str) -> str:
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        return re.sub(r"//.*", "", text)

    define_classes: dict[str, str] = {}
    for path in defines_root.rglob("*.cs"):
        text = strip_comments(path.read_text(encoding="utf-8", errors="ignore"))
        for match in re.finditer(r"class\s+([A-Za-z0-9_]+)\s*:\s*BlockDefineImpl<", text):
            class_name = match.group(1)
            tail = text[match.start() :]
            name_match = re.search(
                r'public override string Name\s*=>\s*(?:BlockNames\.([A-Za-z0-9_]+)|"([^"]+)")',
                tail,
            )
            if not name_match:
                continue

            const_name = name_match.group(1)
            define_classes[class_name] = (
                block_names.get(const_name, const_name) if const_name else name_match.group(2)
            )

    registered_classes: set[str] = set()
    for path in modules_root.rglob("*.cs"):
        text = strip_comments(path.read_text(encoding="utf-8", errors="ignore"))
        registered_classes.update(re.findall(r"Register<\s*([A-Za-z0-9_]+)\s*>", text))

    return {define_classes[name] for name in registered_classes if name in define_classes}


def text_from_result(result) -> str:
    return "".join(
        item.text for item in result.content if getattr(item, "type", None) == "text"
    )


async def call_json(session: ClientSession, tool: str, args: dict) -> object:
    result = await session.call_tool(tool, args)
    return json.loads(text_from_result(result))


async def call_text(session: ClientSession, tool: str, args: dict) -> str:
    result = await session.call_tool(tool, args)
    return text_from_result(result)


async def expect_tool_error(session: ClientSession, tool: str, args: dict) -> str:
    try:
        result = await session.call_tool(tool, args)
        if getattr(result, "isError", False):
            return text_from_result(result)
    except Exception as exc:  # pragma: no cover - exercised in smoke runs
        return str(exc)

    raise AssertionError(f"Expected tool {tool} to fail")


def make_project_workspace(
    scene_children: list[dict],
    *,
    project_type: int = 3,
    show_myblock: bool = True,
    whitelist: list[dict] | None = None,
) -> dict:
    return {
        "name": "Policy Project",
        "desc": "",
        "icon": "",
        "author": "",
        "created": 0,
        "modified": 0,
        "type": project_type,
        "version": 3,
        "stageType": 0,
        "scene": {
            "type": "Scene",
            "id": "scene-root",
            "props": {"Name": "Scene", "EditMode": 0},
            "children": scene_children,
        },
        "agents": {
            "type": "Folder",
            "id": "agents-root",
            "props": {"Name": "agents", "EditMode": 0},
        },
        "assets": {
            "type": "Folder",
            "id": "assets-root",
            "props": {"Name": "assets", "EditMode": 0},
        },
        "res": [],
        "showmyblock": show_myblock,
        "whitelist": whitelist or [],
        "editorScene": {"cameras": []},
        "projectMode": 1,
    }


async def main() -> int:
    temp_output = ROOT / TEMP_FILE
    temp_output.unlink(missing_ok=True)
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PY), str(ROOT)],
    )

    try:
        async with stdio_client(server) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools = await session.list_tools()
                tool_names = [tool.name for tool in tools.tools]
                print(f"tool_count: {len(tool_names)}")
                assert {"get_resource", "find_resources", "validate_resource"}.issubset(tool_names)

                workspace_payload = await call_json(
                    session, "load_workspace_file", {"file_path": WORKSPACE_FILE}
                )
                workspace = workspace_payload["data"]
                print("load_workspace_file: ok")

                sample_resource_id = workspace["res"][0]
                resource = await call_json(
                    session,
                    "get_resource",
                    {"resource_id": sample_resource_id},
                )
                assert resource["resource_id"] == sample_resource_id
                print("get_resource: ok")

                resource_matches = await call_json(
                    session,
                    "find_resources",
                    {"resource_id": sample_resource_id, "limit": 1},
                )
                assert resource_matches["count"] == 1
                assert resource_matches["resources"][0]["resource_id"] == sample_resource_id
                print("find_resources: ok")

                resource_validation = await call_json(
                    session,
                    "validate_resource",
                    {"resource_id": sample_resource_id, "require_primary_url": True},
                )
                assert resource_validation["valid"] is True
                print("validate_resource: ok")
    
                modules = await call_json(session, "get_modules", {"workspace_data": workspace})
                assert modules, "Expected serialized modules from the sample workspace"
                assert any(item["type"] == "Scene" for item in modules)
                assert any(item["type"] == "ImageSet" for item in modules)
                scene_module_entry = next(item for item in modules if item["type"] == "Scene")
                assert scene_module_entry["scene_element_block_target_types"] == ["Scene"]
                assert scene_module_entry["scene_element_supported_block_count"] == 14
                print(f"get_modules: {len(modules)}")
    
                validated_scene = await call_json(
                    session,
                    "validate_module",
                    {"module": workspace["scene"]},
                )
                assert validated_scene["valid"] is True
                assert validated_scene["module_type"] == "Scene"
                assert validated_scene["scene_element_block_target_types"] == ["Scene"]
                assert validated_scene["scene_element_supported_block_count"] == 14
                print("validate_module: ok")

                invalid_effect_module = {
                    "type": "Effect",
                    "id": "effect-with-string-asset-id",
                    "props": {
                        "Name": "Broken FX",
                        "EditMode": 0,
                        "AssetId": "14760",
                        "Loop": False,
                    },
                }
                invalid_effect_validation = await call_json(
                    session,
                    "validate_module",
                    {"module": invalid_effect_module},
                )
                assert invalid_effect_validation["valid"] is False
                assert any(
                    "module.props.AssetId must be integer" in error
                    for error in invalid_effect_validation["errors"]
                )
                print("validate_module_runtime_property_type_rejected: ok")

                runtime_property_type_cases = [
                    (
                        "string",
                        {
                            "type": "Character",
                            "id": "bad-string",
                            "props": {"Name": 123, "EditMode": 0},
                        },
                        "module.props.Name must be string",
                    ),
                    (
                        "boolean",
                        {
                            "type": "Character",
                            "id": "bad-bool",
                            "props": {"Name": "Hero", "EditMode": 0, "Visible": "true"},
                        },
                        "module.props.Visible must be boolean",
                    ),
                    (
                        "float",
                        {
                            "type": "Character",
                            "id": "bad-float",
                            "props": {"Name": "Hero", "EditMode": 0, "Scale": 1},
                        },
                        "module.props.Scale must be numeric string",
                    ),
                    (
                        "vector3",
                        {
                            "type": "Character",
                            "id": "bad-vector3",
                            "props": {"Name": "Hero", "EditMode": 0, "Position": [0, 0, 0]},
                        },
                        "module.props.Position must be 3-item numeric string array",
                    ),
                    (
                        "color",
                        {
                            "type": "Character",
                            "id": "bad-color",
                            "props": {"Name": "Hero", "EditMode": 0, "Color": 123},
                        },
                        "module.props.Color must be color",
                    ),
                    (
                        "object_ref",
                        {
                            "type": "Camera",
                            "id": "bad-object-ref",
                            "props": {"Name": "Camera", "EditMode": 0, "Follow": 123},
                        },
                        "module.props.Follow must be object_ref",
                    ),
                    (
                        "simple_list",
                        {
                            "type": "BlockService",
                            "id": "bad-simple-list",
                            "props": {"Name": "Blocks", "EditMode": 0, "Modules": "motion"},
                        },
                        "module.props.Modules must be simple_list",
                    ),
                ]
                for case_name, module, expected_error in runtime_property_type_cases:
                    case_validation = await call_json(
                        session,
                        "validate_module",
                        {"module": module},
                    )
                    assert case_validation["valid"] is False, case_name
                    assert any(expected_error in error for error in case_validation["errors"]), (
                        case_name,
                        case_validation["errors"],
                    )
                print("validate_module_runtime_property_type_matrix: ok")
    
                image_set_modules = await call_json(
                    session,
                    "find_modules_by_type",
                    {"workspace_data": workspace, "module_type": "ImageSet"},
                )
                assert len(image_set_modules) >= 1
                assert image_set_modules[0]["module"]["type"] == "ImageSet"
                print("find_modules_by_type: ok")
    
                scene_module_doc = await call_text(
                    session,
                    "get_module_documentation",
                    {"module_type": "Scene"},
                )
                assert scene_module_doc.startswith("# Scene")
                assert "## Scene Element Block Support" in scene_module_doc
                assert "Block target types: `Scene`" in scene_module_doc
                compat_module_doc = await call_text(
                    session,
                    "get_module_documentation",
                    {"module_type": "UIView"},
                )
                assert compat_module_doc.startswith("# UIView")
                print("get_module_documentation: ok")
    
                fragments = await call_json(session, "get_fragments", {"workspace_data": workspace})
                assert fragments, "Expected fragments from the sample workspace"
                print(f"get_fragments: {len(fragments)}")
    
                first_fragment = fragments[0]
                script_id = first_fragment["source"]
    
                updated_workspace = await call_json(
                    session,
                    "update_fragment_position",
                    {
                        "workspace_data": workspace,
                        "script_id": script_id,
                        "fragment_index": first_fragment["index"],
                        "position": ["999", "888"],
                    },
                )
                updated_fragments = await call_json(
                    session, "get_fragments", {"workspace_data": updated_workspace}
                )
                changed = [
                    item
                    for item in updated_fragments
                    if item["source"] == script_id and item["index"] == first_fragment["index"]
                ][0]
                assert changed["position"] == ["999", "888"]
                print("update_fragment_position: ok")
    
                sample_fragment = {
                    "pos": ["321", "654"],
                    "head": {"define": "WhenGameStarts", "sections": [{"children": []}]},
                }
                added_workspace = await call_json(
                    session,
                    "add_fragment",
                    {
                        "workspace_data": workspace,
                        "script_id": script_id,
                        "fragment": sample_fragment,
                    },
                )
                added_fragments = await call_json(
                    session, "get_fragments", {"workspace_data": added_workspace}
                )
                assert len(added_fragments) == len(fragments) + 1
                print("add_fragment: ok")
    
                added_in_script = [f for f in added_fragments if f["source"] == script_id]
                removed_workspace = await call_json(
                    session,
                    "remove_fragment",
                    {
                        "workspace_data": added_workspace,
                        "script_id": script_id,
                        "fragment_index": max(item["index"] for item in added_in_script),
                    },
                )
                removed_fragments = await call_json(
                    session, "get_fragments", {"workspace_data": removed_workspace}
                )
                assert len(removed_fragments) == len(fragments)
                print("remove_fragment: ok")
    
                move_block = await call_json(
                    session,
                    "create_block",
                    {"block_define": "MoveSteps", "parameters": {"steps": "42"}},
                )
                assert move_block["define"] == "MoveSteps"
                print("create_block: ok")
    
                play_animation_block = await call_json(
                    session,
                    "create_block",
                    {"block_define": "PlayAnimation", "parameters": {"animation": "wave"}},
                )
                assert play_animation_block["define"] == "PlayAnimation"
                assert play_animation_block["sections"][0]["params"][0]["val"] == "wave"
                print("create_block_script_defined: ok")
    
                transit_project_block = await call_json(
                    session,
                    "create_block",
                    {
                        "block_define": "TransitProject",
                        "parameters": {
                            "project": "ProjectA",
                            "out_transition": "fade",
                            "in_transition": "fade",
                        },
                    },
                )
                assert [entry["val"] for entry in transit_project_block["sections"][0]["params"]] == [
                    "ProjectA",
                    "fade",
                    "fade",
                ]
                print("create_block_stage_parameters: ok")
    
                block_info = await call_json(session, "get_block_info", {"block": move_block})
                assert block_info["parameter_count"] == 1
                print("get_block_info: ok")
    
                modified_block = await call_json(
                    session,
                    "modify_block_parameter",
                    {"block": move_block, "parameter_index": 0, "value": "99"},
                )
                assert modified_block["sections"][0]["params"][0]["val"] == "99"
                print("modify_block_parameter: ok")
    
                trigger_block = await call_json(
                    session, "create_block", {"block_define": "WhenGameStarts"}
                )
                appended = await call_json(
                    session,
                    "append_block",
                    {"block": trigger_block, "new_block": move_block},
                )
                appended_define = (
                    appended.get("next", {}).get("define")
                    or appended.get("sections", [{}])[0].get("children", [{}])[0].get("define")
                )
                assert appended_define == "MoveSteps"
                print("append_block: ok")
    
                keyed_trigger = await call_json(
                    session,
                    "create_block",
                    {"block_define": "WhenKeyPressed", "parameters": {"key": "space"}},
                )
                keyed_trigger_appended = await call_json(
                    session,
                    "append_block",
                    {"block": keyed_trigger, "new_block": move_block},
                )
                assert "next" not in keyed_trigger_appended
                assert keyed_trigger_appended["sections"][0]["children"][0]["define"] == "MoveSteps"
                print("append_block_trigger_children: ok")
    
                forever = await call_json(session, "create_block", {"block_define": "Forever"})
                inserted = await call_json(
                    session,
                    "insert_block_child",
                    {"block": forever, "section_index": 0, "child_block": move_block},
                )
                assert inserted["sections"][0]["children"][0]["define"] == "MoveSteps"
                print("insert_block_child: ok")
    
                repeat = await call_json(
                    session,
                    "create_block",
                    {"block_define": "Repeat", "parameters": {"times": "3"}},
                )
                assert len(repeat["sections"]) == 1
                assert repeat["sections"][0]["params"][0]["val"] == "3"
                assert repeat["sections"][0]["children"] == []
                repeated = await call_json(
                    session,
                    "insert_block_child",
                    {"block": repeat, "section_index": 0, "child_block": move_block},
                )
                assert repeated["sections"][0]["children"][0]["define"] == "MoveSteps"
                print("repeat_branch_structure: ok")
    
                myblocks = await call_json(session, "get_myblocks", {"workspace_data": workspace})
                print(f"get_myblocks: {len(myblocks)}")
    
                target_script_id = myblocks[0]["source"] if myblocks else script_id
                created_myblock_workspace = await call_json(
                    session,
                    "create_myblock",
                    {
                        "workspace_data": workspace,
                        "script_id": target_script_id,
                        "name": "api_smoke",
                        "display_name": "API Smoke",
                        "parameters": [{"name": "distance", "type": "value"}],
                        "yield": True,
                    },
                )
                created_myblocks = await call_json(
                    session, "get_myblocks", {"workspace_data": created_myblock_workspace}
                )
                created_entry = [
                    item for item in created_myblocks if item["name"].endswith("/api_smoke/myblockdefine")
                ][0]
                assert created_entry["parameters"] == [{"name": "distance", "type": "value"}]
                print("create_myblock: ok")
    
                updated_myblock_workspace = await call_json(
                    session,
                    "update_myblock_fragment",
                    {
                        "workspace_data": created_myblock_workspace,
                        "script_id": target_script_id,
                        "myblock_name": created_entry["name"],
                        "fragment": {
                            "pos": ["11", "22"],
                            "head": {
                                "define": created_entry["name"],
                                "sections": [{"children": [move_block]}],
                            },
                        },
                    },
                )
                updated_myblocks = await call_json(
                    session, "get_myblocks", {"workspace_data": updated_myblock_workspace}
                )
                assert any(item["name"] == created_entry["name"] for item in updated_myblocks)
                print("update_myblock_fragment: ok")
    
                myblock_only_workspace = {
                    "type": "BlockScript",
                    "id": "root",
                    "fragments": [],
                    "myblocks": [
                        {
                            "name": "root/test/myblockdefine",
                            "displayName": "Test",
                            "fragment": {
                                "pos": ["0", "0"],
                                "head": {
                                    "define": "root/test/myblockdefine",
                                    "sections": [{"children": [move_block]}],
                                },
                            },
                        }
                    ],
                }
                found_in_myblock_fragment = await call_json(
                    session,
                    "find_blocks_by_type",
                    {"workspace_data": myblock_only_workspace, "block_define": "MoveSteps"},
                )
                assert len(found_in_myblock_fragment) == 1
                assert ".myblocks[0].fragment.head" in found_in_myblock_fragment[0]["path"]
                myblock_only_stats = await call_json(
                    session,
                    "analyze_workspace_statistics",
                    {"workspace_data": myblock_only_workspace},
                )
                assert myblock_only_stats["block_count"] == 2
                print("myblock_fragment_queries: ok")
    
                call_block = await call_json(
                    session,
                    "create_myblock_call",
                    {"myblock_name": created_entry["name"], "parameter_values": ["7"]},
                )
                assert call_block["define"] == created_entry["name"]
                print("create_myblock_call: ok")
    
                custom_call_validation = await call_json(
                    session,
                    "validate_block",
                    {"block": call_block},
                )
                assert custom_call_validation["valid"] is True
                assert custom_call_validation["warning_count"] == 0
                print("validate_block_custom_myblock: ok")
    
                usages = await call_json(
                    session,
                    "find_myblock_usages",
                    {"workspace_data": workspace, "myblock_name": created_entry["name"]},
                )
                assert isinstance(usages, list)
                print("find_myblock_usages: ok")
    
                myblock_usage_workspace = {
                    "type": "BlockScript",
                    "id": "root",
                    "fragments": [],
                    "myblocks": [
                        {
                            "name": "root/a/myblockdefine",
                            "displayName": "A",
                            "fragment": {
                                "pos": ["0", "0"],
                                "head": {
                                    "define": "root/a/myblockdefine",
                                    "sections": [{"children": [{"define": "root/b/myblockdefine", "sections": [{}]}]}],
                                },
                            },
                        },
                        {
                            "name": "root/b/myblockdefine",
                            "displayName": "B",
                            "fragment": {
                                "pos": ["0", "0"],
                                "head": {
                                    "define": "root/b/myblockdefine",
                                    "sections": [{"children": []}],
                                },
                            },
                        },
                    ],
                }
                myblock_usages = await call_json(
                    session,
                    "find_myblock_usages",
                    {"workspace_data": myblock_usage_workspace, "myblock_name": "root/b/myblockdefine"},
                )
                assert len(myblock_usages) == 1
                assert ".myblocks[0].fragment.head" in myblock_usages[0]["location"]
                print("find_myblock_usages_myblock_fragment: ok")
    
                removed_myblock_workspace = await call_json(
                    session,
                    "remove_myblock",
                    {
                        "workspace_data": created_myblock_workspace,
                        "script_id": target_script_id,
                        "myblock_name": created_entry["name"],
                    },
                )
                removed_myblocks = await call_json(
                    session, "get_myblocks", {"workspace_data": removed_myblock_workspace}
                )
                assert not any(item["name"] == created_entry["name"] for item in removed_myblocks)
                print("remove_myblock: ok")
    
                validated = await call_json(session, "validate_block", {"block": move_block})
                assert validated["valid"] is True
                print("validate_block: ok")
    
                invalid_trigger = {
                    "define": "WhenKeyPressed",
                    "sections": [{"params": [{"type": "var", "val": "space"}]}],
                    "next": move_block,
                }
                invalid_trigger_validation = await call_json(
                    session, "validate_block", {"block": invalid_trigger}
                )
                assert invalid_trigger_validation["valid"] is False
                print("validate_block_trigger_next: ok")
    
                invalid_repeat = {
                    "define": "Repeat",
                    "sections": [
                        {"params": [{"type": "var", "val": "3"}]},
                        {"children": [move_block]},
                    ],
                }
                invalid_repeat_validation = await call_json(
                    session, "validate_block", {"block": invalid_repeat}
                )
                assert invalid_repeat_validation["valid"] is False
                print("validate_block_branch_sections: ok")
    
                invalid_sprite_click_trigger = {
                    "define": "WhenThisSpriteClicked",
                    "sections": [{"params": [{"type": "var", "val": "this sprite"}]}],
                    "next": move_block,
                }
                invalid_sprite_click_validation = await call_json(
                    session,
                    "validate_block",
                    {"block": invalid_sprite_click_trigger},
                )
                assert invalid_sprite_click_validation["valid"] is False
                print("validate_block_script_defined_trigger: ok")
    
                unsupported_block_validation = await call_json(
                    session,
                    "validate_block",
                    {
                        "block": {
                            "define": "SetProgressBarValue",
                            "sections": [{"params": [{"type": "var", "val": "10"}]}],
                        }
                    },
                )
                assert unsupported_block_validation["valid"] is True
                assert unsupported_block_validation["error"] is None
                assert unsupported_block_validation["warning_count"] == 1
                assert "unsupported block define" in unsupported_block_validation["warnings"][0]
                print("validate_block_unsupported_define: ok")

                block_payload_type_cases = [
                    (
                        "var-val-string",
                        {
                            "define": "WaitSeconds",
                            "sections": [{"params": [{"type": "var", "val": 1}]}],
                        },
                        "block.sections[0].params[0].val must be a string for var entries",
                    ),
                    (
                        "block-val-dict",
                        {
                            "define": "WaitUntil",
                            "sections": [{"params": [{"type": "block", "val": "not-a-block"}]}],
                        },
                        "block.sections[0].params[0].val must be a dictionary for block entries",
                    ),
                    (
                        "column-block-value-dict",
                        {
                            "define": "SetVariable",
                            "sections": [{"columns": [{"type": "block", "value": "not-a-block"}]}],
                        },
                        "block.sections[0].columns[0].value must be a dictionary for block entries",
                    ),
                    (
                        "entry-type-string",
                        {
                            "define": "WaitSeconds",
                            "sections": [{"params": [{"type": 1, "val": "1"}]}],
                        },
                        "block.sections[0].params[0].type must be a string",
                    ),
                    (
                        "entry-name-string",
                        {
                            "define": "WaitSeconds",
                            "sections": [{"params": [{"name": 1, "type": "var", "val": "1"}]}],
                        },
                        "block.sections[0].params[0].name must be a string",
                    ),
                    (
                        "entry-custom-popup-integer",
                        {
                            "define": "WaitSeconds",
                            "sections": [{"params": [{"customPopup": "0", "type": "var", "val": "1"}]}],
                        },
                        "block.sections[0].params[0].customPopup must be an integer",
                    ),
                ]
                for case_name, block, expected_error in block_payload_type_cases:
                    block_payload_validation = await call_json(
                        session,
                        "validate_block",
                        {"block": block},
                    )
                    assert block_payload_validation["valid"] is False, case_name
                    assert expected_error in (block_payload_validation["error"] or ""), (
                        case_name,
                        block_payload_validation,
                    )
                print("validate_block_payload_runtime_shape_rejected: ok")
    
                found = await call_json(
                    session,
                    "find_blocks_by_type",
                    {"workspace_data": workspace, "block_define": "WhenGameStarts"},
                )
                assert len(found) >= 1
                print("find_blocks_by_type: ok")
    
                documentation = await call_text(
                    session, "get_block_documentation", {"block_define": "MoveSteps"}
                )
                assert documentation.startswith("# MoveSteps")
                print("get_block_documentation: ok")
    
                script_defined_documentation = await call_text(
                    session,
                    "get_block_documentation",
                    {"block_define": "PlayDialogueGroup"},
                )
                assert "Block definition not found" not in script_defined_documentation
                print("get_block_documentation_script_defined: ok")

                think_documentation = await call_text(
                    session,
                    "get_block_documentation",
                    {"block_define": "ThinkForSeconds"},
                )
                assert "### 1. message" in think_documentation
                assert "### 2. seconds" in think_documentation
                print("get_block_documentation_parameter_names: ok")

                damping_documentation = await call_text(
                    session,
                    "get_block_documentation",
                    {"block_define": "SetCameraDamping"},
                )
                assert "**Allowed Object Types**: CameraService" in damping_documentation
                assert "### 1. mode" in damping_documentation
                assert "### 2. x" in damping_documentation
                assert "### 3. y" in damping_documentation
                assert "### 4. z" in damping_documentation
                print("get_block_documentation_literal_name_block: ok")

                generic_param_names = {
                    name: [param["name"] for param in definition.get("parameters", [])]
                    for name, definition in BLOCK_DEFINITIONS.items()
                    if any(
                        param.get("name", "").startswith("param")
                        for param in definition.get("parameters", [])
                    )
                }
                assert not generic_param_names, (
                    f"Generic parameter names remain in extracted definitions: {generic_param_names}"
                )

                unnamed_module_properties = {
                    name: definition.get("properties", [])
                    for name, definition in MODULE_DEFINITIONS.items()
                    if any(not prop.get("name") for prop in definition.get("properties", []))
                }
                assert not unnamed_module_properties, (
                    "Unnamed module properties remain in extracted workspace definitions"
                )
                missing_registered_blocks = sorted(
                    name for name in registered_source_block_names() if name not in BLOCK_DEFINITIONS
                )
                assert not missing_registered_blocks, (
                    f"Registered source blocks missing from extracted definitions: {missing_registered_blocks}"
                )
                assert BLOCK_DEFINITIONS["MoveSteps"].get("object_types") == [
                    "Part",
                    "ImageSet",
                    "CameraService",
                    "PartSet",
                    "Quad",
                ]
                assert BLOCK_DEFINITIONS["TurnToTargetInSecs"].get("object_types") == ["Character"]
                assert BLOCK_DEFINITIONS["SetCameraDamping"].get("object_types") == ["CameraService"]
                assert SCENE_ELEMENT_BLOCK_TARGET_TYPES == {
                    "Scene": ["Scene"],
                    "CameraService": ["CameraService"],
                    "ImageSet": ["ImageSet"],
                    "MeshPart": ["Part"],
                    "Avatar": ["Avatar"],
                    "Character": ["Character"],
                    "PartSet": ["PartSet"],
                    "QuestObject": ["QuestObject"],
                    "Quad": ["Quad"],
                }
                assert SCENE_ELEMENT_SUPPORTED_BLOCK_COUNTS == {
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
                assert SCENE_ELEMENT_BLOCK_TARGET_TYPES["MeshPart"] == ["Part"]
                assert get_scene_element_block_target_types("Character") == ["Character"]
                assert get_scene_element_block_target_types("UnknownOwner") == ["UnknownOwner"]
                meshpart_support = get_scene_element_block_support_info("MeshPart")
                quest_support = get_scene_element_block_support_info("QuestObject")
                assert meshpart_support is not None
                assert meshpart_support["supported_block_count"] == 73
                assert meshpart_support["target_types"] == ["Part"]
                assert quest_support is not None
                assert quest_support["supported_block_count"] == 5
                assert quest_support["target_types"] == ["QuestObject"]
                print("definition_integrity: ok")

                stats = await call_json(
                    session, "analyze_workspace_statistics", {"workspace_data": workspace}
                )
                assert stats["script_count"] >= 1
                assert stats["fragment_count"] >= 1
                assert stats["module_count"] >= 1
                assert stats["module_types"]["Scene"] >= 1
                print("analyze_workspace_statistics: ok")
    
                workspace_validation = await call_json(
                    session, "validate_workspace", {"workspace_data": workspace}
                )
                assert workspace_validation["valid"] is True
                assert workspace_validation["error_count"] == 0
                assert isinstance(workspace_validation["warnings"], list)
                print("validate_workspace: ok")
    
                valid_custom_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": myblock_only_workspace},
                )
                assert valid_custom_workspace_validation["valid"] is True
                print("validate_workspace_custom_myblock: ok")

                invalid_effect_workspace = make_project_workspace([invalid_effect_module])
                invalid_effect_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": invalid_effect_workspace},
                )
                assert invalid_effect_workspace_validation["valid"] is False
                assert any(
                    "scene.children[0].props.AssetId must be integer" in error
                    for error in invalid_effect_workspace_validation["errors"]
                )
                print("validate_workspace_runtime_property_type_rejected: ok")

                invalid_blockscript_shape_workspace = {
                    "type": "BlockScript",
                    "id": "bad-script-shape",
                    "props": {"Name": "BlockScript", "EditMode": 0},
                    "fragments": [
                        {
                            "pos": [0, 0],
                            "head": {"define": "WhenGameStarts", "sections": [{"params": []}]},
                        }
                    ],
                    "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": 1},
                }
                invalid_blockscript_shape_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": invalid_blockscript_shape_workspace},
                )
                assert invalid_blockscript_shape_validation["valid"] is False
                assert any(
                    "bad-script-shape.fragments[0].pos must be 2-item numeric string array" in error
                    for error in invalid_blockscript_shape_validation["errors"]
                )
                assert any(
                    "root.uiState.scale must be numeric string" in error
                    for error in invalid_blockscript_shape_validation["errors"]
                )
                print("validate_workspace_blockscript_runtime_shape_rejected: ok")

                invalid_myblock_shape_workspace = {
                    "type": "BlockScript",
                    "id": "bad-myblock-shape",
                    "props": {"Name": "BlockScript", "EditMode": 0},
                    "fragments": [],
                    "myblocks": [
                        {
                            "name": 1,
                            "displayName": 2,
                            "wrapBlockName": 3,
                            "yield": "false",
                            "columns": [
                                {"type": 1, "data": {}},
                                {"type": "NotAColumn", "data": {}},
                                {"type": "Variable", "data": {"name": 1}},
                                {"type": "Variable", "data": {"customPopup": "0"}},
                                {"type": "Logical", "data": "not-a-dict"},
                            ],
                        }
                    ],
                }
                invalid_myblock_shape_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": invalid_myblock_shape_workspace},
                )
                assert invalid_myblock_shape_validation["valid"] is False
                for expected_error in (
                    "bad-myblock-shape.myblocks[0].name must be a string",
                    "bad-myblock-shape.myblocks[0].displayName must be a string",
                    "bad-myblock-shape.myblocks[0].wrapBlockName must be a string",
                    "bad-myblock-shape.myblocks[0].yield must be a boolean",
                    "bad-myblock-shape.myblocks[0].columns[0].type must be a non-empty string",
                    "bad-myblock-shape.myblocks[0].columns[1].type must be one of",
                    "bad-myblock-shape.myblocks[0].columns[2].data.name must be a string",
                    "bad-myblock-shape.myblocks[0].columns[3].data.customPopup must be an integer",
                    "bad-myblock-shape.myblocks[0].columns[4].data must be a dictionary",
                ):
                    assert any(
                        expected_error in error
                        for error in invalid_myblock_shape_validation["errors"]
                    ), (expected_error, invalid_myblock_shape_validation["errors"])
                print("validate_workspace_myblock_runtime_shape_rejected: ok")

                valid_character_workspace = {
                    "type": "Character",
                    "id": "character-root",
                    "props": {"Name": "Hero", "EditMode": 0},
                    "children": [
                        {
                            "type": "BlockScript",
                            "id": "character-script",
                            "props": {"Name": "BlockScript", "EditMode": 0},
                            "fragments": [
                                {
                                    "pos": ["0", "0"],
                                    "head": {
                                        "define": "TurnToTargetInSecs",
                                        "sections": [
                                            {
                                                "params": [
                                                    {"type": "var", "val": "TargetA"},
                                                    {"type": "var", "val": "0.3"},
                                                ]
                                            }
                                        ],
                                    },
                                }
                            ],
                            "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                        }
                    ],
                }
                valid_character_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": valid_character_workspace},
                )
                assert valid_character_workspace_validation["valid"] is True
                print("validate_workspace_object_type_allowed: ok")

                invalid_character_workspace = {
                    "type": "Character",
                    "id": "character-root",
                    "props": {"Name": "Hero", "EditMode": 0},
                    "children": [
                        {
                            "type": "BlockScript",
                            "id": "character-script",
                            "props": {"Name": "BlockScript", "EditMode": 0},
                            "fragments": [
                                {
                                    "pos": ["0", "0"],
                                    "head": {
                                        "define": "MoveSteps",
                                        "sections": [{"params": [{"type": "var", "val": "10"}]}],
                                    },
                                }
                            ],
                            "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                        }
                    ],
                }
                invalid_character_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": invalid_character_workspace},
                )
                assert invalid_character_workspace_validation["valid"] is False
                assert any(
                    "not allowed for owner type Character" in error
                    for error in invalid_character_workspace_validation["errors"]
                )
                print("validate_workspace_object_type_rejected: ok")

                invalid_fragment_error = await expect_tool_error(
                    session,
                    "add_fragment",
                    {
                        "workspace_data": {
                            "type": "Character",
                            "id": "character-root",
                            "props": {"Name": "Hero", "EditMode": 0},
                            "children": [
                                {
                                    "type": "BlockScript",
                                    "id": "character-script",
                                    "props": {"Name": "BlockScript", "EditMode": 0},
                                    "fragments": [],
                                    "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                                }
                            ],
                        },
                        "script_id": "character-script",
                        "fragment": {
                            "pos": ["0", "0"],
                            "head": {
                                "define": "MoveSteps",
                                "sections": [{"params": [{"type": "var", "val": "10"}]}],
                            },
                        },
                    },
                )
                assert "not allowed for owner type Character" in invalid_fragment_error
                print("add_fragment_object_type_rejected: ok")

                valid_meshpart_workspace = {
                    "type": "MeshPart",
                    "id": "meshpart-root",
                    "props": {"Name": "Light", "EditMode": 0},
                    "children": [
                        {
                            "type": "BlockScript",
                            "id": "meshpart-script",
                            "props": {"Name": "BlockScript", "EditMode": 0},
                            "fragments": [
                                {
                                    "pos": ["0", "0"],
                                    "head": {
                                        "define": "WhenGameStarts",
                                        "sections": [
                                            {
                                                "children": [
                                                    {
                                                        "define": "Hide",
                                                        "sections": [{"params": [{}]}],
                                                    }
                                                ]
                                            }
                                        ],
                                    },
                                }
                            ],
                            "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                        }
                    ],
                }
                valid_meshpart_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": valid_meshpart_workspace},
                )
                assert valid_meshpart_workspace_validation["valid"] is True
                print("validate_workspace_meshpart_alias: ok")

                valid_partset_workspace = {
                    "type": "PartSet",
                    "id": "partset-root",
                    "props": {"Name": "AnimSet", "EditMode": 0},
                    "children": [
                        {
                            "type": "BlockScript",
                            "id": "partset-script",
                            "props": {"Name": "BlockScript", "EditMode": 0},
                            "fragments": [
                                {
                                    "pos": ["0", "0"],
                                    "head": {
                                        "define": "WhenGameStarts",
                                        "sections": [
                                            {
                                                "children": [
                                                    {
                                                        "define": "NextCostume",
                                                        "sections": [{}],
                                                    }
                                                ]
                                            }
                                        ],
                                    },
                                }
                            ],
                            "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                        }
                    ],
                }
                valid_partset_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": valid_partset_workspace},
                )
                assert valid_partset_workspace_validation["valid"] is True
                print("validate_workspace_partset_alias: ok")

                quest_text_block = await call_json(
                    session,
                    "create_block",
                    {"block_define": "SetQuestText", "parameters": {"text": "Find the key"}},
                )
                valid_quest_object_workspace = {
                    "type": "QuestObject",
                    "id": "quest-root",
                    "props": {"Name": "Quest", "EditMode": 0},
                    "children": [
                        {
                            "type": "BlockScript",
                            "id": "quest-script",
                            "props": {"Name": "BlockScript", "EditMode": 0},
                            "fragments": [
                                {
                                    "pos": ["0", "0"],
                                    "head": {
                                        "define": "WhenGameStarts",
                                        "sections": [{"children": [quest_text_block]}],
                                    },
                                }
                            ],
                            "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                        }
                    ],
                }
                valid_quest_object_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": valid_quest_object_workspace},
                )
                assert valid_quest_object_workspace_validation["valid"] is True
                print("validate_workspace_quest_object_allowed: ok")

                invalid_quest_object_workspace = {
                    "type": "QuestObject",
                    "id": "quest-root",
                    "props": {"Name": "Quest", "EditMode": 0},
                    "children": [
                        {
                            "type": "BlockScript",
                            "id": "quest-script",
                            "props": {"Name": "BlockScript", "EditMode": 0},
                            "fragments": [
                                {
                                    "pos": ["0", "0"],
                                    "head": {
                                        "define": "MoveSteps",
                                        "sections": [{"params": [{"type": "var", "val": "10"}]}],
                                    },
                                }
                            ],
                            "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                        }
                    ],
                }
                invalid_quest_object_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": invalid_quest_object_workspace},
                )
                assert invalid_quest_object_workspace_validation["valid"] is False
                assert any(
                    "not allowed for owner type QuestObject" in error
                    for error in invalid_quest_object_workspace_validation["errors"]
                )
                print("validate_workspace_quest_object_rejected: ok")

                valid_avatar_workspace = {
                    "type": "Avatar",
                    "id": "avatar-root",
                    "props": {"Name": "Guide", "EditMode": 0},
                    "children": [
                        {
                            "type": "BlockScript",
                            "id": "avatar-script",
                            "props": {"Name": "BlockScript", "EditMode": 0},
                            "fragments": [
                                {
                                    "pos": ["0", "0"],
                                    "head": {
                                        "define": "PlayAnimationAndWait",
                                        "sections": [{"params": [{"type": "var", "val": "wave"}]}],
                                    },
                                }
                            ],
                            "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                        }
                    ],
                }
                valid_avatar_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": valid_avatar_workspace},
                )
                assert valid_avatar_workspace_validation["valid"] is True
                print("validate_workspace_avatar_exact_allowed: ok")

                invalid_avatar_workspace = {
                    "type": "Avatar",
                    "id": "avatar-root",
                    "props": {"Name": "Guide", "EditMode": 0},
                    "children": [
                        {
                            "type": "BlockScript",
                            "id": "avatar-script",
                            "props": {"Name": "BlockScript", "EditMode": 0},
                            "fragments": [
                                {
                                    "pos": ["0", "0"],
                                    "head": {
                                        "define": "MoveSteps",
                                        "sections": [{"params": [{"type": "var", "val": "10"}]}],
                                    },
                                }
                            ],
                            "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                        }
                    ],
                }
                invalid_avatar_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": invalid_avatar_workspace},
                )
                assert invalid_avatar_workspace_validation["valid"] is False
                assert any(
                    "not allowed for owner type Avatar" in error
                    for error in invalid_avatar_workspace_validation["errors"]
                )
                print("validate_workspace_avatar_exact_rejected: ok")

                invalid_partset_workspace = {
                    "type": "PartSet",
                    "id": "partset-root",
                    "props": {"Name": "AnimSet", "EditMode": 0},
                    "children": [
                        {
                            "type": "BlockScript",
                            "id": "partset-script",
                            "props": {"Name": "BlockScript", "EditMode": 0},
                            "fragments": [
                                {
                                    "pos": ["0", "0"],
                                    "head": {
                                        "define": "PlayEmotionAnimation",
                                        "sections": [
                                            {
                                                "params": [
                                                    {"type": "var", "val": "blink"},
                                                    {"type": "var", "val": "true"},
                                                ]
                                            }
                                        ],
                                    },
                                }
                            ],
                            "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                        }
                    ],
                }
                invalid_partset_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": invalid_partset_workspace},
                )
                assert invalid_partset_workspace_validation["valid"] is False
                assert any(
                    "not allowed for owner type PartSet" in error
                    for error in invalid_partset_workspace_validation["errors"]
                )
                print("validate_workspace_partset_exact_rejected: ok")

                invalid_avatar_fragment_error = await expect_tool_error(
                    session,
                    "add_fragment",
                    {
                        "workspace_data": {
                            "type": "Avatar",
                            "id": "avatar-root",
                            "props": {"Name": "Guide", "EditMode": 0},
                            "children": [
                                {
                                    "type": "BlockScript",
                                    "id": "avatar-script",
                                    "props": {"Name": "BlockScript", "EditMode": 0},
                                    "fragments": [],
                                    "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                                }
                            ],
                        },
                        "script_id": "avatar-script",
                        "fragment": {
                            "pos": ["0", "0"],
                            "head": {
                                "define": "MoveSteps",
                                "sections": [{"params": [{"type": "var", "val": "10"}]}],
                            },
                        },
                    },
                )
                assert "not allowed for owner type Avatar" in invalid_avatar_fragment_error
                print("add_fragment_avatar_exact_rejected: ok")

                end_user_whitelist_allowed = make_project_workspace(
                    [
                        {
                            "type": "ImageSet",
                            "id": "image-root",
                            "props": {"Name": "Sprite", "EditMode": 0},
                            "children": [
                                {
                                    "type": "BlockScript",
                                    "id": "image-script",
                                    "props": {"Name": "BlockScript", "EditMode": 0},
                                    "fragments": [
                                        {
                                            "pos": ["0", "0"],
                                            "head": {
                                                "define": "WhenGameStarts",
                                                "sections": [
                                                    {
                                                        "children": [
                                                            {"define": "Show", "sections": [{"params": [{}]}]},
                                                        ]
                                                    }
                                                ],
                                            },
                                        }
                                    ],
                                    "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                                }
                            ],
                        }
                    ],
                    project_type=0,
                    show_myblock=True,
                    whitelist=[
                        {"define": "WhenGameStarts", "sections": [{"children": []}]},
                        {"define": "Show", "sections": [{"params": [{}]}]},
                    ],
                )
                end_user_whitelist_allowed_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": end_user_whitelist_allowed},
                )
                assert end_user_whitelist_allowed_validation["valid"] is True
                print("validate_workspace_end_user_whitelist_allowed: ok")

                end_user_whitelist_rejected = make_project_workspace(
                    [
                        {
                            "type": "ImageSet",
                            "id": "image-root",
                            "props": {"Name": "Sprite", "EditMode": 0},
                            "children": [
                                {
                                    "type": "BlockScript",
                                    "id": "image-script",
                                    "props": {"Name": "BlockScript", "EditMode": 0},
                                    "fragments": [
                                        {
                                            "pos": ["0", "0"],
                                            "head": {
                                                "define": "WhenGameStarts",
                                                "sections": [
                                                    {
                                                        "children": [
                                                            {
                                                                "define": "WaitSeconds",
                                                                "sections": [
                                                                    {
                                                                        "params": [
                                                                            {"type": "var", "val": "1"}
                                                                        ]
                                                                    }
                                                                ],
                                                            },
                                                        ]
                                                    }
                                                ],
                                            },
                                        }
                                    ],
                                    "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                                }
                            ],
                        }
                    ],
                    project_type=0,
                    show_myblock=True,
                    whitelist=[
                        {"define": "WhenGameStarts", "sections": [{"children": []}]},
                        {"define": "Show", "sections": [{"params": [{}]}]},
                    ],
                )
                end_user_whitelist_rejected_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": end_user_whitelist_rejected},
                )
                assert end_user_whitelist_rejected_validation["valid"] is False
                assert any(
                    "not present in project whitelist" in error
                    for error in end_user_whitelist_rejected_validation["errors"]
                )
                print("validate_workspace_end_user_whitelist_rejected: ok")

                end_user_whitelist_fragment_error = await expect_tool_error(
                    session,
                    "add_fragment",
                    {
                        "workspace_data": make_project_workspace(
                            [
                                {
                                    "type": "ImageSet",
                                    "id": "image-root",
                                    "props": {"Name": "Sprite", "EditMode": 0},
                                    "children": [
                                        {
                                            "type": "BlockScript",
                                            "id": "image-script",
                                            "props": {"Name": "BlockScript", "EditMode": 0},
                                            "fragments": [],
                                            "uiState": {
                                                "pos": ["0", "0"],
                                                "scroll": ["0", "0"],
                                                "scale": "1",
                                            },
                                        }
                                    ],
                                }
                            ],
                            project_type=0,
                            show_myblock=True,
                            whitelist=[
                                {"define": "WhenGameStarts", "sections": [{"children": []}]},
                                {"define": "Show", "sections": [{"params": [{}]}]},
                            ],
                        ),
                        "script_id": "image-script",
                        "fragment": {
                            "pos": ["0", "0"],
                            "head": {
                                "define": "WhenGameStarts",
                                "sections": [
                                    {
                                        "children": [
                                            {
                                                "define": "WaitSeconds",
                                                "sections": [{"params": [{"type": "var", "val": "1"}]}],
                                            }
                                        ]
                                    }
                                ],
                            },
                        },
                    },
                )
                assert "not present in project whitelist" in end_user_whitelist_fragment_error
                print("add_fragment_end_user_whitelist_rejected: ok")

                end_user_hidden_category = make_project_workspace(
                    [
                        {
                            "type": "CameraService",
                            "id": "camera-root",
                            "props": {"Name": "Camera", "EditMode": 0},
                            "children": [
                                {
                                    "type": "BlockScript",
                                    "id": "camera-script",
                                    "props": {"Name": "BlockScript", "EditMode": 0},
                                    "fragments": [
                                        {
                                            "pos": ["0", "0"],
                                            "head": {
                                                "define": "WhenGameStarts",
                                                "sections": [
                                                    {
                                                        "children": [
                                                            {
                                                                "define": "SetCameraDamping",
                                                                "sections": [
                                                                    {
                                                                        "params": [
                                                                            {"type": "var", "val": "all"},
                                                                            {"type": "var", "val": "1"},
                                                                            {"type": "var", "val": "1"},
                                                                            {"type": "var", "val": "1"},
                                                                        ]
                                                                    }
                                                                ],
                                                            }
                                                        ]
                                                    }
                                                ],
                                            },
                                        }
                                    ],
                                    "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                                }
                            ],
                        }
                    ],
                    project_type=0,
                    show_myblock=True,
                )
                end_user_hidden_category_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": end_user_hidden_category},
                )
                assert end_user_hidden_category_validation["valid"] is False
                assert any(
                    "category experiment is disabled" in error
                    for error in end_user_hidden_category_validation["errors"]
                )
                print("validate_workspace_end_user_hidden_category: ok")

                end_user_showmyblock_rejected = make_project_workspace(
                    [
                        {
                            "type": "Character",
                            "id": "character-root",
                            "props": {"Name": "Hero", "EditMode": 0},
                            "children": [
                                {
                                    "type": "BlockScript",
                                    "id": "character-script",
                                    "props": {"Name": "BlockScript", "EditMode": 0},
                                    "fragments": [],
                                    "myblocks": [
                                        {
                                            "name": "character-script/hidden/myblockdefine",
                                            "displayName": "Hidden",
                                            "wrapBlockName": "",
                                            "fragment": {
                                                "pos": ["0", "0"],
                                                "head": {
                                                    "define": "character-script/hidden/myblockdefine",
                                                    "sections": [{"children": []}],
                                                },
                                            },
                                        }
                                    ],
                                    "uiState": {"pos": ["0", "0"], "scroll": ["0", "0"], "scale": "1"},
                                }
                            ],
                        }
                    ],
                    project_type=0,
                    show_myblock=False,
                )
                end_user_showmyblock_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": end_user_showmyblock_rejected},
                )
                assert end_user_showmyblock_validation["valid"] is False
                assert any(
                    "showmyblock=false" in error for error in end_user_showmyblock_validation["errors"]
                )
                print("validate_workspace_end_user_showmyblock_rejected: ok")

                end_user_create_myblock_error = await expect_tool_error(
                    session,
                    "create_myblock",
                    {
                        "workspace_data": make_project_workspace(
                            [
                                {
                                    "type": "Character",
                                    "id": "character-root",
                                    "props": {"Name": "Hero", "EditMode": 0},
                                    "children": [
                                        {
                                            "type": "BlockScript",
                                            "id": "character-script",
                                            "props": {"Name": "BlockScript", "EditMode": 0},
                                            "fragments": [],
                                            "uiState": {
                                                "pos": ["0", "0"],
                                                "scroll": ["0", "0"],
                                                "scale": "1",
                                            },
                                        }
                                    ],
                                }
                            ],
                            project_type=0,
                            show_myblock=False,
                        ),
                        "script_id": "character-script",
                        "name": "hidden",
                        "display_name": "Hidden",
                        "parameters": [],
                        "yield": True,
                    },
                )
                assert "showmyblock=false" in end_user_create_myblock_error
                print("create_myblock_end_user_showmyblock_rejected: ok")

                scientific_notation_workspace = {
                    "scene": workspace["scene"],
                    "editorScene": {
                        "cameras": [
                            {
                                "name": "scientific-rotation",
                                "position": ["0", "0", "0"],
                                "rotation": ["0.224951", "-1.012205E-08", "4.384341E-08", "0.9743701"],
                                "fov": 25.0,
                            }
                        ]
                    },
                }
                scientific_notation_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": scientific_notation_workspace},
                )
                assert scientific_notation_workspace_validation["valid"] is True
                assert scientific_notation_workspace_validation["error_count"] == 0
                print("validate_workspace_scientific_notation: ok")

                invalid_resource_workspace = make_project_workspace([])
                invalid_resource_workspace["res"] = [999999999]
                invalid_resource_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": invalid_resource_workspace},
                )
                assert invalid_resource_workspace_validation["valid"] is False
                assert any(
                    "unknown resource id" in error
                    for error in invalid_resource_workspace_validation["errors"]
                )
                print("validate_workspace_resource_ids: ok")
    
                invalid_myblock_workspace = {
                    "type": "BlockScript",
                    "id": "root",
                    "fragments": [],
                    "myblocks": [
                        {
                            "name": "root/bad/myblockdefine",
                            "displayName": "Bad",
                            "fragment": {
                                "pos": ["0", "0"],
                                "head": {"sections": [{}]},
                            },
                        }
                    ],
                }
                invalid_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": invalid_myblock_workspace},
                )
                assert invalid_workspace_validation["valid"] is False
                print("validate_workspace_myblock_fragment: ok")

                mismatched_myblock_workspace = {
                    "type": "BlockScript",
                    "id": "root",
                    "fragments": [],
                    "myblocks": [
                        {
                            "name": "root/good/myblockdefine",
                            "displayName": "Good",
                            "fragment": {
                                "pos": ["0", "0"],
                                "head": {
                                    "define": "WhenGameStarts",
                                    "sections": [{"children": []}],
                                },
                            },
                        }
                    ],
                }
                mismatched_myblock_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": mismatched_myblock_workspace},
                )
                assert mismatched_myblock_validation["valid"] is False
                assert any(
                    "fragment.head.define must match myblock name" in error
                    for error in mismatched_myblock_validation["errors"]
                )
                print("validate_workspace_myblock_head_binding: ok")
    
                missing_custom_call_workspace = {
                    "type": "BlockScript",
                    "id": "root",
                    "fragments": [
                        {
                            "pos": ["0", "0"],
                            "head": {
                                "define": "WhenGameStarts",
                                "sections": [
                                    {
                                        "children": [
                                            {
                                                "define": "root/missing/myblockdefine",
                                                "sections": [{"params": []}],
                                            }
                                        ]
                                    }
                                ],
                            },
                        }
                    ],
                    "myblocks": [],
                }
                missing_custom_workspace_validation = await call_json(
                    session,
                    "validate_workspace",
                    {"workspace_data": missing_custom_call_workspace},
                )
                assert missing_custom_workspace_validation["valid"] is True
                assert missing_custom_workspace_validation["error_count"] == 0
                assert "undefined myblock" in "\n".join(missing_custom_workspace_validation["warnings"])
                print("validate_workspace_missing_custom_myblock: ok")
    
                save_message = await call_text(
                    session,
                    "save_workspace_file",
                    {
                        "file_path": TEMP_FILE,
                        "content": workspace,
                        "create_backup": False,
                    },
                )
                assert "File saved successfully" in save_message
                print("save_workspace_file: ok")

                invalid_save_error = await expect_tool_error(
                    session,
                    "save_workspace_file",
                    {
                        "file_path": "reference/smoke/test-api-smoke.invalid.generated.ws",
                        "content": invalid_effect_workspace,
                        "create_backup": False,
                    },
                )
                assert "Workspace validation failed before save" in invalid_save_error
                assert "scene.children[0].props.AssetId must be integer" in invalid_save_error
                print("save_workspace_file_validation_rejected: ok")
    
                reloaded = await call_json(
                    session, "load_workspace_file", {"file_path": TEMP_FILE}
                )
                assert reloaded["data"]["name"] == workspace["name"]
                print("reload_saved_file: ok")
    
            print("all_smoke_tests_passed")
        return 0
    finally:
        temp_output.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
