"""热更新对话框：版本通知 + 下载进度。"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QTextEdit, QMessageBox,
)

from ..updater import (
    UpdateDownloader, apply_skills_update, apply_dir_update, get_dir_update_bat_path,
)


class UpdateNotifyDialog(QDialog):
    """发现新版本通知弹窗。"""

    def __init__(self, info: dict, proxy_prefix: str = "", parent=None):
        super().__init__(parent)
        self._info = info
        self._proxy = proxy_prefix
        self._downloader: UpdateDownloader | None = None
        self._new_exe_zip: Path | None = None
        self._bat_path: Path | None = None

        self.setWindowTitle("发现新版本")
        self.setMinimumWidth(420)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 版本标题
        ver = self._info.get("version", "?")
        title = QLabel(f"🎉  发现新版本  <b>v{ver}</b>")
        title.setStyleSheet("font-size: 15px; padding: 4px 0;")
        layout.addWidget(title)

        # 更新日志
        changelog = self._info.get("changelog", "").strip()
        if changelog:
            log_label = QLabel("更新内容：")
            log_label.setStyleSheet("color: #6b7280; font-size: 12px;")
            layout.addWidget(log_label)
            log = QTextEdit()
            log.setReadOnly(True)
            log.setPlainText(changelog)
            log.setMaximumHeight(120)
            log.setStyleSheet(
                "background: #f9fafb; border: 1px solid #e5e7eb; "
                "border-radius: 6px; padding: 6px; font-size: 12px;"
            )
            layout.addWidget(log)

        # 进度条（隐藏直到下载开始）
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(True)
        self._progress.hide()
        layout.addWidget(self._progress)

        # 状态文字
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #6b7280; font-size: 12px;")
        self._status_label.hide()
        layout.addWidget(self._status_label)

        # 按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self._later_btn = QPushButton("稍后再说")
        self._later_btn.setFixedWidth(90)
        self._later_btn.clicked.connect(self.reject)
        btn_row.addWidget(self._later_btn)

        self._update_btn = QPushButton("立即更新")
        self._update_btn.setFixedWidth(90)
        self._update_btn.setDefault(True)
        self._update_btn.clicked.connect(self._start_download)
        btn_row.addWidget(self._update_btn)

        layout.addLayout(btn_row)

    def _start_download(self):
        self._update_btn.setEnabled(False)
        self._later_btn.setEnabled(False)
        self._progress.show()
        self._status_label.show()
        self._status_label.setText("正在连接...")

        skills_url = self._info.get("skills_url") or ""
        exe_url = self._info.get("exe_url") or ""

        # 只在打包运行时才下载 EXE（开发模式不替换）
        if not getattr(sys, "frozen", False):
            exe_url = ""

        self._downloader = UpdateDownloader(
            skills_url=skills_url or None,
            exe_url=exe_url or None,
            proxy_prefix=self._proxy,
            parent=self,
        )
        self._downloader.progress.connect(self._on_progress)
        self._downloader.skills_ready.connect(self._on_skills_ready)
        self._downloader.exe_ready.connect(self._on_exe_ready)
        self._downloader.failed.connect(self._on_failed)
        self._downloader.finished.connect(self._on_download_finished)
        self._downloader.start()

    def _on_progress(self, downloaded: int, total: int):
        if total > 0:
            pct = int(downloaded * 100 / total)
            self._progress.setValue(pct)
            mb_d = downloaded / 1024 / 1024
            mb_t = total / 1024 / 1024
            self._status_label.setText(f"下载中… {mb_d:.1f} / {mb_t:.1f} MB")
        else:
            kb = downloaded // 1024
            self._status_label.setText(f"下载中… {kb} KB")

    def _on_skills_ready(self, zip_path: Path):
        self._status_label.setText("正在应用 skills 更新…")
        new_ver = self._info.get("version", "")
        ok, err = apply_skills_update(zip_path, new_version=new_ver)
        if not ok:
            self._status_label.setText(f"应用失败：{err}")

    def _on_exe_ready(self, zip_path: Path):
        self._new_exe_zip = zip_path
        new_ver = self._info.get("version", "")
        ok, result = apply_dir_update(zip_path, new_version=new_ver)
        if ok:
            self._bat_path = Path(result)
        else:
            self._status_label.setText(f"程序更新准备失败：{result}")

    def _on_failed(self, msg: str):
        self._progress.hide()
        self._status_label.setText(f"下载失败：{msg}")
        self._update_btn.setText("重试")
        self._update_btn.setEnabled(True)
        self._later_btn.setEnabled(True)
        self._update_btn.clicked.disconnect()
        self._update_btn.clicked.connect(self._start_download)

    def _on_download_finished(self):
        if self._bat_path and getattr(sys, "frozen", False):
            # 有程序更新，提示重启
            self._progress.setValue(100)
            self._status_label.setText("✅ 下载完成！重启程序后将自动更新到新版本。")
            self._update_btn.setText("重启应用")
            self._update_btn.setEnabled(True)
            self._update_btn.clicked.disconnect()
            self._update_btn.clicked.connect(self._restart_app)
            self._later_btn.setText("稍后重启")
            self._later_btn.setEnabled(True)
        else:
            # 只有 skills 更新，立即生效无需重启
            self._progress.setValue(100)
            self._status_label.setText("✅ skills 已更新，下次任务即可使用新版本。")
            QTimer.singleShot(1500, self.accept)

    def _restart_app(self):
        if self._bat_path and self._bat_path.exists():
            try:
                import subprocess
                subprocess.Popen(
                    ["cmd", "/c", str(self._bat_path)],
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                )
            except Exception:
                pass
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
