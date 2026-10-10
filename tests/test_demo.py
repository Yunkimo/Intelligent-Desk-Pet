"""离线演示必须走真实工厂/门面/记忆链路，禁止创建在线客户端。"""

import os
import subprocess
import sys
from pathlib import Path

from pet.config import Settings
from pet.llm import LLMClient
from pet.memory import Memory
from pet.providers import DemoChatProvider, create_chat_provider


def test_offline_chat_does_not_create_network_client(tmp_path, monkeypatch):
    import pet.providers as providers

    def forbidden(**kwargs):
        raise AssertionError("演示不得创建网络客户端")

    monkeypatch.setattr(providers, "OpenAI", forbidden)
    settings = Settings()
    settings.enable_demo()
    provider = create_chat_provider(settings)
    assert isinstance(provider, DemoChatProvider)
    assert not settings.enable_voice and not settings.persist_history
    assert settings.image_engine == "sprite" and settings.frames == []
    path = tmp_path / "history.json"
    memory = Memory(path, persist=settings.persist_history)
    memory.set_system("系统提示")
    memory.add_user("你好")
    chunks = []
    answer = LLMClient(provider).chat(memory.get_messages(), chunks.append)
    memory.add_assistant(answer)
    memory.save()
    assert "你好" in answer and "离线演示" in answer
    assert "".join(chunks) == answer
    assert len(memory.get_messages()) == 3
    assert not path.exists()


def test_cli_outputs_utf8_even_with_legacy_console_encoding():
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, "scripts/demo.py"],
        cwd=root,
        env={**os.environ, "PYTHONIOENCODING": "cp1252"},
        capture_output=True,
        check=True,
        timeout=20,
    )
    assert "离线演示" in result.stdout.decode("utf-8")
