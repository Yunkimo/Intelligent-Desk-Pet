# 测试与质量检查

## 1. 从干净环境复现

建议 Python 3.12 或 3.13。本轮 Windows 实测 Python 3.13.0，更高版本未验证。

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m ruff format --check .
python -m pytest --cov=pet --cov-report=term-missing --cov-report=xml:reports/coverage.xml --junitxml=reports/junit.xml
python scripts/check_repo.py
python scripts/demo.py
python main.py --demo --selftest
python -m pip_audit --format=json --output=reports/pip-audit.json
python scripts/metrics.py
```

PowerShell 若禁止激活脚本，可直接使用 `.venv\Scripts\python.exe`。`check_repo.py` 检查 Git 索引，不能代替完整的历史密钥扫描。

## 2. 测试层级与用例

| 范围 | 用例文件 | 输入与预期 |
|---|---|---|
| 配置 | test_config.py | 环境覆盖；拒绝越界/非有限值/布尔冒充数值；保存保留其他字段 |
| 文件 | test_storage.py | JSON 往返；非法类型拒绝；replace 失败后原文件不变且临时文件清理 |
| 记忆 | test_memory.py | 最近 N 轮；过滤无效角色/非文本；不信任磁盘 system 消息 |
| LLM | test_providers.py | 拼接与回调、异常时关闭流、限制参数注入、不泄漏原始错误 |
| 离线 | test_demo.py | 工厂→LLMClient→Memory；禁止创建网络客户端，不写历史 |
| GUI 集成 | test_window_demo.py | 真实窗口/QThread 往返、空输入/忙碌保护、禁止演示录音 |
| 形象交互 | test_image_utils.py、test_live2d.py、test_bubble.py、test_hotkey.py | 文件、模型元数据、折行、平台键盘能力 |
| 提交规范 | test_quality_tools.py | 接受合法中文描述，拒绝缺类型/过长/全英文描述 |

测试隔离 `.env`、环境密钥和可变 config.json，不访问真实历史，不向 LLM/TTS 发请求。Qt offscreen 测试不等于 GPU/音频设备实测。

## 3. CI 与服务器环境

Actions 在分支 push 和 PR 上运行 Windows/Linux 检查，上传 JUnit、覆盖率、GUI 截图、Git/AST 度量。独立依赖审计任务发现漏洞或无法完成时不报告成功。

Ubuntu 需要 Qt/声音系统库、xvfb、xauth，包清单见 [CI 配置](../.github/workflows/ci.yml)。pynput 导入时探测 X，因此测试使用 `xvfb-run -a python -m pytest`。CLI 演示无需 X、音频设备或 Qt 窗口，可在服务器复现核心链路。

远端结果以 [Actions](https://github.com/Yunkimo/Intelligent-Desk-Pet/actions) 为准。本地通过不能替代 CI；报告中的覆盖率不将未测 GUI/音频分支算作已覆盖。

## 4. 人工与网络验收（待执行）

| 编号 | 操作 | 验收标准 |
|---|---|---|
| M01 | 在线 LLM 文字对话 | 流式回复、窗口可拖动；记录模型、网络、首 token/总时延 |
| M02 | 录制固定中文句子 | 记录设备、16kHz 输入、ASR 模型、转写与人工标注 CER |
| M03 | 合成固定句子 | 可播放、清理临时文件；记录 10 次成功次数和时延 |
| M04 | 可信 Live2D、动作/形象切换 | 无渲染错误；记录 GPU/驱动、截图与录屏 |
| M05 | 聊天中退出、换人设、断网 | 检查线程清理、错误提示与旧历史隔离 |

`python scripts/smoke_test.py llm` / `tts` 会向服务方发送文本，可能产生费用。缺密钥跳过不能记为通过。[TTS Issue #4](https://github.com/Yunkimo/Intelligent-Desk-Pet/issues/4) 仍需真实网络复现。数值结果见 [validation.md](validation.md)。
