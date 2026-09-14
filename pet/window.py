"""宠物主窗口：无边框/置顶/透明，组合形象、气泡、输入框，编排聊天与语音。"""

import os
import shutil
from pathlib import Path

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import QFileDialog, QInputDialog, QMenu, QWidget

from .asr import ASREngine
from .avatar import create_avatar
from .bubble import SpeechBubble
from .config import Settings
from .input_box import ChatInput
from .llm import LLMClient
from .memory import Memory
from .persona import build_system_prompt
from .providers import create_chat_provider
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
        self._size_and_position()
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

    def _init_children(self) -> None:
        self.avatar = create_avatar(self.settings, parent=self)
        self.bubble = SpeechBubble(self.settings.bubble_timeout_ms, parent=self)
        self.input = ChatInput(parent=self)
        self.input.hide()

        self.input.submitted.connect(self.send_text)
        self.input.mic_toggled.connect(self.on_mic_toggled)
        self.bubble.resized.connect(self._position_bubble)

    def _init_audio(self) -> None:
        self.player = QMediaPlayer(self)
        self.audio_out = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_out)
        self.audio_out.setVolume(1.0)
        self.player.mediaStatusChanged.connect(self._on_media_status)

    def _size_and_position(self) -> None:
        sw = self.avatar.widget.width()
        sh = self.avatar.widget.height()
        self.win_w = max(320, sw + 120)
        self.win_h = sh + _INPUT_H + _BUBBLE_RESERVE + _GAP * 4
        self.resize(self.win_w, self.win_h)

        screen = QGuiApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(geo.right() - self.win_w - 40, geo.bottom() - self.win_h - 40)

        self._layout_children()

    def _layout_children(self) -> None:
        sw = self.avatar.widget.width()
        sh = self.avatar.widget.height()
        sx = (self.width() - sw) // 2
        sy = self.height() - sh - _INPUT_H - _GAP * 2
        self.avatar.widget.setGeometry(sx, sy, sw, sh)

        ix = (self.width() - self.input.width()) // 2
        iy = sy + sh + _GAP
        self.input.move(ix, iy)

        self._position_bubble()

    def _position_bubble(self) -> None:
        if not self.bubble.isVisible():
            return
        bx = (self.width() - self.bubble.width()) // 2
        by = self.avatar.widget.y() - self.bubble.height() - _GAP
        self.bubble.move(max(0, bx), max(0, by))

    # ---------- 拖拽与点击 ----------
    def _hit_avatar(self, pos) -> bool:
        """判断给定窗口坐标是否落在形象区域内，避免透明空白区误触。"""
        return self.avatar.widget.geometry().contains(pos)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if not self._hit_avatar(event.position().toPoint()):
            return
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
        if event.button() != Qt.MouseButton.LeftButton or self._press_pos is None:
            return
        if not self._moved:
            self.toggle_input()
        self._press_pos = None
        self._moved = False

    def toggle_input(self) -> None:
        if self.input.isVisible():
            self.input.hide()
        else:
            self.input.show()
            self.input.focus_input()

    # ---------- 更换形象 / 切换人设 ----------
    def contextMenuEvent(self, event) -> None:  # noqa: N802
        if not self._hit_avatar(event.pos()):
            return
        menu = QMenu(self)

        change = menu.addAction("更换形象…")
        change.triggered.connect(self._choose_image)

        if self.avatar.supports_motion:
            poke = menu.addAction("逗一下 ♪")
            poke.triggered.connect(lambda: self.avatar.react("poke"))
            expr_menu = menu.addMenu("切换表情")
            for name in self.avatar.expressions:
                act = expr_menu.addAction(name)
                act.triggered.connect(lambda _checked=False, n=name: self.avatar.set_expression(n))
        else:
            to_live2d = menu.addAction("切换为 Live2D 动态形象")
            to_live2d.triggered.connect(lambda: self._switch_engine("live2d"))

        persona_menu = menu.addMenu("切换人设")
        for name in self.settings.personas:
            act = persona_menu.addAction(name)
            act.triggered.connect(lambda _checked=False, n=name: self._switch_persona(n))
        persona_menu.addSeparator()
        add_act = persona_menu.addAction("添加人设…")
        add_act.triggered.connect(self._add_persona)

        quit_act = menu.addAction("退出")
        quit_act.triggered.connect(self.close)

        menu.exec(event.globalPos())

    def _switch_persona(self, name: str) -> None:
        if not self.settings.switch_persona(name):
            return
        self.memory.set_system(build_system_prompt(self.settings))
        self.setWindowTitle(self.settings.pet_name)
        self.bubble.set_text(f"人设已切换为「{name}」")

    def _add_persona(self) -> None:
        name, ok = QInputDialog.getText(self, "添加人设", "人设名字：")
        if not ok or not name.strip():
            return
        personality, ok = QInputDialog.getMultiLineText(self, "添加人设", f"「{name}」的性格描述：")
        if not ok:
            return
        tone, ok = QInputDialog.getMultiLineText(self, "添加人设", f"「{name}」的说话语气：")
        if not ok:
            return
        if self.settings.add_persona(name, personality, tone):
            self._switch_persona(name)

    def _choose_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "选择桌宠形象", "",
            "图片 (*.png *.jpg *.jpeg *.gif *.webp *.bmp)",
        )
        if not path:
            return
        self._apply_image(Path(path))

    def _apply_image(self, src: Path) -> None:
        """更换形象：用图片/动图引擎显示所选图片（必要时先从 Live2D 切过来）。"""
        dest = self._normalize_image(src)
        self.settings.update_frames([dest.name])
        if self.settings.image_engine != "sprite":
            self._switch_engine("sprite")  # 会按新 frames 重建并布局
        else:
            self.avatar.set_appearance(dest, self.settings.sprite_size)
            self._size_and_position()

    def _switch_engine(self, engine: str) -> None:
        """运行时切换形象引擎（图片 ↔ Live2D），重建形象控件并重新布局。"""
        if engine == self.settings.image_engine:
            return
        self.settings.update_image_engine(engine)

        old = self.avatar.widget
        old.hide()
        old.setParent(None)
        old.deleteLater()

        self.avatar = create_avatar(self.settings, parent=self)
        self.avatar.widget.show()
        self._size_and_position()

    def _normalize_image(self, src: Path) -> Path:
        """把用户选中的图统一转成 Qt 能稳定读取的格式，复制进 assets/ 并返回路径。"""
        from PIL import Image

        im = Image.open(src)
        if getattr(im, "is_animated", False):
            ext = src.suffix.lower() or ".gif"
            dest = self.settings.assets_dir / f"custom{ext}"
            shutil.copyfile(src, dest)
        else:
            im = self._trim_transparent(im.convert("RGBA"))
            dest = self.settings.assets_dir / "custom.webp"
            im.save(dest, lossless=True)
        return dest

    @staticmethod
    def _trim_transparent(im):
        """裁掉四周全透明边，让形象更贴合、显示更大。"""
        bbox = im.getchannel("A").getbbox()
        return im.crop(bbox) if bbox else im

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
        self.avatar.react("speak")

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
