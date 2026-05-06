"""左侧输入面板：根据模式展示不同内容。"""
from __future__ import annotations

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QScrollArea

from .widgets import SingleFileZone, FileListZone, DescriptionBox


class Sidebar(QWidget):
    start_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(320)
        self._mode = "modify"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("QScrollArea{background: transparent;}")
        outer.addWidget(scroll, 1)

        self.body = QWidget()
        self.body.setStyleSheet("background: transparent;")
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(24, 24, 24, 24)
        self.body_layout.setSpacing(20)
        scroll.setWidget(self.body)

        self.start_btn = QPushButton("🚀 开始任务")
        self.start_btn.setObjectName("PrimaryButton")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setFixedHeight(40)
        self.start_btn.clicked.connect(self._on_start)
        btn_wrap = QWidget()
        btn_layout = QVBoxLayout(btn_wrap)
        btn_layout.setContentsMargins(24, 0, 24, 24)
        btn_layout.addWidget(self.start_btn)
        outer.addWidget(btn_wrap)

        self._build_modify()

    def _clear_body(self):
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _build_modify(self):
        self._clear_body()
        self.zone_archive = SingleFileZone("关卡包")
        self.body_layout.addWidget(self.zone_archive)

        self.zone_old = FileListZone("需要替换的文件", hint="拖放或点击 + 添加")
        self.body_layout.addWidget(self.zone_old)

        self.zone_new = FileListZone("修改到的文件", hint="拖放或点击 + 添加")
        self.body_layout.addWidget(self.zone_new)

        self.zone_desc = DescriptionBox("描述", "例如：换成春日主题，UI 更清新")
        self.body_layout.addWidget(self.zone_desc)

        self.body_layout.addStretch()
        self.start_btn.setText("🚀 开始修改")

    def _build_create(self, what: str):
        self._clear_body()
        self.zone_refs = FileListZone("参考文件", hint="拖放或点击 + 添加")
        self.body_layout.addWidget(self.zone_refs)

        self.zone_desc = DescriptionBox(
            "描述",
            f"描述你想生成的{what}，越详细越好。" if what else "详细描述你的需求...",
        )
        self.body_layout.addWidget(self.zone_desc)

        self.body_layout.addStretch()
        self.start_btn.setText(f"🚀 生成{what}" if what else "🚀 开始生成")

    def _build_resource_search(self):
        self._clear_body()
        from PySide6.QtWidgets import QLabel
        hint = QLabel(
            "描述你要搜索的资源，例如：\n"
            "• 推荐一个能开心跑跳的角色\n"
            "• 找 3 个可以打开的宝箱\n"
            "• 确认小核桃有没有战斗动画\n"
            "• 找一个室内教室场景和轻松 BGM"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #6B7280; font-size: 12px; line-height: 1.6;")
        hint.setAlignment(Qt.AlignTop)
        self.body_layout.addWidget(hint)

        self.zone_desc = DescriptionBox("搜索需求", "描述你需要的资源，可包含多类需求……")
        self.body_layout.addWidget(self.zone_desc)

        self.body_layout.addStretch()
        self.start_btn.setText("🔍 开始搜索")

    def set_mode(self, mode: str):
        self._mode = mode
        if mode == "modify":
            self._build_modify()
        elif mode == "create_level":
            self._build_create("新关卡")
        elif mode == "create_story":
            self._build_create("新剧情")
        elif mode == "resource_search":
            self._build_resource_search()
        elif mode == "free_chat":
            self._build_free_chat()

    def _build_free_chat(self):
        self._clear_body()
        from PySide6.QtWidgets import QLabel
        hint = QLabel(
            "自由对话模式\n\n"
            "直接在右侧输入框发消息即可，\n"
            "支持粘贴 / 拖入图片一起发送。\n\n"
            "AI 拥有全部工具能力，\n"
            "可随时让它搜索、读写文件等。"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #6B7280; font-size: 13px; line-height: 1.6;")
        hint.setAlignment(Qt.AlignTop)
        self.body_layout.addWidget(hint)
        self.body_layout.addStretch()
        self.start_btn.setText("💬 开始对话")

    def _on_start(self):
        if self._mode == "free_chat":
            self.start_requested.emit({"mode": "free_chat", "description": ""})
            return
        payload = {"mode": self._mode, "description": self.zone_desc.text()}
        if self._mode == "modify":
            payload["archive"] = self.zone_archive.path()
            payload["old_files"] = self.zone_old.paths()
            payload["new_files"] = self.zone_new.paths()
        elif self._mode == "resource_search":
            pass  # 只需描述文字
        else:
            payload["refs"] = self.zone_refs.paths()
        self.start_requested.emit(payload)

    def get_state(self) -> dict:
        """返回当前侧边栏所有输入字段的快照，用于 session 保存。"""
        state: dict = {"mode": self._mode}
        if self._mode == "modify":
            state["archive"] = getattr(self, "zone_archive", None) and self.zone_archive.path()
            state["old_files"] = getattr(self, "zone_old", None) and self.zone_old.paths() or []
            state["new_files"] = getattr(self, "zone_new", None) and self.zone_new.paths() or []
            state["desc"] = getattr(self, "zone_desc", None) and self.zone_desc.text() or ""
        elif self._mode in ("create_level", "create_story", "resource_search"):
            state["refs"] = getattr(self, "zone_refs", None) and self.zone_refs.paths() or []
            state["desc"] = getattr(self, "zone_desc", None) and self.zone_desc.text() or ""
        return state

    def restore_state(self, state: dict):
        """从保存的快照恢复输入字段。"""
        if not state:
            self.clear_inputs()
            return
        mode = state.get("mode", self._mode)
        if mode != self._mode:
            return   # 模式不同，不恢复
        if self._mode == "modify":
            if hasattr(self, "zone_archive") and state.get("archive"):
                self.zone_archive.set_file(state["archive"])
            if hasattr(self, "zone_old"):
                self.zone_old.clear()
                if state.get("old_files"):
                    self.zone_old.add_files(state["old_files"])
            if hasattr(self, "zone_new"):
                self.zone_new.clear()
                if state.get("new_files"):
                    self.zone_new.add_files(state["new_files"])
            if hasattr(self, "zone_desc"):
                self.zone_desc.editor.setPlainText(state.get("desc", ""))
        elif self._mode in ("create_level", "create_story"):
            if hasattr(self, "zone_refs"):
                self.zone_refs.clear()
                if state.get("refs"):
                    self.zone_refs.add_files(state["refs"])
            if hasattr(self, "zone_desc"):
                self.zone_desc.editor.setPlainText(state.get("desc", ""))
        elif self._mode == "resource_search":
            if hasattr(self, "zone_desc"):
                self.zone_desc.editor.setPlainText(state.get("desc", ""))

    def clear_inputs(self):
        """清空所有输入控件。"""
        if self._mode == "modify":
            if hasattr(self, "zone_archive"):
                self.zone_archive.clear()
            if hasattr(self, "zone_old"):
                self.zone_old.clear()
            if hasattr(self, "zone_new"):
                self.zone_new.clear()
            if hasattr(self, "zone_desc"):
                self.zone_desc.clear()
        elif self._mode in ("create_level", "create_story"):
            if hasattr(self, "zone_refs"):
                self.zone_refs.clear()
            if hasattr(self, "zone_desc"):
                self.zone_desc.clear()
        elif self._mode == "resource_search":
            if hasattr(self, "zone_desc"):
                self.zone_desc.clear()

    def set_enabled_inputs(self, enabled: bool):
        self.body.setEnabled(enabled)
        self.start_btn.setEnabled(enabled)
        if not enabled:
            self.start_btn.setText("⏳ 处理中…")
        else:
            # 恢复对应模式的原始文字
            texts = {
                "modify": "🚀 开始修改",
                "create_level": "🚀 生成新关卡",
                "create_story": "🚀 生成新剧情",
                "resource_search": "🔍 开始搜索",
                "free_chat": "💬 开始对话",
            }
            self.start_btn.setText(texts.get(self._mode, "🚀 开始"))
