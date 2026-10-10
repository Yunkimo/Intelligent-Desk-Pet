# 演示与复现

## 离线演示（已提供）

- [运行截图](images/offline-demo.png)
- [真实窗口录像 MP4](images/offline-demo.mp4)：约 11 秒，无音轨，展示两次输入、后台回复与气泡，来自程序实际渲染，不是 UI 设计稿。

```powershell
python scripts/demo.py
python main.py --demo
python main.py --demo --selftest --screenshot reports/demo.png
```

回复带“离线演示”标记，不具备真实大模型推理能力。演示关闭录音、在线 TTS、历史读写，使用内置绘制形象，不依赖第三方 Live2D 模型。

## 重新录制

```powershell
python -m pip install -r requirements-demo.txt
$env:QT_QPA_FONTDIR = "$env:WINDIR\Fonts"
python scripts/record_demo.py --output reports/offline-demo.mp4
```

脚本默认 offscreen，仅录制应用窗口，不读取桌面或其他窗口。Windows 无头 Qt 可能无法枚举字体，需上述字体目录；Linux 需安装中文字体并设置对应目录。imageio-ffmpeg 是可选开发依赖，分发工具时须保留其许可要求。

## 期末展示建议（待执行）

1. 30 秒介绍场景、软件复杂性和团队实际分工。
2. 1 分钟对照 UML 解释策略、适配器、简单工厂和文件边界。
3. 1 分钟运行离线演示、故障注入测试，展示改进前后实测数据。
4. 1 分钟演示在线 LLM、麦克风、TTS、Live2D，记录设备和网络。
5. 30 秒展示 Issue→分支→PR→CI→合并及 AI 纠错经验。

当前短片只覆盖离线流程，不替代完整在线/硬件演示。完整录像须确认不含密钥、个人对话或无授权素材后上传，再在此补充云端链接。
