"""提交规范检查器的接受/拒绝边界。"""

import pytest

from scripts.check_commit import valid_title


@pytest.mark.parametrize(
    "title",
    ["feat: 添加离线演示", "fix(config): 修复保存失败", "Merge pull request #1 from team/topic"],
)
def test_valid_commit_title(title):
    assert valid_title(title)


@pytest.mark.parametrize("title", ["update", "feat: add demo", "fix: ", "feat: " + "字" * 100])
def test_invalid_commit_title(title):
    assert not valid_title(title)
