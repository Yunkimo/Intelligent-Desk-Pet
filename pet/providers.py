"""LLM 提供者抽象：策略模式（Strategy）+ 简单工厂（Simple Factory）。

把「调用哪家 LLM」抽象成策略，便于在不改上层代码的前提下切换
DeepSeek / 通义 / 智谱 / Moonshot 等任意 OpenAI 兼容服务。
"""

from abc import ABC, abstractmethod
from collections.abc import Callable

from openai import OpenAI

from .config import Settings


class ChatProvider(ABC):
    """LLM 对话提供者接口（策略）。"""

    @abstractmethod
    def stream_chat(
        self, messages: list[dict], on_chunk: Callable[[str], None] | None = None
    ) -> str:
        """流式对话。on_chunk(str) 每收到一个增量被调用；返回完整文本。"""


class OpenAICompatProvider(ChatProvider):
    """OpenAI 兼容协议实现（DeepSeek 等）。客户端惰性创建，避免未配密钥时启动即报错。"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        *,
        timeout: float = 30,
        max_retries: int = 1,
        temperature: float = 0.9,
        max_tokens: int = 1024,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client: OpenAI | None = None

    def _get_client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=self.max_retries,
            )
        return self._client

    def stream_chat(self, messages: list[dict], on_chunk=None) -> str:
        stream = self._get_client().chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        parts: list[str] = []
        try:
            for chunk in stream:
                if not chunk.choices:
                    continue
                content = getattr(chunk.choices[0].delta, "content", None)
                if content:
                    parts.append(content)
                    if on_chunk is not None:
                        on_chunk(content)
        finally:
            close = getattr(stream, "close", None)
            if close is not None:
                close()
        return "".join(parts)


class DemoChatProvider(ChatProvider):
    """确定性离线策略，用于课堂演示与集成测试，不模拟真实模型能力。"""

    def stream_chat(
        self, messages: list[dict], on_chunk: Callable[[str], None] | None = None
    ) -> str:
        text = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "你好")
        reply = (
            f"【离线演示】收到：{text[:80]}。我可以展示聊天与记忆流程；真实智能回答需配置在线服务。"
        )
        for start in range(0, len(reply), 8):
            if on_chunk is not None:
                on_chunk(reply[start : start + 8])
        return reply


def create_chat_provider(settings: Settings) -> ChatProvider:
    """简单工厂：按运行配置选择在线或离线策略。"""
    if settings.demo_mode:
        return DemoChatProvider()
    return OpenAICompatProvider(
        settings.llm_api_key,
        settings.llm_base_url,
        settings.llm_model,
        timeout=settings.llm_timeout,
        max_retries=settings.llm_max_retries,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
    )
