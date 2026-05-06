"""
Hetu MCP Server package initialization.
"""

from .version import __version__
__author__ = "Hetu Team"
__description__ = "Hetu MCP server for Hetu workspace editing and validation"

from .server import HetuMcpServer, main
from .definitions.block_models import BlockModel, BlockType, BlockCategory

__all__ = [
    "HetuMcpServer",
    "main",
    "BlockModel",
    "BlockType",
    "BlockCategory",
]
