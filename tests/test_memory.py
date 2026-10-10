"""Memory 会话历史测试。"""

import json

import pytest

from pet.memory import Memory


def test_add_and_order():
    m = Memory("unused.json", max_turns=10, persist=False)
    m.set_system("你是宠物")
    m.add_user("你好")
    m.add_assistant("你好呀")
    msgs = m.get_messages()
    assert msgs[0] == {"role": "system", "content": "你是宠物"}
    assert msgs[1] == {"role": "user", "content": "你好"}
    assert msgs[2] == {"role": "assistant", "content": "你好呀"}


def test_clear_history_keeps_system():
    m = Memory("unused.json", max_turns=10, persist=False)
    m.set_system("你是宠物")
    m.add_user("你好")
    m.add_assistant("你好呀")
    m.clear_history()
    assert m.get_messages() == [{"role": "system", "content": "你是宠物"}]


def test_trim_keeps_recent_turns():
    m = Memory("unused.json", max_turns=2, persist=False)
    m.set_system("sys")
    for i in range(5):
        m.add_user(f"u{i}")
        m.add_assistant(f"a{i}")
    msgs = m.get_messages()
    assert msgs[0]["role"] == "system"
    rest = msgs[1:]
    assert len(rest) == 4  # 最近 2 轮
    assert rest[0]["content"] == "u3"
    assert rest[-1]["content"] == "a4"


def test_persist_roundtrip(tmp_path):
    path = tmp_path / "data" / "history.json"
    m = Memory(path, max_turns=10, persist=True)
    m.set_system("sys")
    m.add_user("hi")
    m.add_assistant("hello")
    m.save()

    m2 = Memory(path, persist=True)
    m2.set_system("sys")  # 系统指令从当前人设重新建立，不信任磁盘中的 system 消息
    msgs = m2.get_messages()
    assert msgs[1]["content"] == "hi"
    assert msgs[2]["content"] == "hello"


def test_loaded_history_filters_invalid_entries_and_system(tmp_path):
    path = tmp_path / "history.json"
    path.write_text(
        json.dumps(
            {
                "messages": [
                    None,
                    "bad",
                    {"role": "system", "content": "untrusted"},
                    {"role": "tool", "content": "bad"},
                    {"role": "user", "content": 5},
                    {"role": "user", "content": "old"},
                    {"role": "assistant", "content": "old"},
                    {"role": "user", "content": "new"},
                    {"role": "assistant", "content": "new"},
                ]
            }
        ),
        encoding="utf-8",
    )
    memory = Memory(path, max_turns=1)
    assert memory.get_messages() == [
        {"role": "user", "content": "new"},
        {"role": "assistant", "content": "new"},
    ]


@pytest.mark.parametrize("turns", [0, -1, True, 1.5])
def test_invalid_history_limit(turns):
    with pytest.raises(ValueError):
        Memory("unused.json", max_turns=turns, persist=False)
