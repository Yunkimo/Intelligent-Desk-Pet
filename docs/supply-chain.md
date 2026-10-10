# 开源来源、许可证与供应链

## 1. 授权范围

[LICENSE](../LICENSE) 中 MIT 适用于本仓库有权授权的自有代码，不能自动覆盖依赖、模型、角色形象或整个打包程序。“课程用途”本身不等于取得再分发授权。

PyQt 官方说明采用 GPL v3 / 商业双重许可，见 [Riverbank](https://www.riverbankcomputing.com/software/pyqt/intro)。分发时需核查相应条款，不将源码 MIT 标识当成整个软件包的授权结论。

## 2. Python 直接依赖

| 依赖 | 上游项目 | 用途 / 许可证线索 |
|---|---|---|
| PyQt6 / PyQt6-WebEngine | Riverbank | GUI/WebEngine，GPL v3 或商业 |
| openai | openai/openai-python | API 客户端，Apache-2.0 |
| edge-tts | rany2/edge-tts | 在线合成，LGPL-3.0 |
| faster-whisper | SYSTRAN/faster-whisper | ASR，MIT |
| sounddevice | spatialaudio/python-sounddevice | 录音，MIT |
| python-dotenv | theskumar/python-dotenv | 配置，BSD-3-Clause |
| numpy | numpy/numpy | 数组，BSD-3-Clause；另有捆绑组件条款 |
| Pillow | python-pillow/Pillow | 图像，HPND；另有捆绑组件条款 |
| pynput | mosestern/pynput | 快捷键，LGPL-3.0 |

均通过 PyPI 安装。具体版本/许可元数据见 [environment.json](evidence/environment.json) 及 wheel 的 LICENSE，表格不是所有传递依赖的完整法律审查。开发工具另有 Ruff、pytest、pytest-cov、pre-commit、pip-audit、PyInstaller，录屏使用 imageio-ffmpeg。

## 3. 内嵌前端与素材

| 文件/目录 | 文件或历史证据 | 状态 |
|---|---|---|
| pixi.min.js | 文件头声明 pixi.js 7.4.3 / MIT | 保留文件头并记录校验和 |
| cubism4.min.js | 内嵌 pixi-live2d-display / Cubism 代码 | 需核对各内嵌组件，不只看插件 MIT |
| live2dcubismcore.min.js | 文件头声明 Live2D 专有许可链接 | 发布前按条款核查 |
| assets/live2d/cyrene/ | 旧 README 称来自 Cyrene-Agent，缺准确 URL/版本/授权凭据 | **待补证据**，不宣称可公开再分发 |
| assets/custom.gif、custom.webp | 仓库历史中的角色图片 | **待补来源和授权** |
| 内置猫 | pet/sprite.py 绘制 | 离线演示使用，不加载第三方模型 |

文件 SHA-256 见 [asset-hashes.json](evidence/asset-hashes.json)，只识别审查对象，不证明来源或授权。团队应补上游链接、版本、作者、许可证全文和修改说明；必要时用明确许可的素材替换。

## 4. 复现与更新

requirements.txt / requirements-dev.txt 的版本下限**不能保证完全复现**。另提供 [Windows Python 3.13 版本快照](../requirements-lock-win-py313.txt)，含测试/开发/录屏工具；仅用于相同平台，不是跨平台或哈希锁文件。

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements-lock-win-py313.txt
python -m pip check
python -m pip_audit --format=json --output=reports/pip-audit.json
```

升级依赖应独立提交并重跑 CI。CI 按版本范围解析，以检测升级兼容性；审计不覆盖全部捆绑组件。不要从不明来源安装 SDK 或把密钥写进下载地址。
