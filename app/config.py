"""应用配置（所有硬编码的配置在这里集中管理）"""
from pathlib import Path
import sys

APP_NAME = "关卡助手"
APP_VERSION = "1.0.0"

ANTHROPIC_API_KEY = "dummy"
ANTHROPIC_BASE_URL = "http://10.200.30.19:14000"
CLAUDE_USER_AGENT = "claude-cli/1.0.58 (external, cli)"
DEFAULT_MODEL = "claude-sonnet-4-6"

AVAILABLE_MODELS = [
    "claude-sonnet-4-6",
    "claude-3-7-sonnet",
    "claude-3-5-sonnet-20241022",
    "claude-haiku-4-5-20251001",
]

MAX_TOOL_ITERATIONS = 100
MAX_TOKENS_PER_TURN = 16000


def base_dir() -> Path:
    """定位资源根目录：打包后指向 exe 所在目录，开发时指向项目根"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def skills_dir() -> Path:
    """skills 根目录（含 mcp、scripts、output 等）"""
    return base_dir() / "skills"


def cursor_skills_dir() -> Path:
    """Cursor skill 包目录，SKILL.md 都在这里"""
    return skills_dir() / ".cursor" / "skills"


def mcp_dir() -> Path:
    """MCP 插件目录"""
    return skills_dir() / "mcp"


def output_dir() -> Path:
    """AI 最终产出目录（项目根/output），写入前自动创建。
    打包模式下 exe 在 dist/，output 放在 dist 的父目录（即项目根）下。"""
    if getattr(sys, "frozen", False):
        d = Path(sys.executable).parent.parent / "output"
    else:
        d = base_dir() / "output"
    d.mkdir(parents=True, exist_ok=True)
    return d


def workspace_dir() -> Path:
    d = base_dir() / "workspaces"
    d.mkdir(parents=True, exist_ok=True)
    return d


MODES = {
    "modify":          {"label": "修改关卡", "icon": "✏",  "default_skill": "level-modify"},
    "create_level":    {"label": "新建关卡", "icon": "🆕", "default_skill": "level-new"},
    "create_story":    {"label": "新建剧情", "icon": "📖", "default_skill": "level-new"},
    "resource_search": {"label": "资源搜索", "icon": "🔍", "default_skill": "resource-search"},
    "free_chat":       {"label": "自由对话", "icon": "💬", "default_skill": None},
}
