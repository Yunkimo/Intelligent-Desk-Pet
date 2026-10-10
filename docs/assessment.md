# 课程提交与评分项对照

## 提交入口

- [代码仓库](https://github.com/Yunkimo/Intelligent-Desk-Pet)
- [设计开发 Markdown](https://github.com/Yunkimo/Intelligent-Desk-Pet/blob/main/docs/design.md)
- [用户手册](user-manual.md)、[测试说明](testing.md)、[实测结果](validation.md)
- [演示录像与截图](demo.md)、[AI 使用记录](ai-usage.md)
- [团队与 KPI](team.md)、[Actions](https://github.com/Yunkimo/Intelligent-Desk-Pet/actions)

提交前确认 main 已包含最终修改且云端链接可打开。90+ 由课程评审决定，不能保证分数。

## 逐项核对

| 编号 | 评分项 | 证据 / 边界 |
|---|---|---|
| 1 | 代码风格 | CONTRIBUTING、EditorConfig、Ruff |
| 2 | 分支/PR/Issue | 历史 PR #1/#3，本轮 #5/#6/#7 及关联 PR；不替代团队评审 |
| 3 | 仓库污染 | gitignore、索引检查；文档图/小视频有明确证据用途 |
| 4 | 许可/供应链 | LICENSE、supply-chain；角色模型授权待确认 |
| 5 | 配置解耦 | Settings；超时/重试/生成参数注入 |
| 6 | 提交语言 | type(scope): 中文描述，保留自动 merge 标题 |
| 7 | 提交粒度 | 文件边界、演示、测试修复、CI、文档分别提交 |
| 8 | 提交前格式化 | pre-commit + Ruff；CI 检查 lint/format |
| 9 | 前后端解耦 | 引擎/Worker/UI/Live2D JS；窗口编排仍需拆分 |
| 10 | 运行部署 | setup/run/build_exe、CLI/GUI 演示 |
| 11 | 手册 | user-manual.md |
| 12 | 重构量化 | metrics.py、validation.md、可验证基线 |
| 13 | 实验指标 | 通过率/覆盖率/策略数/格式；未测语音精度和时延 |
| 14 | 环境参数 | validation、environment.json、版本快照 |
| 15 | 用例 | tests/、testing.md、CI JUnit |
| 16 | 安全 | security.md、故障/隐私测试；Live2D 开关仍有风险 |
| 17 | 视频 | 离线 MP4；完整联网/音频/Live2D 展示待录制 |
| 18 | 工作量度量 | metrics.py 分类代码/测试/文档/工程配置 |
| 19 | KPI | team.md 给出口径，成员分配和比例待确认 |
| 20 | 多人提交 | 远端基线单一作者；本轮实际账号，不伪造记录 |
| 21 | 非编码劳动 | Issue/PR 模板与指标；待补真实设计/测试/评审链接 |

## 仍需团队完成

1. 确认成员、账号、分工、工时、KPI，并解释远端历史单一作者的原因。
2. 由另一位真实成员评审，不将自动检查或自行合并说成同行审批。
3. 补全模型/图片来源授权，必要时替换素材。
4. 在线 LLM/TTS、麦克风、Live2D、打包启动的人工验收与完整录像。
5. 若课程强制要求嵌入式硬件或实际服务器部署，需另做实践；目前只有桌面软件与 Linux CI/CLI 验证。
