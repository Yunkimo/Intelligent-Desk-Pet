"""应用路径解析：区分「源码运行」与「PyInstaller 打包运行」。

打包成 exe 后采用「便携式布局」——可写数据与素材统一放在 exe 所在目录：

    dist/启动桌宠/
    ├── 启动桌宠.exe      # 双击即用
    ├── _internal/        # PyInstaller 运行库（自动生成）
    ├── assets/           # 宠物素材（含 live2d/ 模型，打包脚本拷入）
    ├── config.json       # 非敏感配置（打包脚本拷入，可编辑）
    ├── data/             # 对话历史（运行时自动生成）
    └── .env              # 密钥（用户按 .env.example 自行创建，不打包）
"""

import sys
from pathlib import Path


def app_dir() -> Path:
    """应用根目录：打包后为 exe 所在目录；开发时为本项目根目录。"""
    if getattr(sys, "frozen", False):  # PyInstaller 打包运行
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent
