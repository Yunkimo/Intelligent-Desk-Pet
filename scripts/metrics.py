"""只读 Git/AST 度量，排除第三方模型与运行时；不把行数等同绩效。"""

import argparse
import ast
import json
import platform
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT).decode("utf-8")


def source_metrics(ref: str | None) -> dict:
    if ref:
        files = git("ls-tree", "-r", "--name-only", ref).splitlines()
    else:
        files = [
            p.relative_to(ROOT).as_posix()
            for folder in ("pet", "tests")
            for p in (ROOT / folder).glob("*.py")
        ]
    counts = {"pet_files": 0, "pet_lines": 0, "test_functions": 0, "provider_implementations": 0}
    largest = (0, "")
    for name in files:
        if not name.endswith(".py") or not name.startswith(("pet/", "tests/")):
            continue
        text = git("show", f"{ref}:{name}") if ref else (ROOT / name).read_text(encoding="utf-8")
        tree = ast.parse(text)
        if name.startswith("pet/"):
            lines = len(text.splitlines())
            counts["pet_files"] += 1
            counts["pet_lines"] += lines
            largest = max(largest, (lines, name))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and any(
                    isinstance(b, ast.Name) and b.id == "ChatProvider" for b in node.bases
                ):
                    counts["provider_implementations"] += 1
        else:
            counts["test_functions"] += sum(
                isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and n.name.startswith("test_")
                for n in ast.walk(tree)
            )
    return {**counts, "largest_module": largest[1], "largest_module_lines": largest[0]}


def contributions() -> dict:
    authors = defaultdict(
        lambda: {"patches": 0, "categories": defaultdict(lambda: {"added": 0, "deleted": 0})}
    )
    author = ""
    for line in git("log", "HEAD", "--no-merges", "--format=@@%aN", "--numstat").splitlines():
        if line.startswith("@@"):
            author = line[2:]
            authors[author]["patches"] += 1
        elif line and author:
            added, deleted, name = line.split("\t", 2)
            if added == "-" or name.startswith("assets/"):
                continue
            category = (
                "test"
                if name.startswith("tests/")
                else "docs"
                if name.endswith(".md")
                else "code"
                if name.endswith(".py")
                else "engineering"
            )
            item = authors[author]["categories"][category]
            item["added"] += int(added)
            item["deleted"] += int(deleted)
    return dict(authors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default="c1f0c80", help="本轮质量改进前的远端提交")
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "metrics.json")
    args = parser.parse_args()
    result = {
        "generated_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "head": git("rev-parse", "HEAD").strip(),
        "baseline": git("rev-parse", args.baseline).strip(),
        "working_tree_dirty": bool(git("status", "--porcelain")),
        "environment": {
            "python": platform.python_version(),
            "os": platform.platform(),
            "cpu": platform.processor(),
        },
        "before": source_metrics(args.baseline),
        "after_worktree": source_metrics(None),
        "contributors_committed_only": contributions(),
        "method": "物理行数含注释/空行；test_functions 不展开参数化；patch 排除 merge；贡献排除 assets 与二进制，不含未提交修改；作者名按 Git mailmap 归并。",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Metrics written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
