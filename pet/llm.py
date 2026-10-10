"""LLM 客户端：对话门面（上下文），持有一个 ChatProvider 策略。纯 Python，不依赖 Qt。"""

from .providers import ChatProvider


class LLMError(Exception):
    """统一的 LLM 调用异常，便于 UI 提示。"""


class LLMClient:
    def __init__(self, provider: ChatProvider) -> None:
        self.provider = provider

    def chat(self, messages: list[dict], on_chunk=None) -> str:
        """流式对话。on_chunk(str) 每收到一个增量被调用；返回完整文本。"""
        try:
            return self.provider.stream_chat(messages, on_chunk=on_chunk)
        except LLMError:
            raise
        except Exception as exc:  # noqa: BLE001 - 统一包装为 LLMError
            # SDK 错误可能包含请求地址、响应体或认证片段，不直接显示给用户。
            raise LLMError("对话服务暂时不可用，请检查网络和模型配置后重试。") from exc
