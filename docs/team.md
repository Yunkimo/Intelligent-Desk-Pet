# 团队分工与工作量度量

用户已确认团队课设；成员身份、实际分工、工时和最终 KPI 比例待团队补充。以下记录不替代成员确认。

## 1. 证据口径

```bash
python scripts/metrics.py --baseline c1f0c80
git shortlog -sne HEAD
git log --no-merges --numstat --format="%h %aN %s"
```

工具按 Git mailmap 作者名汇总非 merge patch，分类统计代码、测试、文档、工程配置的增删行。排除 assets/ 第三方资源与二进制。同一行重复修改及格式化会增加统计，不能直接换算工时/绩效。

远端基线 `c1f0c80` 的 42 次提交全部署名 **Yunkimo**，非 merge patch 为 40。原本地 main 存在内容相同、作者不同的历史，不能当作远端多人协作证据。本轮保留原 main，不强推改写远端，从 origin/main 新建功能分支。

本轮执行账号 **wwweiliang** 使用 Codex 辅助，提交按实际账号署名。不替其他成员补造 commit、Issue、PR 或 Review；历史真正作者和劳动需成员提供证据核实。

## 2. 待成员确认的分工

| 成员/账号 | 负责范围 | 可验收产物 | 实际工时 | KPI 占比 | 证据 |
|---|---|---|---|---|---|
| 待填写 | 架构与核心功能 | UML、实现、回归测试 | 待填写 | 待确认 | PR/commit/设计记录 |
| 待填写 | GUI/音频集成 | 演示、设备测试、缺陷修复 | 待填写 | 待确认 | 视频/Issue/PR |
| 待填写 | 测试与工程质量 | 测试计划、CI、缺陷复现 | 待填写 | 待确认 | CI/JUnit/Review |
| 待填写 | 文档与部署 | 手册、供应链、打包验证 | 待填写 | 待确认 | 文档 patch/发布记录 |

一人可承担多个职责，行数不表示团队人数。确认后删去不适用行，最终比例应合计 100%。

## 3. 建议评价方式（尚非最终比例）

验收产物质量 40%、承担并完成的工作 30%、可验证评审与协作 20%、复现与分享 10%。先以 Issue 明确负责人和验收标准，再共同确认完成情况。代码、测试、设计和文档使用相同证据要求，不按代码行数简单排名。

- 开发：关联需求、单一职责提交、测试结果。
- 测试：可复现缺陷、用例、失败到修复记录。
- 设计：可评审 UML、取舍、设计修改记录。
- 评审：具体意见及后续修改，不能自行“同意”代替同行评审。

## 4. 本轮协作记录

任务见 [#5](https://github.com/Yunkimo/Intelligent-Desk-Pet/issues/5)、[#6](https://github.com/Yunkimo/Intelligent-Desk-Pet/issues/6)、[#7](https://github.com/Yunkimo/Intelligent-Desk-Pet/issues/7)。关联 PR/CI 以 [Pull Requests](https://github.com/Yunkimo/Intelligent-Desk-Pet/pulls) 实际状态为准。

提交前至少由另一位真实成员完成评审或补充已有劳动证据，说明职责/工作量合理性。本轮新增 Issues/PRs 不能消除原先单人署名的证据缺口。
