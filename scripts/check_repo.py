"""检查已暂存文件：屏蔽凭据/运行产物；仅输出路径，绝不输出命中内容。"""

import re
import subprocess
from pathlib import PurePosixPath

SECRET = re.compile(rb"(?:sk-[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")


def main() -> int:
    paths = subprocess.check_output(["git", "ls-files", "-z"]).decode("utf-8").split("\0")
    failures = []
    for name in filter(None, paths):
        path = PurePosixPath(name)
        if (
            (path.name.startswith(".env") and path.name != ".env.example")
            or path.suffix.lower() in {".pyc", ".log", ".exe", ".mp3"}
            or any(part in {".venv", "__pycache__", "data", "dist", "build"} for part in path.parts)
        ):
            failures.append(f"不应跟踪运行文件：{name}")
        if path.suffix in {".py", ".json", ".md", ".yml", ".yaml", ".txt"}:
            content = subprocess.check_output(["git", "show", f":{name}"])
            if SECRET.search(content):
                failures.append(f"疑似凭据，请人工复核：{name}")
    print("\n".join(failures) if failures else "Repository hygiene passed (tracked index).")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
