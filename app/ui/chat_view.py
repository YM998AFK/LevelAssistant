"""对话区：消息列表 + 输入框。支持流式追加文本和工具调用气泡。"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QTextEdit, QPushButton, QFrame, QSizePolicy, QToolButton,
    QScrollBar,
)

from .widgets import DownloadCard


class _ThinkingSection(QFrame):
    """可折叠的思考过程区域，默认收起。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 2, 0, 0)
        root.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        self._toggle_btn = QToolButton()
        self._toggle_btn.setText("▸ 思考过程")
        self._toggle_btn.setStyleSheet("""
            QToolButton {
                background: transparent; border: none;
                color: #94A3B8; font-size: 11px; padding: 2px 0;
                font-weight: 500;
            }
            QToolButton:hover { color: #64748B; }
        """)
        self._toggle_btn.setCursor(Qt.PointingHandCursor)
        self._toggle_btn.clicked.connect(self._toggle)
        header.addWidget(self._toggle_btn)
        header.addStretch()
        root.addLayout(header)

        self._content = QLabel()
        self._content.setObjectName("ThinkingText")
        self._content.setWordWrap(True)
        self._content.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._content.setStyleSheet("""
            background: #F8FAFC;
            border-left: 2px solid #E2E8F0;
            color: #94A3B8; font-size: 12px;
            padding: 8px 12px; margin-top: 4px;
            border-radius: 0 6px 6px 0;
        """)
        self._content.setVisible(False)
        root.addWidget(self._content)

        self._expanded = False
        self._text = ""

    def _toggle(self):
        self._expanded = not self._expanded
        self._content.setVisible(self._expanded)
        self._toggle_btn.setText(
            f"▾ 思考过程（{self._line_count()} 行）" if self._expanded
            else f"▸ 思考过程（{self._line_count()} 行）"
        )

    def _line_count(self) -> int:
        return self._text.count("\n") + 1 if self._text else 0

    def append_text(self, chunk: str):
        self._text += chunk
        self._content.setText(self._text)
        count = self._line_count()
        arrow = "▾" if self._expanded else "▸"
        self._toggle_btn.setText(f"{arrow} 思考过程（{count} 行）")

    def seal(self):
        count = self._line_count()
        if count > 0:
            self._toggle_btn.setText(f"▸ 思考过程（{count} 行）")
        else:
            self.setVisible(False)


