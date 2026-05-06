"""
Hetu MCP Server
"""

import asyncio
import json
from pathlib import Path
import sys
from typing import Optional, Sequence

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio


PACKAGE_ROOT = Path(__file__).resolve().parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))


from version import __version__


class HetuMcpServer:
    def __init__(self):
        self.server = Server("hetu-mcp")
        self.workspace_root: Optional[Path] = None
        self._ensure_resource_data()
        self._register_handlers()

    def _ensure_resource_data(self):
        from definitions.resource_definitions import ensure_resource_data

        ensure_resource_data()

    def _register_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="load_workspace_file",
                    description="Load and parse a .ws workspace file.",
                    inputSchema={
                        "type": "object",
                        "properties": {"file_path": {"type": "string"}},
                        "required": ["file_path"],
                    },
                ),
                types.Tool(
                    name="save_workspace_file",
                    description="Save workspace JSON to a .ws file.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "content": {"type": "object"},
                            "create_backup": {"type": "boolean", "default": True},
                            "validate_before_save": {"type": "boolean", "default": True},
                        },
                        "required": ["file_path", "content"],
                    },
                ),
                types.Tool(
                    name="get_fragments",
                    description="List fragments from a BlockScript or a full .ws workspace.",
                    inputSchema={
                        "type": "object",
                        "properties": {"workspace_data": {"type": "object"}},
                        "required": ["workspace_data"],
                    },
                ),
                types.Tool(
                    name="add_fragment",
                    description=(
                        "Add a fragment to a BlockScript. script_id is required for multi-script workspaces; "
                        "scene-element owner block restrictions are enforced when owner context is available."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_data": {"type": "object"},
                            "fragment": {"type": "object"},
                            "script_id": {"type": "string"},
                        },
                        "required": ["workspace_data", "fragment"],
                    },
                ),
                types.Tool(
                    name="remove_fragment",
                    description="Remove a fragment by index from a BlockScript. script_id is required for multi-script workspaces.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_data": {"type": "object"},
                            "fragment_index": {"type": "integer"},
                            "script_id": {"type": "string"},
                        },
                        "required": ["workspace_data", "fragment_index"],
                    },
                ),
                types.Tool(
                    name="update_fragment_position",
                    description="Update a fragment position. script_id is required for multi-script workspaces.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_data": {"type": "object"},
                            "fragment_index": {"type": "integer"},
                            "position": {"type": "array", "items": {"type": "string"}},
                            "script_id": {"type": "string"},
                        },
                        "required": ["workspace_data", "fragment_index", "position"],
                    },
                ),
                types.Tool(
                    name="create_block",
                    description="Create a block from a block definition.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "block_define": {"type": "string"},
                            "parameters": {"type": "object"},
                            "position": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["block_define"],
                    },
                ),
                types.Tool(
                    name="get_block_info",
                    description="Inspect a block.",
                    inputSchema={
                        "type": "object",
                        "properties": {"block": {"type": "object"}},
                        "required": ["block"],
                    },
                ),
                types.Tool(
                    name="modify_block_parameter",
                    description="Modify a block parameter by index.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "block": {"type": "object"},
                            "parameter_index": {"type": "integer"},
                            "value": {},
                        },
                        "required": ["block", "parameter_index", "value"],
                    },
                ),
                types.Tool(
                    name="append_block",
                    description="Append a block to the end of a chain or branch child list.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "block": {"type": "object"},
                            "new_block": {"type": "object"},
                        },
                        "required": ["block", "new_block"],
                    },
                ),
                types.Tool(
                    name="insert_block_child",
                    description="Insert a child block into a branch section.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "block": {"type": "object"},
                            "section_index": {"type": "integer"},
                            "child_block": {"type": "object"},
                        },
                        "required": ["block", "section_index", "child_block"],
                    },
                ),
                types.Tool(
                    name="create_myblock",
                    description="Create a myblock definition in a BlockScript. script_id is required for multi-script workspaces.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_data": {"type": "object"},
                            "name": {"type": "string"},
                            "display_name": {"type": "string"},
                            "parameters": {"type": "array", "items": {"type": "object"}},
                            "yield": {"type": "boolean", "default": True},
                            "script_id": {"type": "string"},
                        },
                        "required": ["workspace_data", "name", "display_name"],
                    },
                ),
                types.Tool(
                    name="get_myblocks",
                    description="List myblock definitions from a BlockScript or full .ws workspace.",
                    inputSchema={
                        "type": "object",
                        "properties": {"workspace_data": {"type": "object"}},
                        "required": ["workspace_data"],
                    },
                ),
                types.Tool(
                    name="remove_myblock",
                    description="Remove a myblock definition. script_id is required for multi-script workspaces.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_data": {"type": "object"},
                            "myblock_name": {"type": "string"},
                            "script_id": {"type": "string"},
                        },
                        "required": ["workspace_data", "myblock_name"],
                    },
                ),
                types.Tool(
                    name="update_myblock_fragment",
                    description=(
                        "Replace the fragment implementation for a myblock; scene-element owner block "
                        "restrictions are enforced when owner context is available."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_data": {"type": "object"},
                            "myblock_name": {"type": "string"},
                            "fragment": {"type": "object"},
                            "script_id": {"type": "string"},
                        },
                        "required": ["workspace_data", "myblock_name", "fragment"],
                    },
                ),
                types.Tool(
                    name="create_myblock_call",
                    description="Create a myblock call block.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "myblock_name": {"type": "string"},
                            "parameter_values": {"type": "array"},
                        },
                        "required": ["myblock_name"],
                    },
                ),
                types.Tool(
                    name="find_myblock_usages",
                    description="Find usages of a myblock across a BlockScript or full .ws workspace.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_data": {"type": "object"},
                            "myblock_name": {"type": "string"},
                        },
                        "required": ["workspace_data", "myblock_name"],
                    },
                ),
                types.Tool(
                    name="validate_block",
                    description="Validate a block structure.",
                    inputSchema={
                        "type": "object",
                        "properties": {"block": {"type": "object"}},
                        "required": ["block"],
                    },
                ),
                types.Tool(
                    name="find_blocks_by_type",
                    description="Find blocks by define name across a BlockScript or full .ws workspace.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_data": {"type": "object"},
                            "block_define": {"type": "string"},
                        },
                        "required": ["workspace_data", "block_define"],
                    },
                ),
                types.Tool(
                    name="get_block_documentation",
                    description="Get documentation for a block define.",
                    inputSchema={
                        "type": "object",
                        "properties": {"block_define": {"type": "string"}},
                        "required": ["block_define"],
                    },
                ),
                types.Tool(
                    name="get_modules",
                    description=(
                        "List serialized modules from one module node or a full .ws workspace, including "
                        "scene-element block target restrictions when applicable."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {"workspace_data": {"type": "object"}},
                        "required": ["workspace_data"],
                    },
                ),
                types.Tool(
                    name="validate_module",
                    description=(
                        "Validate a serialized module object and return scene-element block target "
                        "restriction metadata when applicable."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {"module": {"type": "object"}},
                        "required": ["module"],
                    },
                ),
                types.Tool(
                    name="find_modules_by_type",
                    description="Find serialized modules by type across one module node or a full .ws workspace.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace_data": {"type": "object"},
                            "module_type": {"type": "string"},
                        },
                        "required": ["workspace_data", "module_type"],
                    },
                ),
                types.Tool(
                    name="get_module_documentation",
                    description=(
                        "Get documentation for a serialized module type, including scene-element block "
                        "support restrictions when applicable."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {"module_type": {"type": "string"}},
                        "required": ["module_type"],
                    },
                ),
                types.Tool(
                    name="get_resource",
                    description="Get one detailed resource record by resource_id from mcp/hetu_mcp/resource/resource_index.json.",
                    inputSchema={
                        "type": "object",
                        "properties": {"resource_id": {"type": ["integer", "string"]}},
                        "required": ["resource_id"],
                    },
                ),
                types.Tool(
                    name="find_resources",
                    description="Find detailed resource records by resource id/name/type, entry kind/class/category, or entry id/name.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "resource_id": {"type": ["integer", "string"]},
                            "resource_name": {"type": "string"},
                            "resource_type": {"type": "string"},
                            "entry_id": {"type": ["integer", "string"]},
                            "entry_name": {"type": "string"},
                            "entry_kind": {"type": "string", "enum": ["asset", "sprite"]},
                            "entry_class_id": {"type": ["integer", "string"]},
                            "entry_type": {"type": "string"},
                            "entry_category_id": {"type": ["integer", "string"]},
                            "entry_category": {"type": "string"},
                            "limit": {"type": "integer", "default": 20},
                        },
                    },
                ),
                types.Tool(
                    name="validate_resource",
                    description="Validate a resource reference against generated resource definitions and resource data.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "resource_id": {"type": ["integer", "string"]},
                            "resource_name": {"type": "string"},
                            "resource_type": {"type": "string"},
                            "entry_kind": {"type": "string", "enum": ["asset", "sprite"]},
                            "entry_class_id": {"type": ["integer", "string"]},
                            "entry_type": {"type": "string"},
                            "entry_category_id": {"type": ["integer", "string"]},
                            "entry_category": {"type": "string"},
                            "require_primary_url": {"type": "boolean", "default": False},
                        },
                    },
                ),
                types.Tool(
                    name="analyze_workspace_statistics",
                    description="Analyze workspace statistics across one BlockScript or a full .ws workspace.",
                    inputSchema={
                        "type": "object",
                        "properties": {"workspace_data": {"type": "object"}},
                        "required": ["workspace_data"],
                    },
                ),
                types.Tool(
                    name="validate_workspace",
                    description=(
                        "Validate one BlockScript or a full .ws workspace, including scene-element owner "
                        "block restrictions, project policy, and resource ids."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {"workspace_data": {"type": "object"}},
                        "required": ["workspace_data"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict | None
        ) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            if arguments is None:
                raise ValueError("Missing arguments")

            from handlers import (
                block_operations,
                resource_operations,
                workspace_operations,
                validation_operations,
            )

            if name == "load_workspace_file":
                result = await workspace_operations.load_workspace_file(
                    arguments["file_path"],
                    self.workspace_root,
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "save_workspace_file":
                result = await workspace_operations.save_workspace_file(
                    arguments["file_path"],
                    arguments["content"],
                    self.workspace_root,
                    arguments.get("create_backup", True),
                    arguments.get("validate_before_save", True),
                )
                return [types.TextContent(type="text", text=result)]

            if name == "get_fragments":
                result = workspace_operations.get_fragments(arguments["workspace_data"])
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "add_fragment":
                result = workspace_operations.add_fragment(
                    arguments["workspace_data"],
                    arguments["fragment"],
                    arguments.get("script_id"),
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "remove_fragment":
                result = workspace_operations.remove_fragment(
                    arguments["workspace_data"],
                    arguments["fragment_index"],
                    arguments.get("script_id"),
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "update_fragment_position":
                result = workspace_operations.update_fragment_position(
                    arguments["workspace_data"],
                    arguments["fragment_index"],
                    arguments["position"],
                    arguments.get("script_id"),
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "create_block":
                result = block_operations.create_block(
                    arguments["block_define"],
                    arguments.get("parameters"),
                    arguments.get("position"),
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "get_block_info":
                result = block_operations.get_block_info(arguments["block"])
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "modify_block_parameter":
                result = block_operations.modify_block_parameter(
                    arguments["block"],
                    arguments["parameter_index"],
                    arguments["value"],
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "append_block":
                result = block_operations.append_block(arguments["block"], arguments["new_block"])
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "insert_block_child":
                result = block_operations.insert_block_child(
                    arguments["block"],
                    arguments["section_index"],
                    arguments["child_block"],
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "create_myblock":
                result = workspace_operations.create_myblock(
                    arguments["workspace_data"],
                    arguments["name"],
                    arguments["display_name"],
                    arguments.get("parameters", []),
                    arguments.get("yield", True),
                    arguments.get("script_id"),
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "get_myblocks":
                result = workspace_operations.get_myblocks(arguments["workspace_data"])
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "remove_myblock":
                result = workspace_operations.remove_myblock(
                    arguments["workspace_data"],
                    arguments["myblock_name"],
                    arguments.get("script_id"),
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "update_myblock_fragment":
                result = workspace_operations.update_myblock_fragment(
                    arguments["workspace_data"],
                    arguments["myblock_name"],
                    arguments["fragment"],
                    arguments.get("script_id"),
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "create_myblock_call":
                result = workspace_operations.create_myblock_call(
                    arguments["myblock_name"],
                    arguments.get("parameter_values", []),
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "find_myblock_usages":
                result = workspace_operations.find_myblock_usages(
                    arguments["workspace_data"],
                    arguments["myblock_name"],
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "validate_block":
                result = validation_operations.validate_block(arguments["block"])
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "find_blocks_by_type":
                result = validation_operations.find_blocks_by_type(
                    arguments["workspace_data"],
                    arguments["block_define"],
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "get_block_documentation":
                result = validation_operations.get_block_documentation(arguments["block_define"])
                return [types.TextContent(type="text", text=result)]

            if name == "get_modules":
                result = validation_operations.get_modules(arguments["workspace_data"])
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "validate_module":
                result = validation_operations.validate_module(arguments["module"])
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "find_modules_by_type":
                result = validation_operations.find_modules_by_type(
                    arguments["workspace_data"],
                    arguments["module_type"],
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "get_module_documentation":
                result = validation_operations.get_module_documentation(arguments["module_type"])
                return [types.TextContent(type="text", text=result)]

            if name == "get_resource":
                result = resource_operations.get_resource(arguments["resource_id"])
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "find_resources":
                result = resource_operations.find_resources(
                    resource_id=arguments.get("resource_id"),
                    resource_name=arguments.get("resource_name"),
                    resource_type=arguments.get("resource_type"),
                    entry_id=arguments.get("entry_id"),
                    entry_name=arguments.get("entry_name"),
                    entry_kind=arguments.get("entry_kind"),
                    entry_class_id=arguments.get("entry_class_id"),
                    entry_type=arguments.get("entry_type"),
                    entry_category_id=arguments.get("entry_category_id"),
                    entry_category=arguments.get("entry_category"),
                    limit=arguments.get("limit", 20),
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "validate_resource":
                result = resource_operations.validate_resource(
                    resource_id=arguments.get("resource_id"),
                    resource_name=arguments.get("resource_name"),
                    resource_type=arguments.get("resource_type"),
                    entry_kind=arguments.get("entry_kind"),
                    entry_class_id=arguments.get("entry_class_id"),
                    entry_type=arguments.get("entry_type"),
                    entry_category_id=arguments.get("entry_category_id"),
                    entry_category=arguments.get("entry_category"),
                    require_primary_url=arguments.get("require_primary_url", False),
                )
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "analyze_workspace_statistics":
                result = validation_operations.analyze_workspace_statistics(arguments["workspace_data"])
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            if name == "validate_workspace":
                result = validation_operations.validate_workspace(arguments["workspace_data"])
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            raise ValueError(f"Unknown tool: {name}")

    async def run(self):
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="hetu-mcp",
                    server_version=__version__,
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


def main():
    import sys

    workspace_root = None
    if len(sys.argv) > 1:
        workspace_root = Path(sys.argv[1])

    server = HetuMcpServer()
    server.workspace_root = workspace_root
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
