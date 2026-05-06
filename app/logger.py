"""日志配置：全局滚动日志 + 每任务独立日志"""
from __future__ import annotations

import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from .config import base_dir

_APP_LOGGER = "levelassistant"
_TASK_LOGGER = "levelassistant.task"

_fmt = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def setup_global_logging() -> None:
    """程序启动时调一次，写到 logs/app_YYYY-MM-DD.log"""
    log_dir = base_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger(_APP_LOGGER)
    if root.handlers:
        return
    root.setLevel(logging.DEBUG)

    fh = TimedRotatingFileHandler(
        log_dir / "app.log",
        when="midnight", backupCount=14,
        encoding="utf-8",
    )
    fh.setFormatter(_fmt)
    root.addHandler(fh)

    # 只在非 frozen 模式（开发时）才输出到控制台
    if not getattr(sys, "frozen", False):
        ch = logging.StreamHandler()
        ch.setFormatter(_fmt)
        root.addHandler(ch)

    root.info("=== LevelAssistant 启动 ===")


def get_app_logger() -> logging.Logger:
    return logging.getLogger(_APP_LOGGER)


def setup_task_logging(workspace: Path) -> logging.Logger:
    """每个任务开始时调一次，把这次任务的日志写到 workspace/task.log"""
    logger = logging.getLogger(f"{_TASK_LOGGER}.{workspace.name}")
    logger.setLevel(logging.DEBUG)
    logger.propagate = True  # 同时流向全局日志

    task_log = workspace / "task.log"
    fh = logging.FileHandler(task_log, encoding="utf-8")
    fh.setFormatter(_fmt)
    logger.addHandler(fh)

    logger.info("任务日志开始 workspace=%s", workspace)
    return logger
