"""提供者（策略）与 LLM 客户端（门面）测试，使用 mock 隔离网络。"""

import pytest

from pet.llm import LLMClient, LLMError
from pet.providers import OpenAICompatProvider, create_chat_provider


class _Delta:
    def __init__(self, content):
        self.content = content


class _Choice:
    def __init__(self, content):
        self.delta = _Delta(content)


class _Chunk:
    def __init__(self, content):
        self.choices = [_Choice(content)] if content is not None else []


class _Completions:
    def __init__(self, chunks):
        self._chunks = chunks

    def create(self, **kwargs):
        return iter(self._chunks)


class _FakeClient:
    def __init__(self, chunks):
        self.chat = type("Chat", (), {"completions": _Completions(chunks)})()


def test_stream_chat_concatenates_and_callbacks(monkeypatch):
    provider = OpenAICompatProvider("sk", "https://x", "m")
    chunks = [_Chunk("你"), _Chunk(None), _Chunk("好")]
    monkeypatch.setattr(provider, "_client", _FakeClient(chunks))

    collected = []
    result = provider.stream_chat([{"role": "user", "content": "hi"}], on_chunk=collected.append)

    assert result == "你好"
    assert collected == ["你", "好"]


def test_llm_client_wraps_error():
    class _Boom:
        def stream_chat(self, messages, on_chunk=None):
            raise RuntimeError("boom")

    client = LLMClient(_Boom())
    with pytest.raises(LLMError):
        client.chat([{"role": "user", "content": "hi"}])


def test_factory_returns_openai_compat_provider():
    from pet.config import Settings

    provider = create_chat_provider(Settings())
    assert isinstance(provider, OpenAICompatProvider)


def test_error_does_not_expose_provider_payload():
    class FailingProvider:
        def stream_chat(self, messages, on_chunk=None):
            raise RuntimeError("private-user-text and secret-token")

    with pytest.raises(LLMError) as error:
        LLMClient(FailingProvider()).chat([])
    assert "private-user-text" not in str(error.value)
    assert "secret-token" not in str(error.value)


def test_stream_closed_when_callback_fails(monkeypatch):
    class Stream:
        closed = False

        def __iter__(self):
            yield _Chunk("hi")

        def close(self):
            self.closed = True

    stream = Stream()
    provider = OpenAICompatProvider("sk", "https://x", "m")
    client = _FakeClient([])
    monkeypatch.setattr(client.chat.completions, "create", lambda **kwargs: stream)
    provider._client = client

    def fail(text):
        raise RuntimeError("callback failed")

    with pytest.raises(RuntimeError):
        provider.stream_chat([], fail)
    assert stream.closed


def test_factory_passes_request_limits(monkeypatch):
    from pet.config import Settings

    settings = Settings()
    settings.llm_timeout = 7
    settings.llm_max_retries = 0
    provider = create_chat_provider(settings)
    seen = {}

    def create_client(**kwargs):
        seen.update(kwargs)
        return _FakeClient([])

    monkeypatch.setattr("pet.providers.OpenAI", create_client)
    assert provider.stream_chat([]) == ""
    assert seen["timeout"] == 7 and seen["max_retries"] == 0
