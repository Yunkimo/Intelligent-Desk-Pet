"""配置加载：合并 .env（密钥）与 config.json（非敏感配置）。"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录（pet/ 的上一级）
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    """应用配置的统一入口，各模块从这里取值。"""

    def __init__(self) -> None:
        load_dotenv(BASE_DIR / ".env")

        # —— 来自 .env 的密钥/模型配置 ——
        self.llm_api_key: str = os.getenv("LLM_API_KEY", "").strip()
        self.llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.deepseek.com").strip()
        self.llm_model: str = os.getenv("LLM_MODEL", "deepseek-chat").strip()

        # —— 来自 config.json 的非敏感配置 ——
        self._load_json()

    def _load_json(self) -> None:
        path = BASE_DIR / "config.json"
        data: dict = {}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                data = {}

        self.pet_name: str = data.get("pet_name", "小萌")
        persona = data.get("persona", {})
        self.personality: str = persona.get("personality", "活泼可爱")
        self.tone: str = persona.get("tone", "口语化、简短俏皮")

        self.frames: list[str] = data.get("frames", [])
        self.sprite_size: int = int(data.get("sprite_size", 180))

        self.whisper_model: str = data.get("whisper_model", "base")
        self.tts_voice: str = data.get("tts_voice", "zh-CN-XiaoyouNeural")
        self.tts_rate: str = data.get("tts_rate", "+10%")
        self.tts_pitch: str = data.get("tts_pitch", "+20Hz")
        self.enable_voice: bool = bool(data.get("enable_voice", True))

        self.max_history: int = int(data.get("max_history", 20))
        self.max_record_secs: float = float(data.get("max_record_secs", 15))
        self.bubble_timeout_ms: int = int(data.get("bubble_timeout_ms", 8000))
        self.persist_history: bool = bool(data.get("persist_history", True))

        # 路径统一解析为绝对路径
        self.assets_dir: Path = BASE_DIR / data.get("assets_dir", "assets")
        self.history_path: Path = BASE_DIR / data.get("history_path", "data/history.json")
