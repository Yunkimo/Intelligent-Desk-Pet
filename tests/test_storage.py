"""文件边界与故障注入：防止写入失败破坏原数据。"""

import json

import pytest

from pet.storage import read_object, write_object


def test_roundtrip_and_missing(tmp_path):
    path = tmp_path / "nested" / "config.json"
    assert read_object(path) == {}
    write_object(path, {"名字": "小萌"})
    assert read_object(path) == {"名字": "小萌"}


@pytest.mark.parametrize("content", ["[]", "null", "1", "{broken"])
def test_reject_invalid_object(tmp_path, content):
    path = tmp_path / "config.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        read_object(path)


def test_failed_replace_preserves_original(tmp_path, monkeypatch):
    import pet.storage as storage

    path = tmp_path / "config.json"
    path.write_text('{"old": true}', encoding="utf-8")

    def fail(*args):
        raise PermissionError("模拟文件被占用")

    monkeypatch.setattr(storage.os, "replace", fail)
    with pytest.raises(PermissionError):
        write_object(path, {"new": True})
    assert json.loads(path.read_text()) == {"old": True}
    assert list(tmp_path.iterdir()) == [path]
