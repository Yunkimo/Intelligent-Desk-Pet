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


def test_cyrene_hides_non_expression_items():
    cyrene = next(m for m in live2d_view.discover_models() if m["name"] == "cyrene")
    for hidden in ("拽秋千1", "拽秋千2", "拽秋千回正", "开", "关"):
        assert hidden not in cyrene["expressions"]


def test_model_entry_missing_returns_none():
    assert live2d_view.model_entry("不存在的模型目录") is None
