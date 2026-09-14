"""入口：python main.py 启动桌面宠物。"""

import os
import sys

from pet.app import run


def _guard_stdio() -> None:
    """窗口化打包时 stdout/stderr 可能为 None，避免 print 崩溃。"""
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")


if __name__ == "__main__":
    _guard_stdio()
    sys.exit(run())
