"""应用配置（所有硬编码的配置在这里集中管理）"""
from pathlib import Path
import sys
import threading
import urllib.request
import json
import logging

_cfg_log = logging.getLogger("levelassistant.config")

APP_NAME = "关卡助手"
APP_VERSION = "1.0.8"

# ── 热更新配置 ────────────────────────────────────────────────────────────────
# 填入你的 GitHub 仓库 raw 地址，留空则禁用热更新
# 示例：https://raw.githubusercontent.com/你的用户名/LevelAssistant/main/version.json
UPDATE_VERSION_URL = "https://cdn.jsdelivr.net/gh/YM998AFK/LevelAssistant@master/version.json"

# 国内加速代理（推荐保留，访问 GitHub 更稳定）
# 留空则直连 GitHub
UPDATE_PROXY_PREFIX = ""

# ── 主通道：新 LiteLLM 网关（TLS 1.2，Anthropic 格式，优先使用）──────────────
NEW_API_KEY      = "sk-lsWY2BhAStHgXT302nF98w"
NEW_API_BASE_URL = "https://ai-gateway.corp.hetao101.com"
NEW_API_MODEL    = "global.anthropic.claude-sonnet-4-6"

# ── 备用通道：旧内部代理 ──────────────────────────────────────────────────────
ANTHROPIC_API_KEY  = "dummy"
ANTHROPIC_BASE_URL = "http://10.200.30.19:14000"
DEFAULT_MODEL      = "claude-sonnet-4-6"

CLAUDE_USER_AGENT  = "claude-cli/1.0.58 (external, cli)"

# ── API 版本自动探测 ───────────────────────────────────────────────────────────
# 按从新到旧排列，探测时取第一个代理服务器接受的版本
_ANTHROPIC_VERSION_CANDIDATES = ["2024-11-01", "2023-06-01"]
_detected_api_version: str | None = None
_version_lock = threading.Lock()


