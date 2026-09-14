"""宠物主窗口：无边框/置顶/透明，组合形象、气泡、输入框，编排聊天与语音。"""

import os

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import QWidget

from .asr import ASREngine
from .bubble import SpeechBubble
from .config import Settings
from .input_box import ChatInput
from .llm import LLMClient
from .memory import Memory
from .persona import build_system_prompt
from .providers import create_chat_provider
from .sprite import PetSprite
from .tts import TTSEngine
from .worker import ASRWorker, ChatWorker, TTSWorker

_GAP = 8
_INPUT_H = 36
_BUBBLE_RESERVE = 240


class PetWindow(QWidget):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings

        # —— 引擎 ——
        self.llm = LLMClient(create_chat_provider(settings))
        self.asr_engine = ASREngine(settings.whisper_model)
        self.tts_engine = TTSEngine(settings.tts_voice, settings.tts_rate, settings.tts_pitch)

        # —— 记忆 ——
        self.memory = Memory(settings.history_path, settings.max_history, settings.persist_history)
        self.memory.set_system(build_system_prompt(settings))

        self._init_window()
        self._init_children()
        self._init_audio()

        # 拖拽/点击状态
        self._press_pos = None
        self._moved = False

        # worker 引用（保持存活，防被 GC）
        self.chat_worker: ChatWorker | None = None
        self.asr_worker: ASRWorker | None = None
        self.tts_worker: TTSWorker | None = None
        self._tts_tmp: str | None = None

    # ---------- 初始化 ----------
    def _init_window(self) -> None:
        self.setWindowTitle(self.settings.pet_name)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        s = self.settings.sprite_size
        self.win_w = max(320, s + 120)
        self.win_h = s + _INPUT_H + _BUBBLE_RESERVE + _GAP * 4
        self.resize(self.win_w, self.win_h)

        screen = QGuiApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(geo.right() - self.win_w - 40, geo.bottom() - self.win_h - 40)

    def _init_children(self) -> None:
        s = self.settings.sprite_size
        self.sprite = PetSprite(self.settings.assets_dir, self.settings.frames, s, parent=self)
        self.bubble = SpeechBubble(self.settings.bubble_timeout_ms, parent=self)
        self.input = ChatInput(parent=self)
        self.input.hide()

        self.input.submitted.connect(self.send_text)
        self.input.mic_toggled.connect(self.on_mic_toggled)
        self.bubble.resized.connect(self._position_bubble)

        self._layout_children()

    def _init_audio(self) -> None:
        self.player = QMediaPlayer(self)
        self.audio_out = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_out)
        self.audio_out.setVolume(1.0)
        self.player.mediaStatusChanged.connect(self._on_media_status)

    def _layout_children(self) -> None:
        s = self.settings.sprite_size
        sx = (self.width() - s) // 2
        sy = self.height() - s - _INPUT_H - _GAP * 2
        self.sprite.setGeometry(sx, sy, s, s)

        ix = (self.width() - self.input.width()) // 2
        iy = sy + s + _GAP
        self.input.move(ix, iy)

        self._position_bubble()

    def _position_bubble(self) -> None:
        if not self.bubble.isVisible():
            return
        bx = (self.width() - self.bubble.width()) // 2
        by = self.sprite.y() - self.bubble.height() - _GAP
        self.bubble.move(max(0, bx), max(0, by))

    # ---------- 拖拽与点击 ----------
    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.globalPosition().toPoint()
            self._moved = False

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._press_pos is not None and (event.buttons() & Qt.MouseButton.LeftButton):
            delta = event.globalPosition().toPoint() - self._press_pos
            if delta.manhattanLength() > 4:
                self._moved = True
                self.move(self.pos() + delta)
                self._press_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._moved:
                self.toggle_input()
            self._press_pos = None

    def toggle_input(self) -> None:
        if self.input.isVisible():
            self.input.hide()
        else:
            self.input.show()
            self.input.focus_input()

    # ---------- 文本/聊天 ----------
    def send_text(self, text: str) -> None:
        self.memory.add_user(text)
        self.input.hide()
        self.bubble.clear()
        self._start_chat(self.memory.get_messages())

    def _start_chat(self, messages: list[dict]) -> None:
        if self.chat_worker is not None and self.chat_worker.isRunning():
            return
        self.input.set_busy(True)
        self.chat_worker = ChatWorker(self.llm, messages, parent=self)
        self.chat_worker.chunk.connect(self.bubble.append_chunk)
        self.chat_worker.done.connect(self._on_chat_done)
        self.chat_worker.error.connect(self._on_chat_error)
        self.chat_worker.start()

    def _on_chat_done(self, text: str) -> None:
        self.input.set_busy(False)
        if text:
            self.memory.add_assistant(text)
            self.memory.save()
            if self.settings.enable_voice:
                self._speak(text)

    def _on_chat_error(self, msg: str) -> None:
        self.input.set_busy(False)
        self.bubble.set_text(f"呜…出错了：{msg}")

    # ---------- 语音合成 ----------
    def _speak(self, text: str) -> None:
        self.tts_worker = TTSWorker(self.tts_engine, text, parent=self)
        self.tts_worker.ready.connect(self._play_voice)
        self.tts_worker.error.connect(lambda e: print(f"[TTS] {e}"))
        self.tts_worker.start()

    def _play_voice(self, path: str) -> None:
        self._tts_tmp = path
        self.player.setSource(QUrl.fromLocalFile(path))
        self.player.play()

    def _on_media_status(self, status) -> None:
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._cleanup_tts_tmp()

    def _cleanup_tts_tmp(self) -> None:
        if self._tts_tmp:
            try:
                os.remove(self._tts_tmp)
            except OSError:
                pass
            self._tts_tmp = None

    # ---------- 语音识别 ----------
    def on_mic_toggled(self, listening: bool) -> None:
        if listening:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self) -> None:
        if self.asr_worker is not None and self.asr_worker.isRunning():
            return
        self.asr_worker = ASRWorker(self.asr_engine, self.settings.max_record_secs, parent=self)
        self.asr_worker.text.connect(self._on_asr_text)
        self.asr_worker.error.connect(self._on_asr_error)
        self.asr_worker.start()

    def _stop_recording(self) -> None:
        if self.asr_worker is not None and self.asr_worker.isRunning():
            self.asr_worker.request_stop()

    def _on_asr_text(self, text: str) -> None:
        self.input.set_listening(False)
        if text:
            self.input.edit.setText(text)
            self.send_text(text)
        else:
            self.bubble.set_text("没听清，再说一次嘛～")

    def _on_asr_error(self, msg: str) -> None:
        self.input.set_listening(False)
        self.bubble.set_text(f"听不到声音：{msg}")

    # ---------- 其它 ----------
    def show_hint(self, text: str) -> None:
        self.bubble.set_text(text)

    def closeEvent(self, event) -> None:  # noqa: N802
        self.memory.save()
        self._cleanup_tts_tmp()
        super().closeEvent(event)
