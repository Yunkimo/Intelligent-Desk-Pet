# 贡献指南

## 代码风格

- 统一使用 [Ruff](https://docs.astral.sh/ruff/) 检查与格式化（配置见 `pyproject.toml`）。
- 行宽 ≤ 100；启用规则 `E`/`F`/`I`/`W`（忽略 E501 由 ruff-format 处理）。
- 新增公共接口应有类型注解，模块职责明确；既有 Qt 回调仍有待逐步完善注解。

```bash
ruff check .            # 静态检查
ruff format .           # 格式化
ruff format --check .   # CI 检查，不写文件
```

## 提交规范（Conventional Commits）

提交信息统一为 `type: 中文描述`，一个提交只做一件事：

| type | 用途 |
|---|---|
| feat | 新功能 |
| fix | 修复缺陷 |
| refactor | 重构（不改行为） |
| test | 测试 |
| docs | 文档 |
| ci | CI/构建脚本 |
| chore | 杂项（脚手架、依赖） |

示例：`feat: 实现语音识别引擎`、`test: 补充记忆裁剪用例`。

## 分支与协作流程

1. 创建或领取 Issue，记录负责人、验收标准、预期工作量。
2. `git fetch origin` 后从远端创建分支：`git switch -c feat/xxx origin/main`。有本地修改时先确认基线兼容，不强推覆盖公共历史。
3. 开发并按上面的规范提交。
4. 推送到远端并创建 **Pull Request**，通过 CI 与评审后合并。

## 测试要求

- 新增或修改逻辑必须补充/更新对应单元测试。
- 提交前跑通 `ruff check .`、`ruff format --check .` 和 `pytest`；命令返回非零须处理后再提交。

## 本地开发

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pre_commit install
python -m pre_commit run --all-files
```

钩子使用虚拟环境中的 Ruff，提交前先激活虚拟环境。pre-commit 自动格式化后需重新暂存；commit-msg 校验 `type(scope): 中文描述`（最多 100 字符），标准 Git 合并标题除外。工具不能自动证明“单一职责”，评审仍需检查提交粒度。依据：[Ruff 格式化文档](https://docs.astral.sh/ruff/formatter/)、[pre-commit 文档](https://pre-commit.com/)。

不要伪造其他成员作者身份或回填不存在的评审。AI 辅助需说明实际使用与验证，工作量以 [team.md](docs/team.md) 口径记录。格式化修改尽量与行为修改分开提交；第三方压缩 JS 不使用 Python 格式化器重写。
