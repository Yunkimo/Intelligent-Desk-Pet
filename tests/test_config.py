"""Settings 配置加载测试。"""

import json

import pytest

from pet.config import Settings


def test_defaults_when_env_unset(monkeypatch):
    for key in ("LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL"):
        monkeypatch.delenv(key, raising=False)
    s = Settings()
    assert s.llm_base_url == "https://api.deepseek.com"
    assert s.llm_model == "deepseek-chat"
    assert s.llm_api_key == ""


def test_env_override(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("LLM_MODEL", "my-model")
    s = Settings()
    assert s.llm_api_key == "sk-test"
    assert s.llm_base_url == "https://example.com/v1"
    assert s.llm_model == "my-model"


def test_config_json_fields():
    s = Settings()
    assert s.pet_name in ("昔涟", "小萌")  # 运行时可通过「切换人设」更改
    assert s.image_engine in ("live2d", "sprite")  # 运行时可通过「切换图片」在两种引擎间切换
    assert s.live2d_model == "cyrene"
    assert s.whisper_model == "base"
    assert s.tts_voice == "zh-CN-XiaoyouNeural"
    assert s.max_history > 0


@pytest.mark.parametrize(
    "key,value",
    [
        ("max_history", 0),
        ("max_history", 1.5),
        ("max_record_secs", -1),
        ("llm_timeout", "30"),
        ("llm_timeout", float("inf")),
        ("llm_max_retries", True),
        ("llm_max_tokens", 0),
        ("llm_temperature", 3),
    ],
)
def test_invalid_limits_fail_with_field_name(tmp_path, monkeypatch, key, value):
    monkeypatch.setattr("pet.config.BASE_DIR", tmp_path)
    (tmp_path / "config.json").write_text(json.dumps({key: value}), encoding="utf-8")
    with pytest.raises(ValueError, match=key):
        Settings()


def test_save_preserves_unrelated_fields(tmp_path, monkeypatch):
    monkeypatch.setattr("pet.config.BASE_DIR", tmp_path)
    path = tmp_path / "config.json"
    path.write_text('{"custom": 42}', encoding="utf-8")
    settings = Settings()
    settings.update_voice_hotkey("ctrl+y")
    assert json.loads(path.read_text()) == {"custom": 42, "voice_hotkey": "ctrl+y"}
