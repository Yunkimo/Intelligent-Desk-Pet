"""Live2D 形象视图：透明 QWebEngineView，渲染 pixi-live2d-display 的昔涟模型。"""

from pathlib import Path

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QWidget

from .webenv import enable_local_file_access  # noqa: F401  # 供 live2d_demo.py 复用

__all__ = ["Live2DView", "enable_local_file_access"]

BASE_DIR = Path(__file__).resolve().parent.parent
LIVE2D_DIR = BASE_DIR / "assets" / "live2d"


class Live2DView(QWebEngineView):
    """加载并渲染 assets/live2d/index.html 的透明 WebView。"""

    def __init__(self, width: int = 360, height: int = 480, parent=None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.resize(width, height)
        self.setMinimumSize(width, height)

        page = self.page()
        page.setBackgroundColor(Qt.GlobalColor.transparent)
        page.settings().setAttribute(
            page.settings().WebAttribute.ShowScrollBars, False
        )

        # 桌面宠物需由父窗口接管鼠标（拖拽/点击），故让 WebView 对鼠标事件穿透
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.loadFinished.connect(self._make_click_through)

        self.load(QUrl.fromLocalFile(str(LIVE2D_DIR / "index.html")))

    def _make_click_through(self, _ok: bool) -> None:
        """页面加载后，对内部 Chromium 子控件同样设置穿透（子控件是延迟创建的）。"""
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        for child in self.findChildren(QWidget):
            child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    # —— 供上层控制的桥接 ——
    def play_motion(self, group: str, index: int = 0) -> None:
        self.page().runJavaScript(f"window.live2d && window.live2d.motion({group!r}, {index})")

    def set_expression(self, name: str) -> None:
        self.page().runJavaScript(f"window.live2d && window.live2d.expression({name!r})")
