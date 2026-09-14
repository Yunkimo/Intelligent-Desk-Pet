# Intelligent Desk Pet · 智能桌面宠物

[![CI](https://github.com/Yunkimo/Intelligent-Desk-Pet/actions/workflows/ci.yml/badge.svg)](https://github.com/Yunkimo/Intelligent-Desk-Pet/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

一个 Windows 桌面宠物：可拖拽、置顶、透明的可爱形象（支持 **Live2D 动态模型** 与图片/GIF 两种引擎），支持 **文字聊天** 和 **双向语音对话**（你说它听、它说给你听），带人设与跨会话记忆。

- **GUI**：PyQt6（无边框 / 置顶 / 透明窗口）
- **形象**：Live2D（Cubism 4）动态模型，或图片 / GIF 精灵，`config.json` 一键切换
- **对话**：DeepSeek（OpenAI 兼容协议，可换任意国内 API）
- **语音合成 TTS**：edge-tts（免费、无需密钥、可爱动漫音色）
- **语音识别 ASR**：本地 faster-whisper（离线）

## 快速开始

### 1. 安装依赖

建议用虚拟环境：

```bash
python -m venv .venv
# Windows 激活：
.venv\Scripts\activate
```

然后安装：

```bash
pip install -r requirements.txt
```

> 首次运行 ASR 会自动下载 faster-whisper 模型（约 100~500 MB）。若下载缓慢，可设置 HuggingFace 镜像后重试：
> ```bash
> set HF_ENDPOINT=https://hf-mirror.com
> ```

### 2. 配置密钥

```bash
copy .env.example .env
```

编辑 `.env`，填入你的 DeepSeek API Key（其它 OpenAI 兼容 API 改 `LLM_BASE_URL` / `LLM_MODEL` 即可）：

```
LLM_API_KEY=sk-xxxx
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

### 3. 运行

```bash
python main.py
```

### 4.（可选）冒烟测试

```bash
python scripts/smoke_test.py llm   # 验证 DeepSeek 连通
python scripts/smoke_test.py tts   # 验证语音合成
```

## 打包成 exe（可选）

不想装 Python 环境时，可把桌宠打包成免安装的 Windows 可执行程序（双击即用，无需 Python / 虚拟环境）：

```bash
# 一次性安装打包工具
pip install -r requirements-dev.txt
# 生成 dist/启动桌宠/启动桌宠.exe（含素材、配置，便携式）
python scripts/build_exe.py
```

或直接双击 `打包exe.bat`（自动装 PyInstaller 并打包）。

产物在 `dist/启动桌宠/`，把整个目录拷到任意电脑即可运行：

- `启动桌宠.exe` —— 双击启动；
- `config.json` —— 可编辑的非敏感配置（人设 / 形象 / 音色等）；
- `assets/` —— 宠物素材（含 Live2D 模型）；
- `.env` —— 密钥，按 `.env.example` 自行创建后填入（不随程序打包）。

> 说明：首次语音识别会自动联网下载 whisper 模型（约 100~500 MB）；打包版默认带控制台窗口以便查看进度，设置环境变量 `DESKPET_CONSOLE=0` 再打包可隐藏控制台。

## 使用说明

- **拖拽**：按住宠物拖动可移动位置
- **点击**：点宠物唤出输入框，回车发送；再点收起
- **说话**：点输入框右侧 🎤 开始录音（变 ⏹），再点停止即转写并发送
- **回复**：气泡流式显示，宠物同时用语音播报
- **记忆**：对话历史保存在 `data/history.json`，重启后仍在（可在 `config.json` 关闭）
- **右键菜单**：切换图片（选图片自动切到图片/动图引擎）/ 切换人设 / 退出
- **Live2D**：右键「逗一下 ♪」触发随机动作、「切换表情」换表情；说话播报时模型自动做动作，待机动作循环；图片模式下可「切换为 Live2D 动态形象」切回
- **多模型**：右键「切换模型」在已导入的 Live2D 模型间切换；「添加 Live2D 模型…」弹出导入窗口，选择本地 Cubism 4 模型文件夹即拷入 `assets/live2d/` 并切换

## 自定义

| 想改什么 | 位置 |
|---|---|
| 宠物名字 / 人设 | `config.json` 的 `pet_name`、`persona` |
| 宠物形象 | 图片放进 `assets/`，更新 `config.json` 的 `frames`（见 `assets/README.md`） |
| 形象引擎 | `config.json` 的 `image_engine`：`live2d`（动态模型）或 `sprite`（图片/动图） |
| Live2D 模型 | `config.json` 的 `live2d_model`，或右键「切换模型」/「添加 Live2D 模型…」 |
| 音色 | `config.json` 的 `tts_voice` / `tts_rate` / `tts_pitch` |
| 语音识别精度 | `config.json` 的 `whisper_model`（`base`/`small`/`medium`） |
| 关闭语音播报 | `config.json` 的 `enable_voice` 设为 `false` |
| LLM 模型 / 地址 | `.env` 的 `LLM_MODEL` / `LLM_BASE_URL` |

## 目录结构

```
main.py            入口
pet/               应用代码（config/paths/window/avatar/sprite/bubble/llm/asr/tts/worker/memory/persona/live2d_view）
assets/            宠物素材（live2d/ 为 Cubism 模型与前端运行时）
scripts/           冒烟测试脚本、打包脚本（build_exe.py）
deskpet.spec       PyInstaller 打包配置
打包exe.bat        一键打包入口
config.json        非敏感配置
.env               密钥（不提交）
```

## 架构与设计模式

系统按「配置 / 引擎（后端）/ 线程 / UI / 记忆」分层，后端与前端解耦。重构中应用了 5 种设计模式：

- **适配器 Adapter**：`LLMClient` / `TTSEngine` / `ASREngine` 隔离 OpenAI、edge-tts、faster-whisper 三方库
- **策略 Strategy + 工厂 Factory**：`ChatProvider` / `create_chat_provider` 抽象 LLM 提供者；`Avatar` / `create_avatar` 抽象形象引擎（图片精灵 / Live2D），可换任意后端
- **观察者 Observer**：Qt 信号/槽让后台线程与 UI 解耦，UI 永不阻塞
- **外观 Facade**：`PetWindow` 对外提供极简操作

详见 [docs/design.md](docs/design.md)（含 UML 图与重构前后量化分析）。

## 文档

- [设计文档（架构 + 设计模式 + UML）](docs/design.md)
- [用户手册](docs/user-manual.md)
- [测试文档](docs/testing.md)
- [信息安全设计](docs/security.md)

## 开源许可证与供应链

- 本项目采用 **MIT License**（见 [LICENSE](LICENSE)）。
- 核心依赖（均来自 PyPI 官方发布的开源项目）：

| 依赖 | 许可证 | 用途 |
|---|---|---|
| PyQt6 | GPL-3.0 / 商业 | GUI |
| PyQt6-WebEngine | GPL-3.0 / 商业 | Live2D 渲染（可选） |
| openai | Apache-2.0 | LLM 调用 |
| edge-tts | LGPL-3.0 | 语音合成 |
| faster-whisper | MIT | 语音识别 |
| sounddevice | MIT | 录音 |
| python-dotenv | BSD-3-Clause | 配置 |
| numpy | BSD-3-Clause | 数值处理 |

### Live2D 前端运行时与模型

`assets/live2d/` 内含渲染 Live2D 模型所需的前端运行时与第三方模型：

| 组件 | 许可证 | 说明 |
|---|---|---|
| pixi.js | MIT | 2D 渲染引擎 |
| pixi-live2d-display | MIT | Live2D 渲染插件（Cubism 4） |
| Cubism Core（live2dcubismcore.min.js） | Live2D 专有许可 | 模型运行时核心 |

> ⚠️ **模型版权**：`assets/live2d/cyrene/` 为「昔涟」角色的第三方 Live2D 模型，提取自开源项目 Cyrene-Agent，**非本仓库原创**。本项目仅用于课程设计 / 学习演示；如需商用或公开分发，请自行确认角色形象版权与模型使用授权。

## 常见问题

- **听不到/说不了话**：确认麦克风权限已允许，且首次已下载 whisper 模型。
- **LLM 报错**：检查 `.env` 里 `LLM_API_KEY` 是否正确、`LLM_BASE_URL` 是否可达。
- **音色想更像某角色**：`edge-tts` 只能在「可爱/动漫感」范围内调；若要克隆某个具体角色音色，需另接 `GPT-SoVITS`（见方案文档，暂未内置）。
