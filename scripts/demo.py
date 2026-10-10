"""无图形界面、无网络演示：python scripts/demo.py [输入文本]。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pet.config import Settings  # noqa: E402
from pet.llm import LLMClient  # noqa: E402
from pet.memory import Memory  # noqa: E402
from pet.persona import build_system_prompt  # noqa: E402
from pet.providers import create_chat_provider  # noqa: E402


def main() -> int:
    settings = Settings()
    settings.enable_demo()
    memory = Memory(settings.history_path, persist=False)
    memory.set_system(build_system_prompt(settings))
    memory.add_user(" ".join(sys.argv[1:]) or "你好，介绍一下离线演示")
    client = LLMClient(create_chat_provider(settings))
    reply = client.chat(
        memory.get_messages(), on_chunk=lambda part: print(part, end="", flush=True)
    )
    memory.add_assistant(reply)
    print()
    return 0 if reply and len(memory.get_messages()) == 3 else 1


if __name__ == "__main__":
    raise SystemExit(main())
