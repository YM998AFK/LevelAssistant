"""主窗口：顶部栏 + 模式切换 + 侧边栏 + 对话区。"""
from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional
import uuid
import shutil

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox,
)

from ..config import (
    APP_NAME, APP_VERSION, MODES, workspace_dir, DEFAULT_MODEL,
    UPDATE_VERSION_URL, UPDATE_PROXY_PREFIX,
)
from ..skills import skills_for_mode, Skill
from ..agent import AgentWorker, ReviewWorker, build_system_prompt, build_review_prompt
from ..logger import get_app_logger, setup_task_logging
from .sidebar import Sidebar
from .chat_view import ChatView, MessageBlock
from .update_dialog import UpdateNotifyDialog
from ..updater import UpdateChecker


MAX_SESSIONS = 10   # 每个模式最多保留的会话数

# ── 单条会话数据 ───────────────────────────────────────────────────────
def _new_session(name: str) -> dict:
    return {
        "name": name,
        "messages": [],
        "display": [],          # (role, text) 最多 30 条
        "workspace": None,
        "current_skill": None,
        "uploaded_files": [],
        "task_logger": None,
        "sidebar_state": {},    # 侧边栏输入快照
        "status_bar_state": {}, # 状态栏快照（工具历史 + 思考行）
        # 并行运行支持
        "worker": None,
        "review_worker": None,
        "status": "idle",       # idle / running / reviewing / done / error / stopped
        "ai_buf": [],           # 后台运行时累积的全部文本
        "final_buf": [],        # 工具调用之间的最后一段文本（用于展示最终回复）
        "task_start_time": 0.0,
        "task_description": "",
        "review_buf": [],
        "created_archives": [],     # 本次任务产出的 zip 路径（精确追踪，避免并行串场）
        "review_attempt": 0,        # 审查重试次数（最多 1 次自动重试）
    }


