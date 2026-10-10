"""录制真实 Qt 窗口离线演示，不捕获桌面：python scripts/record_demo.py。"""

import argparse
import io
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import imageio_ffmpeg  # noqa: E402
from PIL import Image  # noqa: E402
from PyQt6.QtCore import QBuffer, QIODevice, QTimer  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

from pet.config import Settings  # noqa: E402
from pet.window import PetWindow  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("reports/offline-demo.mp4"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    settings = Settings()
    settings.enable_demo()
    app = QApplication([])
    window = PetWindow(settings)
    window.show()
    window.show_hint("离线演示：无需密钥，使用内置绘制形象。")
    writer = imageio_ffmpeg.write_frames(
        str(args.output),
        (window.width(), window.height()),
        fps=10,
        codec="libx264",
        macro_block_size=2,
    )
    writer.send(None)
    frames = 0

    def capture() -> None:
        nonlocal frames
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        window.grab().save(buffer, "PNG")
        rgba = Image.open(io.BytesIO(bytes(buffer.data()))).convert("RGBA")
        background = Image.new("RGB", rgba.size, "#eef2f8")
        background.paste(rgba, mask=rgba.getchannel("A"))
        writer.send(background.tobytes())
        frames += 1
        if frames == 15:
            window.toggle_input()
            window.input.edit.setText("你好，介绍一下离线演示")
        elif frames == 30:
            window.input.submitted.emit(window.input.edit.text())
        elif frames == 65:
            window.toggle_input()
            window.input.edit.setText("再见，下次一起学习设计模式")
        elif frames == 80:
            window.input.submitted.emit(window.input.edit.text())
        elif frames >= 110:
            timer.stop()
            writer.close()
            ok = sum(m["role"] == "assistant" for m in window.memory.get_messages()) == 2
            window.close()
            app.exit(0 if ok else 1)

    timer = QTimer()
    timer.timeout.connect(capture)
    timer.start(100)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
