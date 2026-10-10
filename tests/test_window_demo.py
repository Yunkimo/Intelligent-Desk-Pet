"""真实 Qt 窗口与线程集成：离线聊天往返、忙碌保护和录音阻断。"""

from PyQt6.QtTest import QSignalSpy

from pet.config import Settings
from pet.window import PetWindow


def test_demo_window_chat_and_recording_guard(qapp):
    settings = Settings()
    settings.enable_demo()
    window = PetWindow(settings)
    try:
        window.show()
        before = window.memory.get_messages()
        window.send_text("   ")
        assert window.memory.get_messages() == before
        window.send_text("集成测试")
        completed = QSignalSpy(window.chat_worker.done)
        assert completed.wait(3000)
        assert window.chat_worker.wait(3000)
        qapp.processEvents()
        assert window.memory.get_messages()[-1]["role"] == "assistant"
        assert "集成测试" in window.memory.get_messages()[-1]["content"]
        window._start_recording()
        assert window.asr_worker is None and window.hotkey is None
        assert not settings.history_path.exists()
    finally:
        if window.chat_worker is not None:
            window.chat_worker.wait(3000)
        window.close()


def test_busy_send_does_not_mutate_memory(qapp):
    settings = Settings()
    settings.enable_demo()
    window = PetWindow(settings)

    class BusyWorker:
        def isRunning(self):
            return True

    try:
        before = window.memory.get_messages()
        window.chat_worker = BusyWorker()
        window.send_text("不应插入的重复消息")
        assert window.memory.get_messages() == before
    finally:
        window.chat_worker = None
        window.close()
