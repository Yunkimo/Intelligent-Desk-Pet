# 重构与验证结果

初次测量于 **2026-10-10（UTC+8）**，**2026-10-11** 补充 Windows 编码回归后复测。代码基线为远端 `c1f0c80`，与导出测试的原本地 `d382e0a` 文件树一致；编码/工程提交完成后的快照见 [metrics.json](evidence/metrics.json)，该快照不含后续文档提交的工作量。

## 1. 环境与口径

| 参数 | 实测值 |
|---|---|
| 系统 | Windows 11 x64，10.0.26200 |
| Python | 3.13.0 |
| Qt | PyQt6 6.11.0 / Qt 6.11.2，offscreen |
| 工具 | pytest 9.1.1、pytest-cov 7.1.0、Ruff 0.17.0、pip-audit 2.10.1 |
| CPU 标识 | Intel64 Family 6 Model 140 Stepping 1 |
| 网络/设备 | 自动测试不调用真实 LLM/TTS，不录音，不测 GPU |

全部 Python 包版本与许可元数据见 [environment.json](evidence/environment.json)，相同平台可用 requirements-lock-win-py313.txt 复现。物理行数含空行/注释；测试函数数不展开参数化，pytest 用例数会展开，两者不可混用。

## 2. 改进前后实测

| 指标 | 基线 | 改进后 | 解释 |
|---|---|---|---|
| pytest 结果 | 31 通过 / 1 失败 | 66 通过 / 0 失败 | 修复功能键断言和 Windows 编码问题，新增故障/安全/离线/GUI/提交规范用例 |
| 自动测试成功率 | 96.875% | 100% | 仅对各自测试集，不代表用户需求全部覆盖 |
| Ruff lint | 通过 | 通过 | 同一 Ruff 版本 |
| Ruff format --check | 9 个文件需格式化 | 通过 | 统一格式并加入检查 |
| ChatProvider 具体策略 | 1 | 2 | 在线与离线可通过同一接口替换 |
| JSON 保存 | 直接覆盖 | 原子替换与失败清理 | 通过故障注入检验，不宣称跨进程事务 |
| pytest 全包行覆盖率 | 未测 | 56.39%（754/1337 语句） | 未覆盖分支主要在音频、菜单、Live2D 和应用引导 |
| providers/storage 行覆盖率 | 未测 | 均 100% | 不等于所有输入或外部服务已验证 |

基线耗时 2.24 秒，改进后最新一次 6.22 秒；用例数量和覆盖统计不同，不能据此得出性能提升/下降结论。原始汇总见 [test-results.json](evidence/test-results.json)。

模块/行数以自动度量快照为准；window.py 仍是最大模块，本轮没有借助新增模式名称掩盖其编排复杂度。

## 3. 运行与安全验证

- CLI 离线演示与 `main.py --demo --selftest` 返回 0；GUI 自检必须实际收到 assistant 消息。
- 真正运行 Qt 窗口并导出中文截图，录制约 11 秒离线 MP4；见 [demo.md](demo.md)。
- pip check 通过。首次审计发现虚拟环境 pip 24.2 的漏洞记录，升级到 26.2.1 后重跑：本次审计未发现已知 Python 依赖漏洞。重复数据库记录不当作独立漏洞数量。
- 索引卫生检查通过；该工具不证明历史从未出现密钥。
- 网络错误脱敏、无效历史过滤、文件替换失败保留旧文件、禁止离线创建网络客户端均有断言。

## 4. 重复实验

按 [testing.md](testing.md) 重跑当前版本。若要复核基线，可在独立目录导出 `git archive c1f0c80`，使用相同虚拟环境运行 pytest 和 Ruff，避免覆盖工作区或开发者配置。度量命令：

```bash
python scripts/metrics.py --baseline c1f0c80 --output reports/metrics.json
```

本地报告与远端 CI 独立；PR/Actions 的真实状态以 GitHub 页面为准。尚未做完整网络延迟、ASR CER、TTS 成功率、内存/CPU 压测、exe 打包验收，不填造实验数值。
