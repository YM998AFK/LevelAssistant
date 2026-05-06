"""通用 UI 组件：拖放区、文件列表、输入框、下载卡片等"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, List, Optional

from PySide6.QtCore import Qt, Signal, QSize, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QPixmap
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QFileDialog, QFrame, QSizePolicy,
)


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} TB"


class DropZone(QWidget):
    """虚线框拖放区：支持拖放 + 点击选择。"""
    files_dropped = Signal(list)

    def __init__(self, hint: str = "拖放文件到此处 或 点击选择",
                 file_filter: str = "", multiple: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self._filter = file_filter
        self._multiple = multiple

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setAlignment(Qt.AlignCenter)
        icon = QLabel("↑")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("color: #94A3B8; font-size: 18px; background: transparent;")
        layout.addWidget(icon)
        self.label = QLabel(hint)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #94A3B8; font-size: 12px; background: transparent;")
        layout.addWidget(self.label)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self._open_dialog()

    def _open_dialog(self):
        if self._multiple:
            paths, _ = QFileDialog.getOpenFileNames(self, "选择文件", "", self._filter or "所有文件 (*)")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", self._filter or "所有文件 (*)")
            paths = [path] if path else []
        if paths:
            self.files_dropped.emit([p for p in paths if p])

    def dragEnterEvent(self, ev: QDragEnterEvent):
        if ev.mimeData().hasUrls():
            ev.acceptProposedAction()
            self.setProperty("dragging", True)
            self.style().unpolish(self); self.style().polish(self)

    def dragLeaveEvent(self, ev):
        self.setProperty("dragging", False)
        self.style().unpolish(self); self.style().polish(self)

    def dropEvent(self, ev: QDropEvent):
        urls = ev.mimeData().urls()
        paths = [u.toLocalFile() for u in urls if u.isLocalFile()]
        if paths:
            self.files_dropped.emit(paths if self._multiple else [paths[0]])
        self.setProperty("dragging", False)
        self.style().unpolish(self); self.style().polish(self)


class FileChip(QWidget):
    """一行文件展示：名字 + 大小 + 删除按钮。"""
    removed = Signal(str)

    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.path = path
        self.setObjectName("FileChip")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 6, 6)
        layout.setSpacing(6)

        p = Path(path)
        name = QLabel(p.name)
        name.setStyleSheet("background: transparent; font-size: 12px; color: #1E293B;")
        try:
            sz = p.stat().st_size
            size = QLabel(human_size(sz))
            size.setStyleSheet("color: #94A3B8; font-size: 11px; background: transparent;")
        except Exception:
            size = QLabel("")
        layout.addWidget(name, 1)
        layout.addWidget(size)

        btn = QPushButton("×")
        btn.setObjectName("RemoveBtn")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(20, 20)
        btn.clicked.connect(lambda: self.removed.emit(self.path))
        layout.addWidget(btn)


class FileListZone(QWidget):
    """一组文件上传区：顶部标签 + 添加链接 + 拖放区 + 文件列表。"""
    changed = Signal()

    def __init__(self, title: str, hint: str = "拖放或点击 + 添加",
                 file_filter: str = "", parent=None):
        super().__init__(parent)
        self._paths: List[str] = []
        self._filter = file_filter
        self.setAcceptDrops(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        label = QLabel(title)
        label.setProperty("sectionLabel", True)
        header.addWidget(label)
        header.addStretch()
        add_btn = QPushButton("+ 添加")
        add_btn.setObjectName("AddLinkBtn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._open_dialog)
        header.addWidget(add_btn)
        root.addLayout(header)

        self.drop = DropZone(hint=hint, file_filter=file_filter, multiple=True)
        self.drop.setMinimumHeight(48)
        self.drop.files_dropped.connect(self.add_files)
        root.addWidget(self.drop)

        self.list_layout = QVBoxLayout()
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(4)
        root.addLayout(self.list_layout)

    def _open_dialog(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "选择文件", "",
                                                self._filter or "所有文件 (*)")
        if paths:
            self.add_files(paths)

    def add_files(self, paths: list):
        for p in paths:
            if p and p not in self._paths:
                self._paths.append(p)
                chip = FileChip(p)
                chip.removed.connect(self.remove_file)
                self.list_layout.addWidget(chip)
        self.changed.emit()

    def remove_file(self, path: str):
        if path in self._paths:
            self._paths.remove(path)
        for i in range(self.list_layout.count() - 1, -1, -1):
            w = self.list_layout.itemAt(i).widget()
            if isinstance(w, FileChip) and w.path == path:
                w.deleteLater()
        self.changed.emit()

    def paths(self) -> List[str]:
        return list(self._paths)

    def clear(self):
        self._paths.clear()
        while self.list_layout.count():
            w = self.list_layout.takeAt(0).widget()
            if w:
                w.deleteLater()
        self.changed.emit()


class SingleFileZone(QWidget):
    """单文件上传（比如关卡包）。"""
    changed = Signal()

    def __init__(self, title: str, hint: str = "拖放 .zip 到此处 或 点击选择",
                 file_filter: str = "压缩包 (*.zip *.7z *.tar *.gz *.bz2)", parent=None):
        super().__init__(parent)
        self._path: Optional[str] = None
        self._filter = file_filter

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        label = QLabel(title)
        label.setProperty("sectionLabel", True)
        root.addWidget(label)

        self.drop = DropZone(hint=hint, file_filter=file_filter, multiple=False)
        self.drop.setMinimumHeight(72)
        self.drop.files_dropped.connect(lambda paths: self.set_file(paths[0] if paths else None))
        root.addWidget(self.drop)

        self.chip_holder = QVBoxLayout()
        self.chip_holder.setContentsMargins(0, 0, 0, 0)
        root.addLayout(self.chip_holder)

    def set_file(self, path: Optional[str]):
        self._path = path
        while self.chip_holder.count():
            w = self.chip_holder.takeAt(0).widget()
            if w:
                w.deleteLater()
        if path:
            self.drop.hide()
            chip = FileChip(path)
            chip.removed.connect(lambda _: self.set_file(None))
            self.chip_holder.addWidget(chip)
        else:
            self.drop.show()
        self.changed.emit()

    def path(self) -> Optional[str]:
        return self._path

    def clear(self):
        self.set_file(None)


class DescriptionBox(QWidget):
    def __init__(self, title: str = "描述", placeholder: str = "详细描述要改什么...",
                 parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        label = QLabel(title)
        label.setProperty("sectionLabel", True)
        root.addWidget(label)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText(placeholder)
        self.editor.setFixedHeight(100)
        root.addWidget(self.editor)

    def text(self) -> str:
        return self.editor.toPlainText().strip()

    def clear(self):
        self.editor.clear()


class DownloadCard(QFrame):
    """AI 完成后显示在对话里的下载卡片。"""

    def __init__(self, file_path: str, summary: str = "", parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setObjectName("DownloadCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        icon = QLabel("📦")
        icon.setStyleSheet("font-size: 24px; background: transparent;")
        layout.addWidget(icon)

        info = QVBoxLayout()
        info.setSpacing(2)
        p = Path(file_path)
        name = QLabel(p.name)
        name.setStyleSheet("font-weight: 600; font-size: 13px; background: transparent;")
        info.addWidget(name)
        try:
            sz = p.stat().st_size
            sub = QLabel(f"{human_size(sz)} · {summary}" if summary else human_size(sz))
        except Exception:
            sub = QLabel(summary)
        sub.setStyleSheet("color: #6B7280; font-size: 12px; background: transparent;")
        info.addWidget(sub)
        layout.addLayout(info, 1)

        btn = QPushButton("↓ 下载")
        btn.setObjectName("SecondaryButton")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(32)
        btn.clicked.connect(self._download)
        layout.addWidget(btn)

    def _download(self):
        src = Path(self.file_path)
        if not src.exists():
            return
        dst, _ = QFileDialog.getSaveFileName(self, "保存到", src.name,
                                             f"压缩包 (*{src.suffix})")
        if dst:
            import shutil
            shutil.copy2(src, dst)
