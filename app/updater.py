"""热更新模块：从 GitHub 检查并下载最新版本。

更新流程：
  1. UpdateChecker 在后台检查 version.json，对比当前版本
  2. 发现新版本后 UI 弹出通知
  3. UpdateDownloader 下载 skills.zip（和可选的新 EXE）
  4. apply_skills_update() 解压替换 skills 目录（立即生效）
  5. EXE 更新：写 bat 脚本在退出后替换，用户重启即可
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib import request as urllib_request

from PySide6.QtCore import QThread, Signal


# ── 版本比较 ─────────────────────────────────────────────────────────────────

def _version_tuple(v: str) -> tuple:
    try:
        return tuple(int(x) for x in v.strip().lstrip("v").split("."))
    except Exception:
        return (0,)


def is_newer(remote: str, current: str) -> bool:
    return _version_tuple(remote) > _version_tuple(current)


# ── 网络工具 ──────────────────────────────────────────────────────────────────

def _make_url(url: str, proxy_prefix: str) -> str:
    """按需拼接代理前缀（避免重复添加）。"""
    if proxy_prefix and not url.startswith(proxy_prefix):
        return proxy_prefix.rstrip("/") + "/" + url.lstrip("/")
    return url


def fetch_version_json(version_url: str, proxy_prefix: str = "", timeout: int = 10) -> dict:
    """拉取远端 version.json，返回字典。失败时抛异常。"""
    url = _make_url(version_url, proxy_prefix)
    req = urllib_request.Request(url, headers={"User-Agent": "LevelAssistant-Updater/1.0"})
    with urllib_request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download_file(url: str, dest: Path, proxy_prefix: str = "",
                  progress_cb=None, timeout: int = 120):
    """下载文件到 dest。progress_cb(downloaded_bytes, total_bytes)。"""
    url = _make_url(url, proxy_prefix)
    req = urllib_request.Request(url, headers={"User-Agent": "LevelAssistant-Updater/1.0"})
    with urllib_request.urlopen(req, timeout=timeout) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if progress_cb:
                    progress_cb(downloaded, total)


# ── 应用更新 ──────────────────────────────────────────────────────────────────

def _local_version_file() -> Path:
    from .config import base_dir
    return base_dir() / "version_local.json"


def get_local_version(fallback: str) -> str:
    """读取本地记录的已更新版本号，不存在则返回 fallback（APP_VERSION）。"""
    f = _local_version_file()
    try:
        if f.exists():
            return json.loads(f.read_text(encoding="utf-8")).get("version", fallback)
    except Exception:
        pass
    return fallback


def save_local_version(version: str):
    """更新成功后把版本号写到本地文件。"""
    try:
        _local_version_file().write_text(
            json.dumps({"version": version}, ensure_ascii=False), encoding="utf-8"
        )
    except Exception:
        pass


def apply_skills_update(zip_path: Path, new_version: str = "") -> tuple[bool, str]:
    """解压 skills.zip 替换 skills 目录。返回 (成功, 错误信息)。"""
    from .config import skills_dir
    target = skills_dir()
    backup = target.parent / (target.name + "_update_backup")
    tmp = zip_path.parent / "skills_extracted"
    try:
        # 备份
        if backup.exists():
            shutil.rmtree(backup)
        if target.exists():
            shutil.copytree(target, backup)

        # 解压
        if tmp.exists():
            shutil.rmtree(tmp)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp)

        # ZIP 内可能有顶层 "skills/" 子目录，也可能直接是内容
        if (tmp / "skills").is_dir():
            src = tmp / "skills"
        else:
            src = tmp

        # 替换
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(src, target)

        # 清理
        shutil.rmtree(tmp, ignore_errors=True)
        if backup.exists():
            shutil.rmtree(backup, ignore_errors=True)

        # 记录本地版本号，避免下次启动再次弹窗
        if new_version:
            save_local_version(new_version)

        return True, ""
    except Exception as e:
        # 尝试回滚
        try:
            if backup.exists():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(backup, target)
        except Exception:
            pass
        shutil.rmtree(tmp, ignore_errors=True)
        return False, str(e)


def schedule_exe_replace(new_exe: Path) -> bool:
    """已废弃，保留兼容。单文件 exe 替换（onedir 模式请用 apply_dir_update）。"""
    return False


def get_bat_path(new_exe: Path) -> Path:
    return new_exe.parent / "_la_update_apply.bat"


def apply_dir_update(zip_path: Path, new_version: str = "") -> tuple[bool, str]:
    """
    PyInstaller onedir 模式的整目录更新。
    zip 内顶层目录（如 LevelAssistant/）会整体覆盖当前安装目录。
    成功后写 bat 脚本，等程序退出后执行目录替换并重启。
    返回 (成功, bat路径或错误信息)。
    """
    if sys.platform != "win32":
        return False, "仅支持 Windows"

    current_exe = Path(sys.executable)
    install_dir = current_exe.parent          # e.g. dist/LevelAssistant/
    tmp_extract = zip_path.parent / "_la_new_ver"
    bat_path = zip_path.parent / "_la_dir_update.bat"

    try:
        # 解压
        if tmp_extract.exists():
            shutil.rmtree(tmp_extract)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_extract)

        # 找到 zip 内顶层目录（通常是 LevelAssistant/）
        top_entries = list(tmp_extract.iterdir())
        if len(top_entries) == 1 and top_entries[0].is_dir():
            new_dir = top_entries[0]
        else:
            new_dir = tmp_extract

        # 写 bat：等程序退出 → robocopy 整目录替换 → 重启
        script = (
            "@echo off\n"
            "timeout /t 5 /nobreak >nul\n"
            f'robocopy "{new_dir}" "{install_dir}" /MIR /NFL /NDL /NJH /NJS >nul\n'
            f'start "" "{current_exe}"\n'
            'del "%~f0"\n'
        )
        bat_path.write_text(script, encoding="gbk")

        if new_version:
            save_local_version(new_version)

        return True, str(bat_path)
    except Exception as e:
        shutil.rmtree(tmp_extract, ignore_errors=True)
        return False, str(e)


def get_dir_update_bat_path(zip_path: Path) -> Path:
    return zip_path.parent / "_la_dir_update.bat"


# ── 后台线程 ──────────────────────────────────────────────────────────────────

class UpdateChecker(QThread):
    """后台检查版本，不阻塞 UI。"""
    update_available = Signal(dict)   # version info dict
    no_update = Signal()
    check_failed = Signal(str)

    def __init__(self, version_url: str, current_version: str,
                 proxy_prefix: str = "", parent=None):
        super().__init__(parent)
        self._url = version_url
        self._current = current_version
        self._proxy = proxy_prefix

    def run(self):
        try:
            info = fetch_version_json(self._url, self._proxy)
            # 用本地记录的版本号（热更新后会更新），避免重复弹窗
            effective = get_local_version(self._current)
            if is_newer(info.get("version", "0.0.0"), effective):
                self.update_available.emit(info)
            else:
                self.no_update.emit()
        except Exception as e:
            self.check_failed.emit(str(e))


class UpdateDownloader(QThread):
    """后台下载更新包，发出进度和完成信号。"""
    progress = Signal(int, int)      # downloaded_bytes, total_bytes
    skills_ready = Signal(Path)      # skills zip 已下载完成
    exe_ready = Signal(Path)         # exe 已下载完成
    failed = Signal(str)

    def __init__(self, skills_url: str | None, exe_url: str | None,
                 proxy_prefix: str = "", parent=None):
        super().__init__(parent)
        self._skills_url = skills_url
        self._exe_url = exe_url
        self._proxy = proxy_prefix

    def run(self):
        try:
            tmp = Path(tempfile.mkdtemp(prefix="la_update_"))
            if self._skills_url:
                dest = tmp / "skills_update.zip"
                download_file(self._skills_url, dest, self._proxy,
                              progress_cb=lambda d, t: self.progress.emit(d, t))
                self.skills_ready.emit(dest)
            if self._exe_url:
                dest2 = tmp / "LevelAssistant_new.zip"
                download_file(self._exe_url, dest2, self._proxy,
                              progress_cb=lambda d, t: self.progress.emit(d, t))
                self.exe_ready.emit(dest2)
        except Exception as e:
            self.failed.emit(str(e))
