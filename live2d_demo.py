"""Live2D 桌宠形象 demo：透明窗口 + 透明 WebView 渲染昔涟模型。

用法：
    python live2d_demo.py           正常显示（拖拽移动窗口，Esc/关闭退出）
    python live2d_demo.py --check   离线自检：加载后截图并退出
"""

import base64
import sys
from pathlib import Path

from pet.live2d_view import enable_local_file_access

enable_local_file_access()

from PyQt6.QtCore import Qt, QTimer  # noqa: E402
from PyQt6.QtWidgets import QApplication, QWidget  # noqa: E402

from pet.live2d_view import Live2DView  # noqa: E402


class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("昔涟 Live2D")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(360, 480)

        self.view = Live2DView(360, 480, parent=self)
        self.view.setGeometry(0, 0, 360, 480)

        self._press_pos = None

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):  # noqa: N802
        if self._press_pos is not None and (event.buttons() & Qt.MouseButton.LeftButton):
            delta = event.globalPosition().toPoint() - self._press_pos
            self.move(self.pos() + delta)
            self._press_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):  # noqa: N802
        self._press_pos = None


def run_check(app: QApplication, win: DemoWindow) -> None:
    """自检：轮询模型加载状态，成功后截图退出。"""
    state = {"attempts": 0}

    def poll():
        state["attempts"] += 1
        if state["attempts"] > 50:  # ~25s 超时
            print("[check] TIMEOUT waiting for model")
            app.quit()
            return
        win.view.page().runJavaScript(
            "JSON.stringify({ready: window.__live2dReady, size: window.__live2dSize, err: window.__live2dError, errs: window.__jsErrors})",
            on_state,
        )

    def on_state(js: str):
        import json

        data = json.loads(js or "{}")
        if data.get("ready"):
            print("[check] model READY, size =", data.get("size"))
            win.view.page().runJavaScript(
                "window.__snapshot ? window.__snapshot() : 'NO_SNAPSHOT'", on_snapshot
            )
        elif data.get("err") or data.get("errs"):
            print("[check] model ERROR:", data.get("err"))
            for e in data.get("errs", []):
                print("[check]   js:", e)
            app.quit()
        else:
            QTimer.singleShot(500, poll)

    def on_snapshot(dataurl: str):
        if isinstance(dataurl, str) and dataurl.startswith("data:image/png;base64,"):
            b64 = dataurl.split(",", 1)[1]
            path = Path("_live2d_canvas.png")
            path.write_bytes(base64.b64decode(b64))
            print(f"[check] canvas snapshot saved -> {path} ({path.stat().st_size} bytes)")
        else:
            print("[check] snapshot unavailable:", str(dataurl)[:120])
        # 顺带抓一次 Qt 侧 widget（验证 WebView 透明合成）
        pm = win.view.grab()
        path2 = Path("_live2d_widget.png")
        pm.save(str(path2))
        print(f"[check] widget grab saved -> {path2} ({path2.stat().st_size} bytes)")
        app.quit()

    QTimer.singleShot(1000, poll)


def main() -> int:
    app = QApplication(sys.argv)
    win = DemoWindow()
    win.show()
    if "--check" in sys.argv:
        run_check(app, win)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
