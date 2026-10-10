"""配置加载：合并 .env（密钥）与 config.json（非敏感配置）。"""

import math
import os
from pathlib import Path

from dotenv import load_dotenv

from .paths import app_dir
from .storage import read_object, write_object

# 项目根目录（pet/ 的上一级；打包后为 exe 所在目录）
BASE_DIR = app_dir()


class Settings:
    """应用配置的统一入口，各模块从这里取值。"""

    def __init__(self) -> None:
        load_dotenv(BASE_DIR / ".env")

        # —— 来自 .env 的密钥/模型配置 ——
        self.llm_api_key: str = os.getenv("LLM_API_KEY", "").strip()
        self.llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.deepseek.com").strip()
        self.llm_model: str = os.getenv("LLM_MODEL", "deepseek-chat").strip()
        self.demo_mode = False

        # —— 来自 config.json 的非敏感配置 ——
        self._load_json()

    def _load_json(self) -> None:
        path = BASE_DIR / "config.json"
        data = read_object(path)

        self.pet_name: str = data.get("pet_name", "小萌")
        persona = data.get("persona", {})
        self.personality: str = persona.get("personality", "活泼可爱")
        self.tone: str = persona.get("tone", "口语化、简短俏皮")
        self.personas: dict[str, dict] = data.get("personas", {})

        self.llm_timeout = self._number(data, "llm_timeout", 30, 1, 120)
        self.llm_max_retries = int(self._number(data, "llm_max_retries", 1, 0, 3))
        self.llm_temperature = self._number(data, "llm_temperature", 0.9, 0, 2)
        self.llm_max_tokens = int(self._number(data, "llm_max_tokens", 1024, 1, 8192))

        self.frames: list[str] = data.get("frames", [])
        self.sprite_size: int = int(data.get("sprite_size", 180))

        # 形象引擎：sprite（图片/动图）或 live2d（透明 WebView 渲染）
        self.image_engine: str = data.get("image_engine", "sprite")
        self.live2d_width: int = int(data.get("live2d_width", 360))
        self.live2d_height: int = int(data.get("live2d_height", 360))
        self.live2d_model: str = data.get("live2d_model", "cyrene")

        self.whisper_model: str = data.get("whisper_model", "base")
        self.tts_voice: str = data.get("tts_voice", "zh-CN-XiaoyouNeural")
        self.tts_rate: str = data.get("tts_rate", "+10%")
        self.tts_pitch: str = data.get("tts_pitch", "+20Hz")
        self.enable_voice: bool = bool(data.get("enable_voice", True))
        # 全局语音快捷键：长按开始录音、松开停止并识别（默认 Ctrl+T）
        self.voice_hotkey: str = data.get("voice_hotkey", "ctrl+t")

        self.max_history = int(self._number(data, "max_history", 20, 1, 1000))
        self.max_record_secs = self._number(data, "max_record_secs", 15, 1, 120)
        self.bubble_timeout_ms: int = int(data.get("bubble_timeout_ms", 8000))
        self.persist_history: bool = bool(data.get("persist_history", True))

        # 路径统一解析为绝对路径
        self.assets_dir: Path = BASE_DIR / data.get("assets_dir", "assets")
        self.history_path: Path = BASE_DIR / data.get("history_path", "data/history.json")

    def _save_json(self, **updates: object) -> None:
        """把给定字段合并写回 config.json，保留其余字段。"""
        path = BASE_DIR / "config.json"
        data = read_object(path)
        data.update(updates)
        write_object(path, data)

    @staticmethod
    def _number(data: dict, key: str, default: float, low: float, high: float) -> float:
        value = data.get(key, default)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{key} 必须是数值")
        if not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f"{key} 必须在 {low} 到 {high} 之间")
        if key in {"max_history", "llm_max_retries", "llm_max_tokens"} and value != int(value):
            raise ValueError(f"{key} 必须是整数")
        return value

    def enable_demo(self) -> None:
        """仅覆盖本次运行：无网络、无录音、无历史读写，使用内置绘制形象。"""
        self.demo_mode = True
        self.enable_voice = False
        self.persist_history = False
        self.image_engine = "sprite"
        self.frames = []

    def update_frames(self, frames: list[str]) -> None:
        """更新形象帧列表并写回 config.json，使更换在重启后仍然生效。"""
        self.frames = frames
        self._save_json(frames=frames)

    def update_image_engine(self, engine: str) -> None:
        """切换形象引擎并写回 config.json，使切换在重启后仍然生效。"""
        self.image_engine = engine
        self._save_json(image_engine=engine)

    def update_live2d_model(self, name: str) -> None:
        """切换 Live2D 模型并写回 config.json，使切换在重启后仍然生效。"""
        self.live2d_model = name
        self._save_json(live2d_model=name)

    def update_voice_hotkey(self, hotkey: str) -> None:
        """更新语音快捷键并写回 config.json，使设置重启后仍然生效。"""
        self.voice_hotkey = hotkey
        self._save_json(voice_hotkey=hotkey)

    def switch_persona(self, name: str) -> bool:
        """切换到指定人设（从 personas 预设读取），写回 config.json 并返回是否成功。"""
        preset = self.personas.get(name)
        if not preset:
            return False
        self.pet_name = name
        self.personality = preset.get("personality", self.personality)
        self.tone = preset.get("tone", self.tone)
        self._save_json(
            pet_name=self.pet_name,
            persona={"personality": self.personality, "tone": self.tone},
        )
        return True

    def add_persona(self, name: str, personality: str, tone: str) -> bool:
        """新增（或覆盖）一个人设预设，写回 config.json 并返回是否成功。"""
        name = name.strip()
        if not name:
            return False
        self.personas[name] = {"personality": personality, "tone": tone}
        self._save_json(personas=self.personas)
        return True
