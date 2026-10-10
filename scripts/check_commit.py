"""检查新提交标题；合并提交保留 Git 生成的标题，不重写既有历史。"""

import re
import sys
from pathlib import Path

PATTERN = re.compile(
    r"^(feat|fix|refactor|test|docs|ci|chore|style|perf|build|revert)(\([a-z0-9_-]+\))?!?: .+"
)


def valid_title(title: str) -> bool:
    if title.startswith(("Merge ", 'Revert "')):
        return True
    return bool(
        PATTERN.fullmatch(title) and re.search(r"[\u4e00-\u9fff]", title) and len(title) <= 100
    )


def main() -> int:
    title = Path(sys.argv[1]).read_text(encoding="utf-8-sig").splitlines()[0]
    if valid_title(title):
        return 0
    print("提交标题须为 type(scope): 中文描述，最多 100 字符；一次提交只表达一项职责。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
