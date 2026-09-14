"""Live2D 模型发现测试（纯文件系统逻辑，无需启动 WebEngine）。"""

import pytest

live2d_view = pytest.importorskip("pet.live2d_view")


def test_discover_models_finds_cyrene():
    names = [m["name"] for m in live2d_view.discover_models()]
    assert "cyrene" in names


def test_cyrene_entry_and_expressions():
    cyrene = next(m for m in live2d_view.discover_models() if m["name"] == "cyrene")
    assert cyrene["entry"].endswith(".model3.json")
    assert "表情回正" in cyrene["expressions"]


def test_cyrene_swing_and_switch_removed():
    """秋千互动（拽秋千1/2/回正）与开关（开/关）已从模型删除，只保留真实表情。"""
    cyrene = next(m for m in live2d_view.discover_models() if m["name"] == "cyrene")
    assert "表情回正" in cyrene["expressions"]
    assert "开心眼" in cyrene["expressions"]
    for removed in ("拽秋千1", "拽秋千2", "拽秋千回正", "开", "关"):
        assert removed not in cyrene["expressions"]


def test_model_entry_missing_returns_none():
    assert live2d_view.model_entry("不存在的模型目录") is None
