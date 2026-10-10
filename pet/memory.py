"""会话历史：内存维护 + 本地 JSON 持久化（跨会话记忆）。"""

from pathlib import Path

from .storage import read_object, write_object


class Memory:
    """维护 message 列表（含 system），限制最近 N 轮，可选持久化。"""

    def __init__(self, history_path: Path, max_turns: int = 20, persist: bool = True) -> None:
        self.history_path = Path(history_path)
        if isinstance(max_turns, bool) or not isinstance(max_turns, int) or max_turns < 1:
            raise ValueError("max_turns 必须是正整数")
        self.max_turns = max_turns
        self.persist = persist
        self.messages: list[dict] = []
        self._load()

    def _load(self) -> None:
        if not self.persist or not self.history_path.exists():
            self.messages = []
            return
        try:
            data = read_object(self.history_path)
            msgs = data.get("messages", [])
            self.messages = [
                {"role": m["role"], "content": m["content"]}
                for m in (msgs if isinstance(msgs, list) else [])
                if isinstance(m, dict)
                and m.get("role") in ("user", "assistant")
                and isinstance(m.get("content"), str)
            ]
            self._trim()
        except (OSError, ValueError):
            self.messages = []

    def set_system(self, prompt: str) -> None:
        """替换系统提示词（放在列表最前）。"""
        self.messages = [m for m in self.messages if m.get("role") != "system"]
        self.messages.insert(0, {"role": "system", "content": prompt})

    def clear_history(self) -> None:
        """清空对话历史，仅保留系统提示词（切换人设时避免旧人设语气残留）。"""
        self.messages = [m for m in self.messages if m.get("role") == "system"]

    def add_user(self, text: str) -> None:
        self.messages.append({"role": "user", "content": text})

    def add_assistant(self, text: str) -> None:
        self.messages.append({"role": "assistant", "content": text})
        self._trim()

    def _trim(self) -> None:
        system = [m for m in self.messages if m.get("role") == "system"]
        rest = [m for m in self.messages if m.get("role") != "system"]
        limit = self.max_turns * 2  # 一轮 = user + assistant
        if len(rest) > limit:
            rest = rest[-limit:]
        self.messages = system + rest

    def get_messages(self) -> list[dict]:
        return [dict(m) for m in self.messages]

    def save(self) -> None:
        if not self.persist:
            return
        write_object(self.history_path, {"messages": self.messages})
