"""应用引导。"""

import argparse
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from .config import Settings
from .webenv import enable_local_file_access, prepare_webengine
from .window import PetWindow


def run() -> int:
    parser = argparse.ArgumentParser(description="智能桌宠")
    parser.add_argument("--demo", action="store_true", help="无网络、无密钥的离线演示")
    parser.add_argument(
        "--selftest", action="store_true", help="检查窗口启动；演示模式同时检查聊天"
    )
    parser.add_argument("--screenshot", type=Path, help="自检结束前保存窗口截图")
    args = parser.parse_args()
    if args.screenshot and not args.selftest:
        parser.error("--screenshot 需要同时使用 --selftest")
    enable_local_file_access()  # 必须在 QApplication 之前，WebEngine 才能读取本地模型

    settings = Settings()
    if args.demo:
        settings.enable_demo()
    if settings.image_engine == "live2d":
        try:
            prepare_webengine()  # 必须在 QApplication 之前导入 WebEngineWidgets
        except ImportError:
            pass  # WebEngine 未安装，交由 create_avatar 回退到精灵引擎

    app = QApplication(sys.argv)
    app.setApplicationName("Intelligent Desk Pet")

    window = PetWindow(settings)
    window.show()

    if settings.demo_mode:
        window.show_hint("离线演示：可输入文字体验聊天，无需密钥；语音与历史保存已关闭。")
    elif not settings.llm_api_key:
        window.show_hint("还没配置 LLM_API_KEY 哦～在 .env 里填好再重启我就能聊天啦")
        print("警告：未配置 LLM_API_KEY，请在 .env 中填写（参考 .env.example）。")

    # 自检模式：完整构造 GUI 后短暂运行即退出（打包验证用，退出码 0 表示依赖齐全）
    if args.selftest:
        from PyQt6.QtCore import QTimer

        def finish() -> None:
            ok = not settings.demo_mode or any(
                m["role"] == "assistant" for m in window.memory.get_messages()
            )
            if args.screenshot:
                args.screenshot.parent.mkdir(parents=True, exist_ok=True)
                ok = window.grab().save(str(args.screenshot)) and ok
            window.close()
            app.exit(0 if ok else 1)

        if settings.demo_mode:
            QTimer.singleShot(100, lambda: window.send_text("你好，介绍一下离线演示"))
        QTimer.singleShot(2500, finish)
        return app.exec()

    return app.exec()