def _probe_api_version() -> str:
    """向代理发送最小测试请求，返回第一个可用的 anthropic-version。"""
    body = json.dumps({
        "model": DEFAULT_MODEL,
        "max_tokens": 1,
        "messages": [{"role": "user", "content": "v"}],
    }).encode()
    for version in _ANTHROPIC_VERSION_CANDIDATES:
        try:
            req = urllib.request.Request(
                f"{ANTHROPIC_BASE_URL}/v1/messages",
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": ANTHROPIC_API_KEY,
                    "User-Agent": CLAUDE_USER_AGENT,
                    "anthropic-version": version,
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    _cfg_log.info("API 版本探测成功：%s", version)
                    return version
        except Exception as e:
            _cfg_log.debug("API 版本 %s 不可用：%s", version, e)
    _cfg_log.warning("所有 API 版本探测失败，使用默认值：%s", _ANTHROPIC_VERSION_CANDIDATES[0])
    return _ANTHROPIC_VERSION_CANDIDATES[0]


def get_anthropic_api_version() -> str:
    """返回当前代理接受的 anthropic-version（首次调用时自动探测，结果缓存）。"""
    global _detected_api_version
    if _detected_api_version is not None:
        return _detected_api_version
    with _version_lock:
        if _detected_api_version is None:
            _detected_api_version = _probe_api_version()
    return _detected_api_version

def make_new_api_http_client():
    """创建适用于新 LiteLLM 网关的 httpx 客户端（强制 TLS 1.2，服务器不支持 1.3）。"""
    import ssl, httpx
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    return httpx.Client(transport=httpx.HTTPTransport(verify=ctx), timeout=120.0)


def make_new_api_async_http_client():
    """异步版本（供 AsyncAnthropic 使用）。"""
    import ssl, httpx
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    return httpx.AsyncClient(transport=httpx.AsyncHTTPTransport(verify=ctx), timeout=120.0)


AVAILABLE_MODELS = [
    "claude-sonnet-4-6",
    "claude-3-7-sonnet",
    "claude-3-5-sonnet-20241022",
    "claude-haiku-4-5-20251001",
]

MAX_TOOL_ITERATIONS = 100
MAX_TOKENS_PER_TURN = 32000
THINKING_BUDGET_TOKENS = 10000   # 扩展思考 token 预算（含在 max_tokens 内）


def base_dir() -> Path:
    """定位资源根目录：打包后指向 exe 所在目录，开发时指向项目根"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def skills_dir() -> Path:
    """skills 根目录（含 mcp、scripts 等）。
    onedir 打包模式下 skills/ 与 exe 同级，热更新时也写到这里。"""
    return base_dir() / "skills"


def cursor_skills_dir() -> Path:
    """Cursor skill 包目录，SKILL.md 都在这里"""
    return skills_dir() / ".cursor" / "skills-v2"


def mcp_dir() -> Path:
    """MCP 插件目录"""
    return skills_dir() / "mcp"


def output_dir() -> Path:
    """AI 最终产出目录，写入前自动创建。"""
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
    "resource_search": {"label": "资源搜索", "icon": "🔍", "default_skill": None},
    "free_chat":       {"label": "自由对话", "icon": "💬", "default_skill": None},
}


import time as _time_mod

class ChannelHealth:
    """
    全局通道健康度追踪器。
    自动记录每个通道的失败情况，为每次请求推荐最优通道顺序。

    通道编号约定：
      0 = 新 LiteLLM 网关（NEW_API_BASE_URL）
      1 = 旧内部代理（ANTHROPIC_BASE_URL）
    """

    # 超过此连续失败次数后，该通道优先级下降
    _FAILURE_THRESHOLD = 2
    # 降级后多少秒重新尝试该通道（探测恢复）
    _RETRY_AFTER = 120

    def __init__(self):
        self._lock = threading.Lock()
        self._stats = {
            0: {"failures": 0, "last_fail": 0.0, "budget_exceeded": False, "last_success": 0.0},
            1: {"failures": 0, "last_fail": 0.0, "budget_exceeded": False, "last_success": 0.0},
        }

    def mark_success(self, ch: int) -> None:
        with self._lock:
            s = self._stats[ch]
            s["failures"] = 0
            s["last_success"] = _time_mod.time()

    def mark_failure(self, ch: int, budget_exceeded: bool = False) -> None:
        with self._lock:
            s = self._stats[ch]
            s["failures"] += 1
            s["last_fail"] = _time_mod.time()
            if budget_exceeded:
                s["budget_exceeded"] = True

    def is_budget_exceeded(self, ch: int) -> bool:
        with self._lock:
            return self._stats[ch]["budget_exceeded"]

    def get_channel_order(self) -> list[int]:
        """
        返回通道列表，按当前健康度从优到劣排序。
        - budget_exceeded 的通道排到最后
        - 连续失败超过阈值且未到重试窗口的通道排后
        - 其余按最近成功时间倒序（最近成功的优先）
        """
        now = _time_mod.time()
        with self._lock:
            def _score(ch: int) -> tuple:
                s = self._stats[ch]
                if s["budget_exceeded"]:
                    return (3, 0)  # 永久最低优先级
                # 连续失败超阈值且仍在冷却窗口内 → 降级
                in_cooldown = (
                    s["failures"] >= self._FAILURE_THRESHOLD
                    and (now - s["last_fail"]) < self._RETRY_AFTER
                )
                if in_cooldown:
                    return (2, -s["last_fail"])  # 失败越早，越早尝试恢复
                # 正常：失败越少、最近成功越新，优先级越高
                return (1 if s["failures"] > 0 else 0, -s["last_success"])

            return sorted(self._stats.keys(), key=_score)

    def reset_budget_exceeded(self, ch: int) -> None:
        """管理员续费后可调用此方法重置 budget_exceeded 标记。"""
        with self._lock:
            self._stats[ch]["budget_exceeded"] = False
            self._stats[ch]["failures"] = 0

    def status_str(self) -> str:
        """返回可读的健康状态字符串，供日志输出。"""
        with self._lock:
            parts = []
            for ch, s in self._stats.items():
                name = "新网关" if ch == 0 else "旧代理"
                if s["budget_exceeded"]:
                    tag = "❌额度耗尽"
                elif s["failures"] == 0:
                    tag = "✅正常"
                else:
                    tag = f"⚠️失败{s['failures']}次"
                parts.append(f"{name}:{tag}")
            return " | ".join(parts)


# 全局单例，agent.py / tools.py 直接 import 使用
channel_health = ChannelHealth()
