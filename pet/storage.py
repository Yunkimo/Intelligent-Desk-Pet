"""JSON 文件边界：验证顶层结构，使用同目录临时文件原子替换。"""

import json
import os
import tempfile
from pathlib import Path


def read_object(path: Path) -> dict:
    """不存在返回空对象；损坏或类型错误向调用者报告，不静默覆盖。"""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} 顶层必须是 JSON 对象")
    return data


def write_object(path: Path, data: dict) -> None:
    """失败时保留原文件并清理临时文件；不提供跨进程并发事务。"""
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, suffix=".tmp", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
