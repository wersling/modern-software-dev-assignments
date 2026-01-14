# 第 4 周 — 现实生活中的自主编码代理

> ***我们建议在开始之前阅读整个文档。***

本周，您的任务是在此存储库的上下文中使用以下 **Claude Code** 功能的任意组合构建至少 **2 个自动化**：

- 自定义斜杠命令（签入 `.claude/commands/*.md`）

- 用于存储库或上下文指导的 `CLAUDE.md` 文件

- Claude SubAgents（协同工作的角色专用代理）

- 集成到 Claude Code 中的 MCP 服务器

您的自动化应有意义地改进开发人员的工作流程——例如，通过简化测试、文档、重构或数据相关任务。然后，您将使用创建的自动化来扩展 `week4/` 中的入门应用程序。

## 了解 Claude Code
要深入了解 Claude Code 并探索您的自动化选项，请阅读以下两个资源：

1. **Claude Code 最佳实践：** [anthropic.com/engineering/claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices)

2. **SubAgents 概述：** [docs.anthropic.com/en/docs/claude-code/sub-agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

## 探索入门应用程序
最小的全栈入门应用程序，旨在成为 **“开发人员的指挥中心”**。
- 带有 SQLite (SQLAlchemy) 的 FastAPI 后端
- 静态前端（不需要 Node 工具链）
- 最小测试 (pytest)
- 预提交钩子 (black + ruff)
- 用于练习代理驱动工作流的任务

使用此应用程序作为您的游乐场，试验您构建的 Claude 自动化。

### 结构

```
backend/                # FastAPI 应用程序
frontend/               # 由 FastAPI 服务的静态 UI
data/                   # SQLite 数据库 + 种子数据
docs/                   # 代理驱动工作流的任务
```

### 快速入门

1) 激活您的 conda 环境。

```bash
conda activate cs146s
```

2) (可选) 安装预提交钩子

```bash
pre-commit install
```

3) 运行应用程序（从 `week4/` 目录）

```bash
make run
```

4) 打开 `http://localhost:8000` 查看前端，打开 `http://localhost:8000/docs` 查看 API 文档。

5) 试用入门应用程序，了解其当前功能和特性。

### 测试
运行测试（从 `week4/` 目录）
```bash
make test
```

### 格式化/Linting
```bash
make format
make lint
```

## 第一部分：构建您的自动化（选择 2 个或更多）
既然您已熟悉入门应用程序，下一步就是构建自动化以增强或扩展它。以下是您可以选择的几个自动化选项。您可以混合搭配不同类别。

在构建自动化时，请在 `writeup.md` 文件中记录您的更改。暂时将 *“您如何使用自动化来增强入门应用程序”* 部分留空——您将在作业的第二部分返回此部分。

### A) Claude 自定义斜杠命令
斜杠命令是针对重复工作流的功能，允许您在 `.claude/commands/` 内的 Markdown 文件中创建可重用的工作流。Claude 通过 `/` 公开这些命令。

- 示例 1：带覆盖率的测试运行器
  - 名称：`tests.md`
  - 意图：运行 `pytest -q backend/tests --maxfail=1 -x`，如果通过，则运行覆盖率。
  - 输入：可选标记或路径。
  - 输出：总结失败并建议后续步骤。
- 示例 2：文档同步
  - 名称：`docs-sync.md`
  - 意图：读取 `/openapi.json`，更新 `docs/API.md`，并列出路由差异。
  - 输出：类似 diff 的摘要和待办事项。
- 示例 3：重构线束
  - 名称：`refactor-module.md`
  - 意图：重命名模块（例如，`services/extract.py` → `services/parser.py`），更新导入，运行 lint/测试。
  - 输出：修改文件的清单和验证步骤。

>*提示：保持命令专注，使用 `$ARGUMENTS`，并首选幂等步骤。考虑允许列表安全工具并使用无头模式以实现可重复性。*

### B) `CLAUDE.md` 指导文件
`CLAUDE.md` 文件在开始对话时会自动读取，允许您提供影响 Claude 行为的特定于存储库的说明、上下文或指导。在存储库根目录（以及可选的 `week4/` 子文件夹中）创建一个 `CLAUDE.md` 以指导 Claude 的行为。

- 示例 1：代码导航和入口点
  - 包括：如何运行应用程序，路由器位于何处（`backend/app/routers`），测试位于何处，数据库如何播种。
- 示例 2：样式和安全护栏
  - 包括：工具期望（black/ruff），要运行的安全命令，要避免的命令，以及 lint/测试门控。
- 示例 3：工作流片段
  - 包括：“当被要求添加端点时，首先编写一个失败的测试，然后实现，然后运行预提交。”

> *提示：像提示一样迭代 `CLAUDE.md`，保持简洁和可操作，并记录您期望 Claude 使用的自定义工具/脚本。*

### C) SubAgents（角色专用）

SubAgents 是配置为使用自己的系统提示、工具和上下文处理特定任务的专用 AI 助手。设计两个或更多协作代理，每个代理负责单个工作流中的不同步骤。

- 示例 1：TestAgent + CodeAgent
  - 流程：TestAgent 为更改编写/更新测试 → CodeAgent 实现代码以通过测试 → TestAgent 验证。
- 示例 2：DocsAgent + CodeAgent
  - 流程：CodeAgent 添加新的 API 路由 → DocsAgent 更新 `API.md` 和 `TASKS.md` 并根据 `/openapi.json` 检查漂移。
- 示例 3：DBAgent + RefactorAgent
  - 流程：DBAgent 提议架构更改（调整 `data/seed.sql`） → RefactorAgent 更新模型/架构/路由器并修复 lint。

>*提示：使用清单/草稿板，在角色之间重置上下文（`/clear`），并并行运行代理以执行独立任务。*

## 第二部分：让您的自动化发挥作用
既然您已经构建了 2+ 个自动化，让我们把它们投入使用！在 `writeup.md` 的 *“您如何使用自动化来增强入门应用程序”* 部分下，描述您如何利用每个自动化来改进或扩展应用程序的功能。

例如，如果您实现了自定义斜杠命令 `/generate-test-cases`，请解释您如何使用它来与入门应用程序交互并对其进行测试。

## 交付物
1) 两个或更多自动化，其中可能包括：
   - `.claude/commands/*.md` 中的斜杠命令
   - `CLAUDE.md` 文件
   - SubAgent 提示/配置（记录清楚，文件/脚本（如果有））

2) `week4/` 下的 `writeup.md` 报告，其中包括：
  - 设计灵感（例如引用最佳实践和/或子代理文档）
  - 每个自动化的设计，包括目标、输入/输出、步骤
  - 如何运行它（确切的命令）、预期输出和回滚/安全说明
  - 之前与之后（即手动工作流与自动化工作流）
  - 您如何使用自动化来增强入门应用程序

## 提交说明
1. 确保您已将所有更改推送到远程存储库以进行评分。
2. **确保您已将 brentju 和 febielin 添加为作业存储库的协作者。**
3. 通过 Gradescope 提交。
