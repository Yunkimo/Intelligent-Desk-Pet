"""一键打包：生成 exe，并把素材 / 配置 / 文档拷到 exe 旁（便携式布局）。

用法（Windows，需已安装运行依赖与 pyinstaller）：
    .venv\\Scripts\\python scripts\\build_exe.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_NAME = "启动桌宠"
DIST = ROOT / "dist" / APP_NAME

# 需随 exe 一起放置的外部文件；密钥 .env 由用户自行创建，绝不打包
EXTERNAL = ["assets", "config.json", ".env.example", "LICENSE", "README.md", "CHANGELOG.md", "docs"]


def _copy(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst) if src.is_dir() else dst.unlink()
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main() -> int:
    subprocess.check_call(
        [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", str(ROOT / "deskpet.spec")],
        cwd=ROOT,
    )

    DIST.mkdir(parents=True, exist_ok=True)
    for name in EXTERNAL:
        src = ROOT / name
        if not src.exists():
            print(f"[build] 跳过（不存在）：{name}")
            continue
        _copy(src, DIST / name)

    exe = DIST / f"{APP_NAME}.exe"
    if exe.exists():
        print(f"\n打包完成：{exe}")
        print("把整个 dist/启动桌宠/ 目录拷给别人即可运行（首次运行会联网下载 whisper 模型）。")
        return 0
    print("\n打包失败：未找到生成的可执行文件。", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
