# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包脚本：把桌宠打包成 Windows exe（onedir 便携式布局）。

构建（需先安装 pyinstaller，见 requirements-dev.txt）：
    .venv\\Scripts\\python -m PyInstaller --noconfirm deskpet.spec

产物：dist/启动桌宠/启动桌宠.exe。配合 scripts/build_exe.py 把素材与配置拷到 exe 旁。
"""

import os

from PyInstaller.utils.hooks import collect_all, collect_submodules

# 默认保留控制台（便于看报错与 whisper 首次下载进度）；
# 想生成无控制台窗口的干净 GUI 版，设置环境变量 DESKPET_CONSOLE=0
CONSOLE = os.environ.get("DESKPET_CONSOLE", "1") == "1"

# 含原生二进制 / 数据文件的三方库，需整体收集，否则打包后缺 DLL / 资源
_BIN_PKGS = [
    "ctranslate2",   # faster-whisper 推理后端
    "av",            # faster-whisper 音频解码（FFmpeg 库）
    "onnxruntime",   # faster-whisper 的 VAD
    "tokenizers",    # faster-whisper 分词数据
    "sounddevice",   # 麦克风录音（PortAudio DLL）
]

datas, binaries, hiddenimports = [], [], []
for _pkg in _BIN_PKGS:
    try:
        _d, _b, _h = collect_all(_pkg)
    except Exception as _exc:  # noqa: BLE001
        print(f"[spec] collect_all({_pkg}) 失败：{_exc}")
        continue
    datas += _d
    binaries += _b
    hiddenimports += _h

# 懒加载的纯 Python 依赖，显式声明子模块以防静态分析遗漏
hiddenimports += collect_submodules("faster_whisper")
hiddenimports += collect_submodules("pynput")  # 全局语音快捷键（平台相关后端 _win32 等）

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="启动桌宠",
    debug=False,
    strip=False,
    upx=False,
    console=CONSOLE,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="启动桌宠",
)