class ModeTabs(QWidget):
    mode_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ModeBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(0)
        self.buttons = {}
        for key, cfg in MODES.items():
            btn = QPushButton(cfg["label"])
            btn.setProperty("modeTab", True)
            btn.setProperty("active", key == "modify")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _=False, k=key: self._select(k))
            layout.addWidget(btn)
            self.buttons[key] = btn
        self._current = "modify"

    def _select(self, key: str):
        if key == self._current:
            return
        self._current = key
        for k, btn in self.buttons.items():
            btn.setProperty("active", k == key)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.mode_changed.emit(key)

    def current(self) -> str:
        return self._current


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 820)
        self._center_window()

        self._log = get_app_logger()
        self.current_mode = "modify"

        # 活动会话的便捷引用（随 _restore_session_state 更新）
        self.messages: list = []
        self.workspace: Optional[Path] = None
        self.current_skill: Optional[Skill] = None
        self.uploaded_files: list[str] = []
        self.task_logger = None
        self.current_ai_message: Optional[MessageBlock] = None
        self.review_message: Optional[MessageBlock] = None
        self._current_iter: int = 0
        self._last_tool_chip = None

        # 每个模式有多个会话，mode_state[mode] = {"sessions": [...], "current_session": 0}
        self.mode_state: dict = {
            mode: {
                "sessions": [_new_session("会话 1")],
                "current_session": 0,
            }
            for mode in MODES
        }

        self._build_ui()
        self._wire()
        self._load_history()
        self._restore_session_state()   # 还原上次会话（内部若无内容则显示欢迎语）
        self._update_checker: UpdateChecker | None = None
        # 延迟 0.5 秒等主窗口渲染完毕后立即检查更新
        if UPDATE_VERSION_URL:
            QTimer.singleShot(500, self._check_for_updates)

    def _center_window(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move((screen.width() - self.width()) // 2,
                  (screen.height() - self.height()) // 2)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        top = QWidget()
        top.setObjectName("TopBar")
        top.setFixedHeight(56)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(16, 8, 16, 8)
        top_layout.setSpacing(8)

        menu_btn = QPushButton("☰")
        menu_btn.setObjectName("IconButton")
        menu_btn.setCursor(Qt.PointingHandCursor)
        top_layout.addWidget(menu_btn)

        logo_wrap = QWidget()
        logo_wrap.setStyleSheet("background: transparent;")
        logo_row = QHBoxLayout(logo_wrap)
        logo_row.setContentsMargins(0, 0, 0, 0)
        logo_row.setSpacing(7)

        logo_icon = QLabel("L")
        logo_icon.setFixedSize(24, 24)
        logo_icon.setAlignment(Qt.AlignCenter)
        logo_icon.setStyleSheet(
            "background: #7C3AED; color: white; border-radius: 6px;"
            "font-size: 12px; font-weight: 800;"
        )
        logo_row.addWidget(logo_icon)

        title = QLabel(APP_NAME)
        title.setObjectName("AppTitle")
        logo_row.addWidget(title)

        ver_label = QLabel(f"v{APP_VERSION}")
        ver_label.setStyleSheet(
            "background: transparent; color: #A1A1AA; font-size: 11px;"
        )
        ver_label.setAlignment(Qt.AlignVCenter)
        logo_row.addWidget(ver_label)

        top_layout.addWidget(logo_wrap)

        top_layout.addStretch()
        self.mode_tabs = ModeTabs()
        top_layout.addWidget(self.mode_tabs)
        top_layout.addStretch()

        avatar = QLabel("H")
        avatar.setObjectName("UserAvatar")
        avatar.setFixedSize(28, 28)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("""
            background: #7C3AED; color: white; border-radius: 14px;
            font-weight: 600; font-size: 12px;
        """)
        top_layout.addWidget(avatar)
        top_layout.addSpacing(4)

        self.clear_history_btn = QPushButton("🗑 清空历史")
        self.clear_history_btn.setObjectName("IconButton")
        self.clear_history_btn.setCursor(Qt.PointingHandCursor)
        self.clear_history_btn.setToolTip("清空所有已保存的历史记录")
        top_layout.addWidget(self.clear_history_btn)

        root.addWidget(top)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.sidebar = Sidebar()
        body.addWidget(self.sidebar)

        self.chat = ChatView()
        body.addWidget(self.chat, 1)

        body_wrap = QWidget()
        body_wrap.setLayout(body)
        root.addWidget(body_wrap, 1)

    def _wire(self):
        self.mode_tabs.mode_changed.connect(self._on_mode_change)
        self.sidebar.start_requested.connect(self._on_start_task)
        self.chat.send_requested.connect(self._on_chat_send)
        self.chat.stop_requested.connect(self._stop_agent)
        self.clear_history_btn.clicked.connect(self._clear_all_history)
        self.chat.session_changed.connect(self._on_session_switch)
        self.chat.session_add.connect(self._on_session_add)

    def _current_session(self) -> dict:
        ms = self.mode_state[self.current_mode]
        return ms["sessions"][ms["current_session"]]

    def _session_names(self) -> list[str]:
        return [s["name"] for s in self.mode_state[self.current_mode]["sessions"]]

    def _make_tab_label(self, description: str, max_len: int = 10) -> str:
        """从描述文字生成 ≤max_len 字的标签页标题。"""
        text = description.strip().replace("\n", " ").replace("\r", "")
        if not text:
            return "新会话"
        return text[:max_len] + "…" if len(text) > max_len else text

    def _session_statuses(self) -> list[str]:
        return [s["status"] for s in self.mode_state[self.current_mode]["sessions"]]

    def _refresh_session_bar(self):
        ms = self.mode_state[self.current_mode]
        self.chat.set_sessions(
            self._session_names(),
            ms["current_session"],
            self._session_statuses(),
        )
        # 计算后台活动（非当前 session 但正在运行的）
        cur = ms["current_session"]
        bg_items = []
        for i, sess in enumerate(ms["sessions"]):
            if i == cur:
                continue
            if sess["status"] in ("running", "reviewing"):
                last_tool = ""
                last_think = ""
                # 从工具历史取最近一个工具名
                bar_snap = sess.get("status_bar_state", {})
                th = bar_snap.get("tool_history", [])
                if th:
                    last_tool = th[-1][0]
                tk = bar_snap.get("think_lines", [])
                if tk:
                    last_think = tk[-1]
                bg_items.append({
                    "name": sess["name"],
                    "tool": last_tool,
                    "thinking": last_think,
                })
        self.chat.set_background_activity(bg_items)

    def _show_welcome(self):
        if self.current_mode == "free_chat":
            self.chat.add_hint(
                "自由对话模式：直接在下方输入框发消息即可。"
            )
        elif self.current_mode == "resource_search":
            self.chat.add_hint(
                "资源搜索模式：在左侧描述你需要的资源（角色/物件/场景/BGM/特效），\n"
                "AI 会并行派出多个搜索子 Agent 同时查询，快速返回带证据的资源清单。"
            )
        else:
            self.chat.add_hint(
                "选择模式（修改关卡 / 新建关卡 / 新建剧情），在左侧上传文件并填写描述，然后点开始。\n"
                "任务启动后，这里会显示 AI 的实时工作进展。"
            )

    def _on_mode_change(self, mode: str):
        self._save_session_state()
        self.current_mode = mode
        self.sidebar.set_mode(mode)
        self._restore_session_state()

    def _save_session_state(self):
        sess = self._current_session()
        # 如果 worker 正在运行，从 worker 同步最新 messages（worker 在 in-place append）
        worker = sess.get("worker")
        if worker and worker.isRunning():
            sess["messages"] = list(worker.messages)
        else:
            sess["messages"] = list(self.messages)
        sess["workspace"] = self.workspace
        sess["current_skill"] = self.current_skill
        sess["uploaded_files"] = list(self.uploaded_files)
        sess["task_logger"] = self.task_logger
        # 保存侧边栏输入状态
        sess["sidebar_state"] = self.sidebar.get_state()
        # 保存状态栏快照（工具历史 + 思考行）
        sess["status_bar_state"] = self.chat.status_snapshot()

    def _restore_session_state(self):
        MAX_DISPLAY = 30
        sess = self._current_session()
        self.messages = list(sess["messages"])
        self.workspace = sess["workspace"]
        self.current_skill = sess["current_skill"]
        self.uploaded_files = list(sess["uploaded_files"])
        self.task_logger = sess["task_logger"]
        self.current_ai_message = None
        self.review_message = None
        self._last_tool_chip = None

        self.chat.clear_messages()
        self._refresh_session_bar()
        display = sess["display"][-MAX_DISPLAY:]
        if display:
            if len(sess["display"]) > MAX_DISPLAY:
                self.chat.add_hint(f"（已显示最近 {MAX_DISPLAY} 条记录）")
            for role, text in display:
                msg = self.chat.add_message(role)
                msg.set_text(text)

        status = sess["status"]
        is_active = status in ("running", "reviewing")

        # 如果该会话正在运行，把已缓冲的文本回放到 UI
        if is_active and sess["ai_buf"]:
            self.current_ai_message = self.chat.add_message("assistant")
            self.current_ai_message.set_active(True)
            buffered = "".join(sess["ai_buf"])
            self.current_ai_message.append_thinking(buffered)

        if is_active and status == "reviewing" and sess["review_buf"]:
            self.review_message = self.chat.add_message("reviewer")
            self.review_message.set_active(True)
            buffered = "".join(sess["review_buf"])
            self.review_message.append_thinking(buffered)

        self.chat.update_status(state=status)
        # 恢复状态栏快照（工具历史 + 思考行）
        status_bar_snap = sess.get("status_bar_state", {})
        if status_bar_snap:
            self.chat.restore_status_snapshot(status_bar_snap)
        else:
            self.chat._status_bar.reset_for_new_task()

        self.chat.set_busy(is_active)
        if is_active:
            self.sidebar.set_enabled_inputs(False)
        else:
            self.sidebar.set_enabled_inputs(True)

        # 恢复/清空侧边栏输入
        sidebar_state = sess.get("sidebar_state", {})
        if sidebar_state:
            self.sidebar.restore_state(sidebar_state)
        else:
            self.sidebar.clear_inputs()

        if not display and not is_active:
            self._show_welcome()

    def _on_session_switch(self, idx: int):
        ms = self.mode_state[self.current_mode]
        if idx == ms["current_session"]:
            return
        self._save_session_state()
        ms["current_session"] = idx
        self._restore_session_state()

    def _on_session_add(self):
        self._save_session_state()
        ms = self.mode_state[self.current_mode]
        if len(ms["sessions"]) >= MAX_SESSIONS:
            # 淘汰最早的已完成/空闲会话
            idle_indices = [
                i for i, s in enumerate(ms["sessions"])
                if s["status"] in ("idle", "done", "error", "stopped")
                and i != ms["current_session"]
            ]
            if idle_indices:
                ms["sessions"].pop(idle_indices[0])
                if ms["current_session"] > idle_indices[0]:
                    ms["current_session"] -= 1
            else:
                QMessageBox.information(self, "提示", f"最多支持 {MAX_SESSIONS} 个并行会话")
                return
        n = len(ms["sessions"]) + 1
        ms["sessions"].append(_new_session(f"会话 {n}"))
        ms["current_session"] = len(ms["sessions"]) - 1
        self._restore_session_state()

    def _clear_current_chat(self):
        sess = self._current_session()
        if sess["status"] in ("running", "reviewing"):
            QMessageBox.warning(self, "提示", "当前会话任务进行中，请等待完成或停止后再清空")
            return
        sess["display"].clear()
        sess["messages"].clear()
        sess["workspace"] = None
        sess["current_skill"] = None
        sess["uploaded_files"] = []
        sess["task_logger"] = None
        sess["ai_buf"].clear()
        sess["final_buf"].clear()
        sess["review_buf"].clear()
        sess["status"] = "idle"
        self.messages.clear()
        self.workspace = None
        self.current_skill = None
        self.uploaded_files = []
        self.task_logger = None
        self.current_ai_message = None
        self.review_message = None
        self.chat.clear_messages()
        self.chat._status_bar.reset_for_new_task()
        self.chat.update_status(state="idle")
        self.chat.set_busy(False)
        self.sidebar.set_enabled_inputs(True)
        self._refresh_session_bar()
        self._show_welcome()

    def _on_start_task(self, payload: dict):
        if self._current_session()["status"] in ("running", "reviewing"):
            QMessageBox.warning(self, "提示", "当前会话任务进行中")
            return

        if payload["mode"] == "free_chat":
            self._init_free_chat_workspace()
            return

        if not payload.get("description"):
            QMessageBox.warning(self, "提示", "请填写描述")
            return

        if payload["mode"] == "modify":
            if not payload.get("archive"):
                QMessageBox.warning(self, "提示", "请上传关卡包")
                return

        if payload["mode"] == "resource_search":
            self._on_start_resource_search(payload)
            return

        self._current_session()["name"] = self._make_tab_label(payload.get("description", ""))

        ws = workspace_dir() / f"task_{uuid.uuid4().hex[:8]}"
        ws.mkdir(parents=True, exist_ok=True)
        self.workspace = ws
        self.task_logger = setup_task_logging(ws)
        self._log.info("新建任务 mode=%s workspace=%s", payload["mode"], ws)

        skills = skills_for_mode(payload["mode"])
        skill = skills[0] if skills else None
        self.current_skill = skill

        uploaded = []
        if payload.get("archive"):
            uploaded.append(payload["archive"])
        for key in ("old_files", "new_files", "refs"):
            for p in payload.get(key, []) or []:
                uploaded.append(p)
        self.uploaded_files = list(dict.fromkeys(uploaded))

        initial_msg = self._compose_initial_message(payload)
        self.messages = [{"role": "user", "content": initial_msg}]

        user_msg = self.chat.add_message("user")
        user_msg.set_text(self._pretty_user_summary(payload))
        self._append_display("user", self._pretty_user_summary(payload))

        self.current_ai_message = self.chat.add_message("assistant")
        self.chat._status_bar.reset_for_new_task()
        self.current_ai_message.set_active(True)

        system_prompt = build_system_prompt(
            skill_content=skill.content if skill else "（当前无匹配技能，按通用流程执行）",
            skill_path=skill.path if skill else None,
            mode_label=MODES[payload["mode"]]["label"],
            workspace=ws,
            uploaded_files=self.uploaded_files,
        )

        self._start_agent(system_prompt)

    def _on_start_resource_search(self, payload: dict):
        """启动资源搜索模式：纯文字描述，无需关卡包，并行子 Agent 搜索。"""
        self._current_session()["name"] = self._make_tab_label(payload.get("description", ""))

        ws = workspace_dir() / f"search_{uuid.uuid4().hex[:8]}"
        ws.mkdir(parents=True, exist_ok=True)
        self.workspace = ws
        self.task_logger = setup_task_logging(ws)
        self._log.info("新建资源搜索任务 workspace=%s", ws)

        skills = skills_for_mode("resource_search")
        skill = skills[0] if skills else None
        self.current_skill = skill
        self.uploaded_files = []

        initial_msg = self._compose_initial_message(payload)
        self.messages = [{"role": "user", "content": initial_msg}]

        user_msg = self.chat.add_message("user")
        user_msg.set_text(self._pretty_user_summary(payload))
        self._append_display("user", self._pretty_user_summary(payload))

        self.current_ai_message = self.chat.add_message("assistant")
        self.chat._status_bar.reset_for_new_task()
        self.current_ai_message.set_active(True)

        system_prompt = build_system_prompt(
            skill_content=skill.content if skill else "你是资源搜索协调员，解析需求并并行派发子 Agent 查询资源。",
            skill_path=skill.path if skill else None,
            mode_label=MODES["resource_search"]["label"],
            workspace=ws,
            uploaded_files=[],
        )
        self._start_agent(system_prompt)

    def _start_task_from_chat(self, text: str, images: list):
        """resource_search / create_level / create_story 从输入框直接发起任务。"""
        mode = self.current_mode
        ws_prefix = "search" if mode == "resource_search" else "task"
        ws = workspace_dir() / f"{ws_prefix}_{uuid.uuid4().hex[:8]}"
        ws.mkdir(parents=True, exist_ok=True)
        self.workspace = ws
        self.task_logger = setup_task_logging(ws)
        self._log.info("从输入框发起任务 mode=%s workspace=%s", mode, ws)

        skills = skills_for_mode(mode)
        skill = skills[0] if skills else None
        self.current_skill = skill
        self.uploaded_files = []

        self._current_session()["name"] = self._make_tab_label(text or "新任务")

        # 构建初始消息（直接用用户输入，不经过侧边栏表单）
        if images:
            content: list = []
            for img_path in images:
                p = Path(img_path)
                suffix = p.suffix.lower()
                media_type = "image/jpeg" if suffix in (".jpg", ".jpeg") else (
                    "image/webp" if suffix == ".webp" else
                    "image/gif" if suffix == ".gif" else "image/png"
                )
                with open(img_path, "rb") as f:
                    img_b64 = base64.standard_b64encode(f.read()).decode()
                content.append({
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": img_b64},
                })
            if text:
                content.append({"type": "text", "text": text})
            self.messages = [{"role": "user", "content": content}]
        else:
            self.messages = [{"role": "user", "content": text}]

        user_msg = self.chat.add_message("user")
        user_msg.set_text(text)
        self._append_display("user", text)

        self.current_ai_message = self.chat.add_message("assistant")
        self.chat._status_bar.reset_for_new_task()
        self.current_ai_message.set_active(True)

        default_skill_content = {
            "resource_search": "你是资源搜索协调员，解析需求并并行派发子 Agent 查询资源。",
            "create_level":    "（当前无匹配技能，按通用流程执行）",
            "create_story":    "（当前无匹配技能，按通用流程执行）",
        }.get(mode, "")

        system_prompt = build_system_prompt(
            skill_content=skill.content if skill else default_skill_content,
            skill_path=skill.path if skill else None,
            mode_label=MODES[mode]["label"],
            workspace=ws,
            uploaded_files=[],
        )
        self._start_agent(system_prompt)

    def _init_free_chat_workspace(self):
        ws = workspace_dir() / f"chat_{uuid.uuid4().hex[:8]}"
        ws.mkdir(parents=True, exist_ok=True)
        self.workspace = ws
        self.task_logger = setup_task_logging(ws)
        self.uploaded_files = []
        self.current_skill = None
        self.messages = []
        self._log.info("自由对话工作空间已就绪 workspace=%s", ws)
        self.chat.clear_messages()
        self.chat._status_bar.reset_for_new_task()
        self.chat.add_hint("对话已就绪，直接输入消息开始吧")
        self.sidebar.set_enabled_inputs(False)

    def _compose_initial_message(self, payload: dict) -> str:
        from ..config import output_dir
        lines = []
        if payload["mode"] == "modify":
            lines.append("【任务】修改关卡")
            lines.append(f"【关卡包绝对路径】{payload['archive']}")
            if payload.get("old_files"):
                lines.append("【需要替换的原始文件】")
                for p in payload["old_files"]:
                    lines.append(f"  - {p}")
            if payload.get("new_files"):
                lines.append("【修改到的新文件】")
                for p in payload["new_files"]:
                    lines.append(f"  - {p}")
            lines.append("【描述】")
            lines.append(payload["description"])
            lines.append("")
            lines.append(
                "请按技能规则开始工作。"
                "改造员子 agent 完成后会直接用 pack_zip_clean 将包写入 "
                f"`{output_dir()}/modify/` 目录，**主 agent 无需再调用 create_archive**，"
                "否则会对已含 zip 的目录二次打包产生 zip 嵌套。"
            )
        elif payload["mode"] == "resource_search":
            lines.append("【任务】资源搜索")
            lines.append("【搜索需求】")
            lines.append(payload["description"])
            lines.append("")
            lines.append(
                "请按技能规范，将上述需求拆分为子任务（角色推荐/物件选取/动画校验/场景BGM特效），"
                "然后一次性调用 run_subagents_parallel 并行派出所有搜索子 Agent，"
                "等所有子 Agent 返回后，汇总结果输出完整资源清单。\n"
                "⚠️ 本任务无需打包，禁止调用 create_archive，结果直接输出在消息中即可。"
            )
        else:
            lines.append(f"【任务】{MODES[payload['mode']]['label']}")
            if payload.get("refs"):
                lines.append("【参考文件】")
                for p in payload["refs"]:
                    lines.append(f"  - {p}")
            lines.append("【描述】")
            lines.append(payload["description"])
            lines.append("")
            if payload["mode"] in ("create_level", "create_story"):
                lines.append(
                    "请按技能规则开始工作。"
                    "创建员子 agent 完成后会直接用 pack_zip_clean 将包写入 "
                    f"`{output_dir()}/new/` 目录，**主 agent 无需再调用 create_archive**，"
                    "否则会对已含 zip 的目录二次打包产生 zip 嵌套。"
                )
            else:
                lines.append(
                    f"请按技能规则开始工作。完成后使用 create_archive 将产出目录打包，"
                    f"output_name 填写 **绝对路径** 保存到产出目录：`{output_dir()}/文件名.zip`"
                )
        msg = "\n".join(lines)
        self._current_session()["task_description"] = msg   # 供审查 Agent 使用
        return msg

    def _pretty_user_summary(self, payload: dict) -> str:
        parts = [f"【{MODES[payload['mode']]['label']}】"]
        if payload["mode"] == "modify":
            if payload.get("archive"):
                parts.append(f"关卡包: {Path(payload['archive']).name}")
            parts.append(f"替换 {len(payload.get('old_files', []))} 项 → 新 {len(payload.get('new_files', []))} 项")
        elif payload["mode"] == "resource_search":
            pass  # 只展示描述
        else:
            parts.append(f"{len(payload.get('refs', []))} 个参考文件")
        parts.append("")
        parts.append(payload["description"])
        return "\n".join(parts)

    def _start_agent(self, system_prompt: str):
        import time
        sess = self._current_session()
        mode = self.current_mode
        ms = self.mode_state[mode]
        sess_idx = ms["current_session"]

        sess["task_start_time"] = time.time()
        sess["ai_buf"].clear()
        sess["final_buf"].clear()
        sess["status"] = "running"

        worker = AgentWorker(
            messages=self.messages,
            system_prompt=system_prompt,
            workspace=self.workspace,
            skill_dir=self.current_skill.path if self.current_skill else None,
            uploaded_files=self.uploaded_files,
            model=DEFAULT_MODEL,
            task_logger=self.task_logger,
            mode=mode,
        )
        sess["worker"] = worker

        # ── 信号路由：捕获 mode + sess_idx，用于跨 session 分发 ──
        worker.text_chunk.connect(
            lambda chunk, m=mode, i=sess_idx: self._route_text_chunk(m, i, chunk))
        worker.tool_call_start.connect(
            lambda name, params, m=mode, i=sess_idx: self._route_tool_start(m, i, name, params))
        worker.tool_call_end.connect(
            lambda name, result, m=mode, i=sess_idx: self._route_tool_end(m, i, name, result))
        worker.iteration_update.connect(
            lambda n, m=mode, i=sess_idx: self._route_iteration(m, i, n))
        worker.error.connect(
            lambda msg, m=mode, i=sess_idx: self._route_error(m, i, msg))
        worker.finished_turn.connect(
            lambda m=mode, i=sess_idx: self._route_done(m, i))

        self.chat.set_busy(True)
        self.chat.update_status(state="running")
        self.sidebar.set_enabled_inputs(False)
        self._refresh_session_bar()
        worker.start()

    # ── 路由判断辅助 ───────────────────────────────────────────────────
    def _is_active_session(self, mode: str, sess_idx: int) -> bool:
        return (self.current_mode == mode and
                self.mode_state[mode]["current_session"] == sess_idx)

    # ── 路由信号处理方法 ────────────────────────────────────────────────
    def _update_bg_status_bar(self, sess: dict, tool: str | None = None,
                              thinking: str | None = None, tool_done: str | None = None):
        """为后台 session 维护其 status_bar_state，用于切回时恢复以及后台活动条显示。"""
        snap = sess.setdefault("status_bar_state", {"tool_history": [], "think_lines": []})
        if tool is not None:
            snap.setdefault("tool_history", []).append((tool, "⋯"))
        if tool_done is not None:
            th = snap.get("tool_history", [])
            for i in range(len(th) - 1, -1, -1):
                if th[i][0] == tool_done[0]:
                    th[i] = tool_done
                    break
            else:
                th.append(tool_done)
        if thinking is not None:
            lines = snap.setdefault("think_lines", [])
            combined = "".join(lines) + thinking
            snap["think_lines"] = combined.split("\n")[-4:]

    def _route_text_chunk(self, mode: str, sess_idx: int, chunk: str):
        sess = self.mode_state[mode]["sessions"][sess_idx]
        sess["ai_buf"].append(chunk)
        sess["final_buf"].append(chunk)
        if self._is_active_session(mode, sess_idx):
            if self.current_ai_message is None:
                self.current_ai_message = self.chat.add_message("assistant")
                self.current_ai_message.set_active(True)
            self.current_ai_message.append_thinking(chunk)
            self.chat._status_bar.add_thinking(chunk)
            self.chat._scroll_to_bottom()
        else:
            self._update_bg_status_bar(sess, thinking=chunk)
            self._refresh_session_bar()   # 刷新后台活动条

    def _route_iteration(self, mode: str, sess_idx: int, n: int):
        if self._is_active_session(mode, sess_idx):
            self._current_iter = n
            self.chat.update_status(iteration=n, state="running")

    def _route_tool_start(self, mode: str, sess_idx: int, name: str, params: dict):
        sess = self.mode_state[mode]["sessions"][sess_idx]
        sess["final_buf"].clear()
        if self._is_active_session(mode, sess_idx):
            if self.current_ai_message is None:
                self.current_ai_message = self.chat.add_message("assistant")
                self.current_ai_message.set_active(True)
            chip = self.current_ai_message.add_tool_chip(name, "running")
            self._last_tool_chip = chip
            self.chat.update_status(iteration=self._current_iter, tool=name, state="running")
            self.chat._status_bar.add_tool_event(name, "running")
            self.chat._scroll_to_bottom()
        else:
            self._update_bg_status_bar(sess, tool=name)
            self._refresh_session_bar()

    def _route_tool_end(self, mode: str, sess_idx: int, name: str, result: dict):
        sess = self.mode_state[mode]["sessions"][sess_idx]
        ok = (result.get("ok") or result.get("valid") or result.get("success")) \
             and not result.get("error")
        # 追踪本 session 产出的压缩包，供审查官精确定位（避免并行任务互相干扰）
        if ok and name == "create_archive":
            archive = result.get("archive") or result.get("path") or result.get("output")
            if archive and str(archive) not in sess["created_archives"]:
                sess["created_archives"].append(str(archive))
        if self._is_active_session(mode, sess_idx):
            if self._last_tool_chip:
                chip = self._last_tool_chip
                chip.setText(f"[🔧 {name}] {'✓' if ok else '✗'}")
                chip.setProperty("status", "done" if ok else "error")
                chip.style().unpolish(chip)
                chip.style().polish(chip)
                self._last_tool_chip = None
            self.chat.update_status(iteration=self._current_iter, tool="", state="running")
            self.chat._status_bar.add_tool_event(name, "✓" if ok else "✗")
        else:
            self._update_bg_status_bar(sess, tool_done=(name, "✓" if ok else "✗"))
            self._refresh_session_bar()

    def _route_error(self, mode: str, sess_idx: int, msg: str):
        self._log.error("Agent 报错 [mode=%s sess=%d]: %s", mode, sess_idx, msg)
        sess = self.mode_state[mode]["sessions"][sess_idx]
        sess["status"] = "error"
        if self._is_active_session(mode, sess_idx):
            self.chat.update_status(state="error")
            ai = self.current_ai_message or self.chat.add_message("assistant")
            if self.current_ai_message:
                self.current_ai_message.seal_thinking()
                self.current_ai_message.set_active(False)
            ai.set_text(f"[错误] {msg}")
            self.chat.set_busy(False)
            self.sidebar.set_enabled_inputs(True)
            self.current_ai_message = None
        self._refresh_session_bar()

    def _route_done(self, mode: str, sess_idx: int):
        sess = self.mode_state[mode]["sessions"][sess_idx]
        final_text = "".join(sess["final_buf"]).strip()
        all_text = "".join(sess["ai_buf"]).strip()
        sess["final_buf"].clear()
        sess["status"] = "done"
        # 把 worker 完整的 messages 同步回 session，供后续对话使用
        worker = sess.get("worker")
        if worker:
            sess["messages"] = list(worker.messages)
        # 如果当前活动 session 也是本 session，同步到 self.messages
        if self._is_active_session(mode, sess_idx):
            self.messages = list(sess["messages"])

        # 把文本追加到 display buffer
        if all_text:
            MAX = 30
            disp = sess["display"]
            disp.append(("assistant", all_text))
            if len(disp) > MAX:
                del disp[:len(disp) - MAX]

        # 优先使用精确追踪的产出路径（避免并行任务互相干扰）
        archive_paths: list[str] = list(sess.get("created_archives", []))
        if not archive_paths:
            # 兜底：扫 skills/output/ 中本次任务新增的文件（仅单任务场景）
            t0 = sess.get("task_start_time", 0)
            if t0 > 0:
                from ..config import output_dir
                try:
                    for f in output_dir().rglob("*"):
                        if f.is_file() and f.stat().st_mtime >= t0 - 1:
                            archive_paths.append(str(f))
                except Exception:
                    pass

        # ReviewWorker 已禁用：level-modify 等技能内部已有子 agent 审查员，无需二次审查
        will_review = False

        if self._is_active_session(mode, sess_idx):
            if self.current_ai_message:
                self.current_ai_message.seal_thinking()
                self.current_ai_message.set_active(False)
                if final_text and mode == "free_chat":
                    self.current_ai_message.set_text(final_text)
            if archive_paths:
                ai = self.current_ai_message or self.chat.add_message("assistant")
                for fp in archive_paths:
                    ai.add_download_card(fp, Path(fp).name)
            self.chat.set_busy(False)
            self.chat.update_status(state="done")
            self.sidebar.set_enabled_inputs(True)
            self.current_ai_message = None

        self._refresh_session_bar()
        self._save_history()   # 任务完成后持久化


    def _on_chat_send(self, text: str, images: list | None = None):
        images = images or []
        sess = self._current_session()
        if sess["status"] in ("running", "reviewing"):
            QMessageBox.information(self, "提示", "请等待当前会话完成，或点停止按钮中断")
            return

        self._log.info("_on_chat_send  text_len=%d  images=%d", len(text), len(images))

        if not self.workspace and self.current_mode == "free_chat":
            self._init_free_chat_workspace()

        if not self.workspace:
            # resource_search / create_level / create_story：允许从输入框直接发起任务
            if self.current_mode in ("resource_search", "create_level", "create_story"):
                self._start_task_from_chat(text, images)
                return
            QMessageBox.information(self, "提示", "请先在左侧开始一个任务")
            return

        if sess["name"].startswith("会话"):
            sess["name"] = self._make_tab_label(text or "图片")

        user_msg = self.chat.add_message("user")
        user_msg.set_text(text)

        # 构建消息内容（纯文字 or 多模态）
        if images:
            content: list = []
            for img_path in images:
                p = Path(img_path)
                suffix = p.suffix.lower()
                media_type = "image/jpeg" if suffix in (".jpg", ".jpeg") else (
                    "image/webp" if suffix == ".webp" else
                    "image/gif" if suffix == ".gif" else "image/png"
                )
                with open(img_path, "rb") as f:
                    img_b64 = base64.standard_b64encode(f.read()).decode()
                content.append({
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": img_b64},
                })
            if text:
                content.append({"type": "text", "text": text})
            self.messages.append({"role": "user", "content": content})
        else:
            self.messages.append({"role": "user", "content": text})

        self._append_display("user", text)
        self.current_ai_message = self.chat.add_message("assistant")
        self.chat._status_bar.reset_for_new_task()

        skill = self.current_skill
        if skill is None:
            skills = skills_for_mode(self.current_mode)
            skill = skills[0] if skills else None
            self.current_skill = skill

        if self.current_mode == "free_chat":
            system_prompt = build_system_prompt(
                skill_content="你是一个全能AI助手，可以自由对话，同时拥有全部工具能力（搜索、读写文件、运行脚本等）。",
                skill_path=None,
                mode_label="自由对话",
                workspace=self.workspace,
                uploaded_files=self.uploaded_files,
            )
        else:
            system_prompt = build_system_prompt(
                skill_content=skill.content if skill else "",
                skill_path=skill.path if skill else None,
                mode_label=MODES[self.current_mode]["label"],
                workspace=self.workspace,
                uploaded_files=self.uploaded_files,
            )
        self._start_agent(system_prompt)

    def _append_display(self, role: str, text: str):
        MAX = 30
        sess = self._current_session()
        disp = sess["display"]
        disp.append((role, text))
        if len(disp) > MAX:
            del disp[: len(disp) - MAX]

    def _stop_agent(self):
        sess = self._current_session()
        w = sess.get("worker")
        if w and w.isRunning():
            w.request_stop()
            sess["status"] = "stopped"
            self.chat.update_status(state="stopped")
            self.chat.set_busy(False)       # 立即解锁输入，无需等 finished_turn
            self.sidebar.set_enabled_inputs(True)
        rw = sess.get("review_worker")
        if rw and rw.isRunning():
            rw.request_stop()
        self._refresh_session_bar()

    def _start_review(self, mode: str, sess_idx: int, archive_paths: list[str]):
        """启动独立审查 Agent。"""
        sess = self.mode_state[mode]["sessions"][sess_idx]
        if sess.get("review_worker") and sess["review_worker"].isRunning():
            return
        if not sess["workspace"]:
            return

        task_desc = sess.get("task_description", "")
        skill = sess.get("current_skill")
        skill_content = skill.content if skill else ""
        skill_dir = skill.path if skill else None
        ws = sess["workspace"]

        sess["review_buf"].clear()
        sess["status"] = "reviewing"

        review_worker = ReviewWorker(
            task_description=task_desc,
            workspace=ws,
            output_files=archive_paths,
            skill_content=skill_content,
            skill_dir=skill_dir,
            task_logger=sess.get("task_logger"),
        )
        sess["review_worker"] = review_worker

        review_worker.text_chunk.connect(
            lambda chunk, m=mode, i=sess_idx: self._route_review_chunk(m, i, chunk))
        review_worker.tool_call_start.connect(
            lambda name, params, m=mode, i=sess_idx: self._route_review_tool_start(m, i, name))
        review_worker.tool_call_end.connect(
            lambda name, result, m=mode, i=sess_idx: self._route_review_tool_end(m, i, name, result))
        review_worker.error.connect(
            lambda msg, m=mode, i=sess_idx: self._route_review_error(m, i, msg))
        review_worker.finished_turn.connect(
            lambda m=mode, i=sess_idx: self._route_review_done(m, i))

        if self._is_active_session(mode, sess_idx):
            self.review_message = self.chat.add_message("reviewer")
            self.review_message.set_active(True)
            self.chat.update_status(state="reviewing")
            self.chat.set_busy(True)
            self.sidebar.set_enabled_inputs(False)

        self._refresh_session_bar()
        review_worker.start()

    def _route_review_chunk(self, mode: str, sess_idx: int, chunk: str):
        sess = self.mode_state[mode]["sessions"][sess_idx]
        sess["review_buf"].append(chunk)
        if self._is_active_session(mode, sess_idx):
            if self.review_message is None:
                self.review_message = self.chat.add_message("reviewer")
                self.review_message.set_active(True)
            self.review_message.append_thinking(chunk)
            self.chat._scroll_to_bottom()

    def _route_review_tool_start(self, mode: str, sess_idx: int, name: str):
        if self._is_active_session(mode, sess_idx) and self.review_message:
            self.review_message.add_tool_chip(name, "running")

    def _route_review_tool_end(self, mode: str, sess_idx: int, name: str, result: dict):
        ok = (result.get("ok") or result.get("valid") or result.get("success")) \
             and not result.get("error")
        if self._is_active_session(mode, sess_idx) and self.review_message:
            last_chip = self.review_message._last_chip() \
                if hasattr(self.review_message, "_last_chip") else None
            if last_chip:
                last_chip.setText(f"[🔍 {name}] {'✓' if ok else '✗'}")
                last_chip.setProperty("status", "done" if ok else "error")
                last_chip.style().unpolish(last_chip)
                last_chip.style().polish(last_chip)

    def _route_review_error(self, mode: str, sess_idx: int, msg: str):
        self._log.error("[审查] 报错 [mode=%s sess=%d]: %s", mode, sess_idx, msg)
        sess = self.mode_state[mode]["sessions"][sess_idx]
        sess["status"] = "error"
        if self._is_active_session(mode, sess_idx) and self.review_message:
            self.review_message.seal_thinking()
            self.review_message.set_active(False)
            self.review_message.set_text(f"[审查错误] {msg}")
            self.chat.update_status(state="done")
            self.chat.set_busy(False)
            self.sidebar.set_enabled_inputs(True)
            self.review_message = None
        self._refresh_session_bar()

    def _route_review_done(self, mode: str, sess_idx: int):
        sess = self.mode_state[mode]["sessions"][sess_idx]
        final = "".join(sess["review_buf"]).strip()
        sess["review_buf"].clear()

        if final:
            MAX = 30
            disp = sess["display"]
            disp.append(("reviewer", final))
            if len(disp) > MAX:
                del disp[:len(disp) - MAX]

        if self._is_active_session(mode, sess_idx):
            if self.review_message:
                self.review_message.seal_thinking()
                self.review_message.set_active(False)
                if final:
                    self.review_message.set_text(final)
            self.review_message = None

        self._log.info("[审查] 完成 [mode=%s sess=%d]", mode, sess_idx)
        self._save_history()   # 审查完成后持久化

        # 如果审查发现问题，自动把报告注入主 Agent 继续修复（最多重试 1 次）
        review_failed = final and ("❌" in final or "FAIL" in final)
        retry_count = sess.get("review_attempt", 0)
        workspace = sess.get("workspace")
        if review_failed and retry_count < 2 and workspace and sess.get("messages"):
            sess["review_attempt"] = retry_count + 1
            retry_msg = (
                "[系统审查报告]\n\n"
                + final
                + "\n\n请根据上述审查发现的问题进行修复，修复后重新打包，确保通过全部检查点。"
            )
            self._log.info("[审查] 发现问题，自动触发修复重试 attempt=%d", retry_count + 1)
            self._continue_agent_with_message(mode, sess_idx, retry_msg)
        else:
            sess["status"] = "done"
            # 审查通过（或无需重试）→ 此时才显示下载卡
            archive_paths: list[str] = list(sess.get("created_archives", []))
            if self._is_active_session(mode, sess_idx):
                if archive_paths:
                    review_msg = self.review_message or self.chat.add_message("assistant")
                    for fp in archive_paths:
                        review_msg.add_download_card(fp, Path(fp).name)
                self.chat.update_status(state="done")
                self.chat.set_busy(False)
                self.sidebar.set_enabled_inputs(True)

        self._refresh_session_bar()

    def _continue_agent_with_message(self, mode: str, sess_idx: int, inject_text: str):
        """审查失败后把审查报告注入 messages，重启主 Agent 继续修复。"""
        import time
        sess = self.mode_state[mode]["sessions"][sess_idx]
        workspace = sess["workspace"]
        skill = sess.get("current_skill")
        uploaded_files = sess.get("uploaded_files", [])

        sess["messages"].append({"role": "user", "content": inject_text})
        sess["ai_buf"].clear()
        sess["final_buf"].clear()
        sess["created_archives"].clear()
        sess["task_start_time"] = time.time()
        sess["status"] = "running"

        MAX = 30
        disp = sess["display"]
        disp.append(("user", inject_text))
        if len(disp) > MAX:
            del disp[:len(disp) - MAX]

        if mode == "free_chat":
            system_prompt = build_system_prompt(
                skill_content="你是一个全能AI助手，可以自由对话，同时拥有全部工具能力。",
                skill_path=None, mode_label="自由对话",
                workspace=workspace, uploaded_files=uploaded_files,
            )
        elif mode == "resource_search":
            system_prompt = build_system_prompt(
                skill_content=skill.content if skill else "你是资源搜索协调员，解析需求并并行派发子 Agent 查询资源。",
                skill_path=skill.path if skill else None,
                mode_label=MODES["resource_search"]["label"],
                workspace=workspace, uploaded_files=uploaded_files,
            )
        else:
            system_prompt = build_system_prompt(
                skill_content=skill.content if skill else "",
                skill_path=skill.path if skill else None,
                mode_label=MODES[mode]["label"],
                workspace=workspace,
                uploaded_files=uploaded_files,
            )

        worker = AgentWorker(
            messages=sess["messages"],
            system_prompt=system_prompt,
            workspace=workspace,
            skill_dir=skill.path if skill else None,
            uploaded_files=uploaded_files,
            model=DEFAULT_MODEL,
            task_logger=sess.get("task_logger"),
            mode=mode,
        )
        sess["worker"] = worker

        worker.text_chunk.connect(
            lambda chunk, m=mode, i=sess_idx: self._route_text_chunk(m, i, chunk))
        worker.tool_call_start.connect(
            lambda name, params, m=mode, i=sess_idx: self._route_tool_start(m, i, name, params))
        worker.tool_call_end.connect(
            lambda name, result, m=mode, i=sess_idx: self._route_tool_end(m, i, name, result))
        worker.iteration_update.connect(
            lambda n, m=mode, i=sess_idx: self._route_iteration(m, i, n))
        worker.error.connect(
            lambda msg, m=mode, i=sess_idx: self._route_error(m, i, msg))
        worker.finished_turn.connect(
            lambda m=mode, i=sess_idx: self._route_done(m, i))

        if self._is_active_session(mode, sess_idx):
            user_msg_block = self.chat.add_message("user")
            user_msg_block.set_text(inject_text)
            self.current_ai_message = self.chat.add_message("assistant")
            self.current_ai_message.set_active(True)
            self.chat._status_bar.reset_for_new_task()
            self.chat.set_busy(True)
            self.chat.update_status(state="running")
            self.sidebar.set_enabled_inputs(False)
            self.messages = sess["messages"]

        self._refresh_session_bar()
        worker.start()


    # ── 历史记录持久化 ─────────────────────────────────────────────────

    def _history_file(self) -> Path:
        from ..config import base_dir
        return base_dir() / "session_history.json"

    def _save_history(self):
        """将所有模式中有内容的会话序列化到 session_history.json。"""
        import json, datetime
        data: dict = {
            "version": 1,
            "saved_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "modes": {},
        }
        for mode, ms in self.mode_state.items():
            sessions_data = []
            for sess in ms["sessions"]:
                # 跳过完全空白且空闲的会话
                if not sess.get("display") and sess.get("status", "idle") == "idle":
                    continue
                sessions_data.append({
                    "name": sess.get("name", ""),
                    "display": [[r, t] for r, t in sess.get("display", [])],
                    "sidebar_state": sess.get("sidebar_state", {}),
                    "status": sess.get("status", "idle"),
                    "task_description": sess.get("task_description", ""),
                    "created_archives": sess.get("created_archives", []),
                    "workspace": str(sess["workspace"]) if sess.get("workspace") else None,
                })
            if sessions_data:
                data["modes"][mode] = {
                    "sessions": sessions_data,
                    "current_session": min(
                        ms["current_session"], len(sessions_data) - 1
                    ),
                }
        try:
            self._history_file().write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            self._log.info("历史记录已保存（%d 个模式）", len(data["modes"]))
        except Exception as e:
            self._log.warning("保存历史失败: %s", e)

    def _load_history(self):
        """从 session_history.json 恢复上次会话状态。"""
        import json
        path = self._history_file()
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            self._log.warning("加载历史失败: %s", e)
            return
        if data.get("version") != 1:
            return
        loaded = 0
        for mode, ms_data in data.get("modes", {}).items():
            if mode not in self.mode_state:
                continue
            sessions = []
            for s in ms_data.get("sessions", []):
                sess = _new_session(s.get("name", "会话"))
                sess["display"] = [[r, t] for r, t in s.get("display", [])]
                sess["sidebar_state"] = s.get("sidebar_state", {})
                status = s.get("status", "idle")
                # 运行中/审查中的状态在加载时视为已完成
                sess["status"] = "done" if status in ("running", "reviewing") else status
                sess["task_description"] = s.get("task_description", "")
                sess["created_archives"] = s.get("created_archives", [])
                ws = s.get("workspace")
                sess["workspace"] = Path(ws) if ws else None
                sessions.append(sess)
            if sessions:
                cur = min(ms_data.get("current_session", 0), len(sessions) - 1)
                self.mode_state[mode]["sessions"] = sessions
                self.mode_state[mode]["current_session"] = cur
                loaded += len(sessions)
        self._log.info("历史记录已加载（共 %d 条会话）", loaded)

    def _clear_all_history(self):
        """清空所有历史记录：删除文件并重置 mode_state。"""
        reply = QMessageBox.question(
            self, "清空历史",
            "确定要清空所有历史记录吗？\n此操作不可撤销，当前所有会话内容都会被清除。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        # 停止所有运行中的 worker
        for ms in self.mode_state.values():
            for sess in ms["sessions"]:
                w = sess.get("worker")
                if w and w.isRunning():
                    w.request_stop()
                    w.wait(1000)
                rw = sess.get("review_worker")
                if rw and rw.isRunning():
                    rw.request_stop()
                    rw.wait(1000)
        # 重置 mode_state
        self.mode_state = {
            mode: {"sessions": [_new_session("会话 1")], "current_session": 0}
            for mode in MODES
        }
        # 删除历史文件
        try:
            f = self._history_file()
            if f.exists():
                f.unlink()
        except Exception:
            pass
        # 重置 UI
        self.messages = []
        self.workspace = None
        self.current_skill = None
        self.uploaded_files = []
        self.task_logger = None
        self.current_ai_message = None
        self.review_message = None
        self._restore_session_state()
        self._log.info("历史记录已清空")

    # ── 热更新 ───────────────────────────────────────────────────────────

    def _check_for_updates(self):
        self._update_checker = UpdateChecker(
            version_url=UPDATE_VERSION_URL,
            current_version=APP_VERSION,
            proxy_prefix=UPDATE_PROXY_PREFIX,
            parent=self,
        )
        self._update_checker.update_available.connect(self._on_update_available)
        self._update_checker.check_failed.connect(
            lambda err: self._log.debug("更新检查失败（忽略）: %s", err)
        )
        self._update_checker.start()

    def _on_update_available(self, info: dict):
        self._log.info("发现新版本: %s", info.get("version"))
        dlg = UpdateNotifyDialog(info, proxy_prefix=UPDATE_PROXY_PREFIX, parent=self)
        dlg.exec()

    # ── 关闭事件 ────────────────────────────────────────────────────────
    def closeEvent(self, ev):
        self._save_session_state()   # 先把当前 UI 状态同步到 session
        self._save_history()         # 持久化到磁盘
        for ms in self.mode_state.values():
            for sess in ms["sessions"]:
                w = sess.get("worker")
                if w and w.isRunning():
                    w.request_stop()
                    w.wait(2000)
                rw = sess.get("review_worker")
                if rw and rw.isRunning():
                    rw.request_stop()
                    rw.wait(2000)
        super().closeEvent(ev)