class MessageBlock(QFrame):
    """一条消息：用户=右对齐气泡，AI=左对齐卡片"""

    def __init__(self, role: str, parent=None):
        super().__init__(parent)
        self.role = role
        self.setObjectName("MessageBlock")
        # 使用 objectName 选择器，避免裸 "background: transparent;" 级联覆盖子元素样式
        self.setStyleSheet("#MessageBlock { background: transparent; }")

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)
        root.setAlignment(Qt.AlignTop)

        if role == "user":
            self._build_user(root)
        elif role == "reviewer":
            self._build_reviewer(root)
        else:
            self._build_ai(root)

        self.text_label: QLabel | None = None
        self._thinking: _ThinkingSection | None = None
        self._chips: list[QLabel] = []

    # ── user layout: spacer + bubble + avatar ──────────────────────
    def _build_user(self, root: QHBoxLayout):
        root.addStretch(1)

        self._bubble = QFrame()
        self._bubble.setObjectName("UserBubble")
        # 直接内联样式，不依赖 app 样式表级联（防止父级 transparent 覆盖）
        self._bubble.setStyleSheet(
            "#UserBubble { background-color: #6366F1; border-radius: 18px;"
            " border-bottom-right-radius: 5px; padding: 10px 14px; }"
        )
        bubble_layout = QVBoxLayout(self._bubble)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.setSpacing(0)
        self.body_layout = bubble_layout
        root.addWidget(self._bubble, 0, Qt.AlignTop)
        root.setStretchFactor(self._bubble, 0)

        avatar = QLabel("我")
        avatar.setObjectName("UserAvatar")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(28, 28)
        root.addWidget(avatar, 0, Qt.AlignTop)

    # ── ai layout: avatar + card ────────────────────────────────────
    def _build_ai(self, root: QHBoxLayout):
        avatar = QLabel("S")
        avatar.setObjectName("AIAvatar")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(28, 28)
        root.addWidget(avatar, 0, Qt.AlignTop)

        self._card = QFrame()
        self._card.setObjectName("AICard")
        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(6)
        self.body_layout = card_layout

        # Sonnet 角色标签
        role_label = QLabel("Sonnet")
        role_label.setObjectName("RoleLabel")
        role_label.setStyleSheet(
            "color: #6366F1; font-size: 11px; font-weight: 600; "
            "background: transparent; padding-bottom: 2px;"
        )
        card_layout.addWidget(role_label)

        root.addWidget(self._card, 1)

    # ── reviewer layout: avatar + card ─────────────────────────────
    def _build_reviewer(self, root: QHBoxLayout):
        avatar = QLabel("🔍")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(28, 28)
        avatar.setStyleSheet("""
            background: #FEF3C7; border-radius: 14px;
            font-size: 14px; border: 1.5px solid #F59E0B;
        """)
        root.addWidget(avatar, 0, Qt.AlignTop)

        self._card = QFrame()
        self._card.setObjectName("ReviewerCard")
        self._card.setStyleSheet("""
            QFrame#ReviewerCard {
                background: #FFFBEB;
                border: 1px solid #FDE68A;
                border-left: 3px solid #F59E0B;
                border-radius: 10px;
                padding: 12px 16px;
            }
            QFrame#ReviewerCard[active="true"] {
                border-left: 3px solid #D97706;
            }
        """)
        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(12, 10, 12, 12)
        card_layout.setSpacing(6)
        self.body_layout = card_layout

        role_label = QLabel("独立审查官")
        role_label.setStyleSheet(
            "color: #D97706; font-size: 11px; font-weight: 600; "
            "background: transparent; padding-bottom: 2px;"
        )
        card_layout.addWidget(role_label)

        root.addWidget(self._card, 1)

    def _ensure_thinking(self) -> "_ThinkingSection":
        if self._thinking is None:
            self._thinking = _ThinkingSection()
            self.body_layout.insertWidget(1, self._thinking)
        return self._thinking

    def append_thinking(self, chunk: str):
        self._ensure_thinking().append_text(chunk)

    def seal_thinking(self):
        if self._thinking:
            self._thinking.seal()

    def set_text(self, text: str):
        if self.text_label is None:
            self.text_label = QLabel()
            self.text_label.setObjectName("MessageText")
            self.text_label.setWordWrap(True)
            self.text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            if self.role == "user":
                self.text_label.setStyleSheet("background: transparent; font-size: 14px; color: white;")
            else:
                self.text_label.setStyleSheet("background: transparent; font-size: 14px;")
            self.body_layout.addWidget(self.text_label)
        self.text_label.setText(text)

    def append_text(self, chunk: str):
        current = self.text_label.text() if self.text_label else ""
        self.set_text(current + chunk)

    def add_tool_chip(self, name: str, status: str = "running"):
        label_map = {"running": "⋯ 运行中", "done": "✓", "error": "✗"}
        chip = QLabel(f"[🔧 {name}] {label_map.get(status, status)}")
        chip.setObjectName("ToolChip")
        chip.setProperty("status", status)
        chip.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.body_layout.addWidget(chip, 0, Qt.AlignLeft)
        self._chips.append(chip)
        return chip

    def _last_chip(self) -> QLabel | None:
        return self._chips[-1] if self._chips else None

    def add_download_card(self, path: str, summary: str = ""):
        card = DownloadCard(path, summary=summary)
        self.body_layout.addWidget(card)

    def set_active(self, active: bool):
        """运行中时给 AI/审查卡片加左侧边框指示器。"""
        if self.role in ("assistant", "reviewer") and hasattr(self, "_card"):
            self._card.setProperty("active", active)
            self._card.style().unpolish(self._card)
            self._card.style().polish(self._card)


