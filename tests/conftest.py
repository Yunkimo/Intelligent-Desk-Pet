"""pytest 全局配置：无界面 Qt 平台 + 隔离 .env 影响。"""

import os
import sys
from pathlib import Path

# 必须在导入 PyQt6 之前设置，否则 CI 无显示环境会失败
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# 确保能 import pet 包（项目根目录）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402


@pytest.fixture(autouse=True)
def _no_dotenv(monkeypatch, tmp_path):
    """隔离真实密钥与可变配置，不读写开发者的设置和历史。"""
    import pet.config as cfg

    monkeypatch.setattr(cfg, "load_dotenv", lambda *a, **k: None)
    monkeypatch.setattr(cfg, "BASE_DIR", tmp_path)
    for key in ("LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL"):
        monkeypatch.delenv(key, raising=False)


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
