# 更新日志

本项目遵循[语义化版本](https://semver.org/lang/zh-CN/)与 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 规范。

## [1.1.0] - 2026-09-14

### 新增

- 桌宠人设升级为「昔涟」（《崩坏：星穹铁道》角色）：自称「人家」、称呼主人「伙伴」、句尾常带「♪」。
- 支持 GIF / WebP 动图形象播放（QMovie），形象按宽高比等比缩放、不再拉伸变形。
- 右键菜单「更换形象…」：运行时选择本地图片即时换装，并自动写入 `config.json`（重启后保留）。
- 右键菜单「退出」：无边框窗口也能正常关闭桌宠。
- 新增 `启动桌宠.bat`，双击即可启动。

### 修复

- 单帧 WebP 改走 QPixmap 平滑缩放，修复大图缩小时锯齿、发虚的问题。
- 更换形象时自动裁掉四周透明边，形象更贴合、显示更大。

### 变更

- 默认形象改为高清透明「昔涟」立绘（`assets/cyrene.webp`，1121×675）。
- 依赖新增 `Pillow`，用于图片格式归一化（规避本机 Qt 读取部分 PNG 报 `libpng error` 的问题）。

## [1.0.0] - 2026-09-14

### 新增

- 初始版本：无边框 / 置顶 / 透明的桌面宠物窗口，支持拖拽移动、点击唤起输入框。
- LLM 文字对话（DeepSeek），气泡流式显示。
- 语音合成（edge-tts）与语音识别（faster-whisper），支持双向语音对话。
- 人设系统与跨会话记忆。
- 设计文档、用户手册、单元测试与 CI 流水线。

[1.1.0]: https://github.com/Yunkimo/Intelligent-Desk-Pet/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Yunkimo/Intelligent-Desk-Pet/releases/tag/v1.0.0