# ── 会话标签栏 ──────────────────────────────────────────────────────
class SessionBar(QFrame):
    """每个模式可有多个对话会话，类似 Cursor 的多聊天记录。"""
    session_changed = Signal(int)    # 切换到 session index
    session_add = Signal()           # 新建会话

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SessionBar")
        self.setFixedHeight(36)
        self.setStyleSheet("""
            QFrame#SessionBar {
                background: #F1F5F9;
                border-bottom: 1px solid #E2E8F0;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(4)

        self._scroll_area = QScrollArea()
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll_area.setFrameShape(QScrollArea.NoFrame)
        self._scroll_area.setFixedHeight(36)
        self._scroll_area.setStyleSheet("background: transparent;")

        self._tab_widget = QWidget()
        self._tab_widget.setStyleSheet("background: transparent;")
        self._tab_layout = QHBoxLayout(self._tab_widget)
        self._tab_layout.setContentsMargins(0, 4, 0, 4)
        self._tab_layout.setSpacing(4)
        self._tab_layout.addStretch()
        self._scroll_area.setWidget(self._tab_widget)
        self._scroll_area.setWidgetResizable(True)
        layout.addWidget(self._scroll_area, 1)

        add_btn = QPushButton("+")
        add_btn.setFixedSize(24, 24)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: 1px solid #CBD5E1;
                border-radius: 4px; color: #64748B; font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover { background: #E2E8F0; }
        """)
        add_btn.clicked.connect(self.session_add)
        layout.addWidget(add_btn)

        self._buttons: list[QPushButton] = []
        self._current = 0

    _STATUS_DOT = {
        "running":   ("●", "#6366F1"),
        "reviewing": ("●", "#F59E0B"),
        "error":     ("●", "#DC2626"),
        "done":      ("●", "#059669"),
    }

    def set_sessions(self, names: list[str], current: int,
                     statuses: list[str] | None = None):
        # Clear existing tabs
        while self._tab_layout.count() > 0:
            item = self._tab_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._buttons.clear()

        self._current = current
        statuses = statuses or ["idle"] * len(names)
        for i, (name, status) in enumerate(zip(names, statuses)):
            is_active = (i == current)
            dot, dot_color = self._STATUS_DOT.get(status, ("", ""))
            label = f"{dot} {name}".strip() if dot else name
            btn = QPushButton(label)
            btn.setFixedHeight(26)
            btn.setCursor(Qt.PointingHandCursor)
            self._style_tab(btn, is_active, dot_color if not is_active else "")
            btn.clicked.connect(lambda _=False, idx=i: self.session_changed.emit(idx))
            self._tab_layout.addWidget(btn)
            self._buttons.append(btn)
        self._tab_layout.addStretch()

    def _style_tab(self, btn: QPushButton, active: bool, dot_color: str = ""):
        if active:
            btn.setStyleSheet("""
                QPushButton {
                    background: white; border: 1px solid #C7D2FE;
                    border-radius: 6px; color: #4F46E5; font-size: 12px;
                    padding: 0 10px; font-weight: 600;
                }
            """)
        else:
            extra_color = f"color: {dot_color};" if dot_color else "color: #64748B;"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: 1px solid transparent;
                    border-radius: 6px; {extra_color} font-size: 12px;
                    padding: 0 10px;
                }}
                QPushButton:hover {{ background: #E2E8F0; }}
            """)


class InputArea(QFrame):
    send_requested = Signal(str)
    stop_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("InputBox")
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("发送消息...")
        self.editor.setFixedHeight(60)
        # 明确指定背景和文字颜色，不依赖 transparent 继承（Windows 下 transparent 会导致文字不可见）
        self.editor.setStyleSheet(
            "QTextEdit { background-color: #FFFFFF; border: none;"
            " color: #1E293B; selection-background-color: #C7D2FE; }"
        )
        root.addWidget(self.editor)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.addStretch()
        self.send_btn = QPushButton("↑")
        self.send_btn.setObjectName("SendBtn")
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.clicked.connect(self._on_send)
        bottom.addWidget(self.send_btn)
        root.addLayout(bottom)

        self.editor.installEventFilter(self)
        self._busy = False

    def eventFilter(self, obj, ev):
        if obj is self.editor and ev.type() == ev.Type.KeyPress:
            ke: QKeyEvent = ev
            if ke.key() in (Qt.Key_Return, Qt.Key_Enter) and not (ke.modifiers() & Qt.ShiftModifier):
                self._on_send()
                return True
        return super().eventFilter(obj, ev)

    def _on_send(self):
        if self._busy:
            self.stop_requested.emit()
            return
        text = self.editor.toPlainText().strip()
        if not text:
            return
        self.editor.clear()
        self.send_requested.emit(text)

    def set_busy(self, busy: bool):
        self._busy = busy
        self.send_btn.setText("■" if busy else "↑")
        self.setProperty("busy", busy)
        self.style().unpolish(self)
        self.style().polish(self)


class ChatView(QWidget):
    """整个对话区：会话标签 + 滚动消息列表 + 底部输入。"""
    send_requested = Signal(str)
    stop_requested = Signal()
    session_changed = Signal(int)
    session_add = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ChatArea")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 会话标签栏
        self.session_bar = SessionBar()
        self.session_bar.session_changed.connect(self.session_changed)
        self.session_bar.session_add.connect(self.session_add)
        root.addWidget(self.session_bar)

        # 后台任务活动条（有后台 running session 时才显示）
        self._bg_strip = QLabel("")
        self._bg_strip.setObjectName("BgStrip")
        self._bg_strip.setStyleSheet("""
            QLabel#BgStrip {
                background: #EEF2FF;
                color: #4F46E5;
                font-size: 11px;
                padding: 3px 16px;
                border-bottom: 1px solid #C7D2FE;
            }
        """)
        self._bg_strip.setVisible(False)
        root.addWidget(self._bg_strip)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        root.addWidget(self.scroll, 1)

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.container)
        self.scroll_layout.setContentsMargins(48, 28, 48, 28)
        self.scroll_layout.setSpacing(20)
        self.scroll_layout.addStretch(1)
        self.scroll.setWidget(self.container)

        # 状态面板（工具历史 + 思考预览）
        self._status_bar = _StatusBar()
        root.addWidget(self._status_bar)

        input_wrap = QWidget()
        input_layout = QHBoxLayout(input_wrap)
        input_layout.setContentsMargins(40, 8, 40, 16)
        self.input_area = InputArea()
        self.input_area.send_requested.connect(self.send_requested)
        self.input_area.stop_requested.connect(self.stop_requested)
        input_layout.addWidget(self.input_area)
        root.addWidget(input_wrap)

    def update_status(self, iteration: int = 0, tool: str = "", state: str = "idle",
                      thinking_line: str = ""):
        self._status_bar.update_status(iteration, tool, state, thinking_line)

    def status_snapshot(self) -> dict:
        return self._status_bar.snapshot()

    def restore_status_snapshot(self, snap: dict):
        self._status_bar.restore_snapshot(snap)

    def set_background_activity(self, items: list[dict]):
        """items: [{"name": "会话2", "tool": "ws_load", "thinking": "..."}]"""
        if not items:
            self._bg_strip.setVisible(False)
            return
        parts = []
        for it in items:
            name = it.get("name", "?")
            tool = it.get("tool", "")
            thinking = it.get("thinking", "")
            if tool:
                parts.append(f"⚡ {name} → {tool}")
            elif thinking:
                snippet = thinking.strip()[:40].replace("\n", " ")
                parts.append(f"⚡ {name}：{snippet}")
            else:
                parts.append(f"⚡ {name} 运行中…")
        self._bg_strip.setText("   ".join(parts))
        self._bg_strip.setVisible(True)

    def add_message(self, role: str) -> MessageBlock:
        msg = MessageBlock(role)
        count = self.scroll_layout.count()
        self.scroll_layout.insertWidget(count - 1, msg)
        QTimer.singleShot(10, self._scroll_to_bottom)
        return msg

    def add_hint(self, text: str):
        label = QLabel(text)
        label.setObjectName("HintLabel")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        count = self.scroll_layout.count()
        self.scroll_layout.insertWidget(count - 1, label)

    def _scroll_to_bottom(self):
        sb = self.scroll.verticalScrollBar()
        sb.setValue(sb.maximum())

    def set_busy(self, busy: bool):
        self.input_area.set_busy(busy)

    def clear_messages(self):
        while self.scroll_layout.count() > 1:
            w = self.scroll_layout.takeAt(0).widget()
            if w:
                w.deleteLater()
        self._status_bar.update_status(state="idle")

    def set_sessions(self, names: list[str], current: int,
                     statuses: list[str] | None = None):
        self.session_bar.set_sessions(names, current, statuses)


class _StatusBar(QFrame):
    """输入框上方的状态面板：
       - 第一行：状态指示 + 轮次 + 当前工具
       - 中间：最近3个工具操作（横向滚动）
       - 最后：2行最新思考内容
    """

    _STATE_STYLES = {
        "idle":      ("●", "#CBD5E1", "就绪"),
        "running":   ("◎", "#6366F1", "运行中"),
        "reviewing": ("🔍", "#F59E0B", "审查中"),
        "stopped":   ("□", "#F59E0B", "已停止"),
        "done":      ("✓", "#059669", "待回复"),
        "error":     ("✗", "#DC2626", "出错"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusPanel")
        self.setStyleSheet("""
            QFrame#StatusPanel {
                background: #F8FAFC;
                border-top: 1px solid #E2E8F0;
            }
            QLabel { background: transparent; }
        """)
        root = QVBoxLayout(self)
        root.setContentsMargins(44, 6, 44, 6)
        root.setSpacing(4)

        # ── 行1：状态指示 ────────────────────────────────────────
        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 0, 0, 0)
        row1.setSpacing(8)

        self._dot = QLabel("●")
        self._dot.setFixedWidth(14)
        self._dot.setStyleSheet("font-size: 11px; color: #CBD5E1;")
        row1.addWidget(self._dot)

        self._state_label = QLabel("就绪")
        self._state_label.setFixedWidth(52)
        self._state_label.setStyleSheet("font-size: 11px; color: #64748B; font-weight: 600;")
        row1.addWidget(self._state_label)

        sep = QLabel("|")
        sep.setStyleSheet("color: #D1D5DB; font-size: 11px;")
        row1.addWidget(sep)

        self._iter_label = QLabel("")
        self._iter_label.setStyleSheet("font-size: 11px; color: #64748B;")
        row1.addWidget(self._iter_label)

        self._cur_tool_label = QLabel("")
        self._cur_tool_label.setStyleSheet("font-size: 11px; color: #6366F1;")
        row1.addWidget(self._cur_tool_label, 1)

        root.addLayout(row1)

        # ── 行2：最近3个工具操作（横向，可滚动）────────────────
        tool_scroll = QScrollArea()
        tool_scroll.setFixedHeight(26)
        tool_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tool_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tool_scroll.setFrameShape(QScrollArea.NoFrame)
        tool_scroll.setStyleSheet("background: transparent;")

        self._tool_container = QWidget()
        self._tool_container.setStyleSheet("background: transparent;")
        self._tool_row = QHBoxLayout(self._tool_container)
        self._tool_row.setContentsMargins(0, 0, 0, 0)
        self._tool_row.setSpacing(6)
        self._tool_row.addStretch()
        tool_scroll.setWidget(self._tool_container)
        tool_scroll.setWidgetResizable(True)
        root.addWidget(tool_scroll)

        # ── 行3：最新2行思考内容 ─────────────────────────────────
        self._think_label = QLabel("")
        self._think_label.setStyleSheet(
            "font-size: 11px; color: #94A3B8; background: transparent;"
        )
        self._think_label.setWordWrap(False)
        root.addWidget(self._think_label)

        self._tool_history: list[tuple[str, str]] = []  # (name, status)
        self._think_lines: list[str] = []
        self._update_tool_chips()
        self.setFixedHeight(86)

    def _update_tool_chips(self):
        # 清空
        while self._tool_row.count() > 1:
            item = self._tool_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 最近3个
        recent = self._tool_history[-3:] if self._tool_history else []
        for name, status in recent:
            chip = QLabel(f"🔧 {name} {status}")
            chip.setStyleSheet("""
                background: #EEF2FF; color: #4F46E5;
                border-radius: 8px; padding: 2px 8px;
                font-size: 11px;
            """)
            chip.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
            self._tool_row.insertWidget(self._tool_row.count() - 1, chip)

    def _update_think_preview(self):
        if not self._think_lines:
            self._think_label.setText("")
            return
        lines = self._think_lines[-2:]
        text = "  /  ".join(ln.strip()[:60] for ln in lines if ln.strip())
        self._think_label.setText(text)

    def update_status(self, iteration: int = 0, tool: str = "", state: str = "idle",
                      thinking_line: str = ""):
        dot_char, color, state_text = self._STATE_STYLES.get(state, self._STATE_STYLES["idle"])
        self._dot.setText(dot_char)
        self._dot.setStyleSheet(f"font-size: 11px; color: {color};")
        self._state_label.setText(state_text)
        self._state_label.setStyleSheet(f"font-size: 11px; color: {color}; font-weight: 600;")
        self._iter_label.setText(f"第 {iteration} 轮" if iteration > 0 else "")
        self._cur_tool_label.setText(f"→ {tool}" if tool else "")

    def add_tool_event(self, name: str, status: str):
        """添加一次工具事件到历史列表（running/✓/✗）。"""
        if status == "running":
            self._tool_history.append((name, "⋯"))
        else:
            # 更新最后一个同名工具的状态
            for i in range(len(self._tool_history) - 1, -1, -1):
                if self._tool_history[i][0] == name:
                    self._tool_history[i] = (name, status)
                    break
            else:
                self._tool_history.append((name, status))
        self._update_tool_chips()

    def add_thinking(self, chunk: str):
        """追加思考文字（状态栏预览）。"""
        combined = "".join(self._think_lines) + chunk
        self._think_lines = combined.split("\n")[-4:]
        self._update_think_preview()

    def reset_for_new_task(self):
        self._tool_history.clear()
        self._think_lines.clear()
        self._update_tool_chips()
        self._update_think_preview()

    def snapshot(self) -> dict:
        """保存状态栏当前快照，用于 session 切换恢复。"""
        return {
            "tool_history": list(self._tool_history),
            "think_lines": list(self._think_lines),
        }

    def restore_snapshot(self, snap: dict):
        """从快照恢复状态栏（session 切回时调用）。"""
        self._tool_history = list(snap.get("tool_history", []))
        self._think_lines = list(snap.get("think_lines", []))
        self._update_tool_chips()
        self._update_think_preview()
