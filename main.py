"""程序入口"""
import sys
import os

os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

from PySide6.QtWidgets import QApplication

from app.logger import setup_global_logging
from app.theme import QSS
from app.ui.main_window import MainWindow


def _install_exception_hook():
    import logging, traceback
    _log = logging.getLogger("levelassistant")

    def _hook(exc_type, exc_value, exc_tb):
        msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        _log.critical("未捕获异常导致崩溃:\n%s", msg)
        # 尝试写到桌面 crash.log
        try:
            crash_path = os.path.join(os.path.expanduser("~"), "Desktop",
                                      "LevelAssistant_crash.log")
            with open(crash_path, "a", encoding="utf-8") as f:
                import datetime
                f.write(f"\n=== {datetime.datetime.now()} ===\n{msg}")
        except Exception:
            pass
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = _hook


def main():
    setup_global_logging()
    _install_exception_hook()
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
