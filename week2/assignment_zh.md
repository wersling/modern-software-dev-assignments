# 第 2 周 —— 行动项（Action Item）提取器

本周我们将在一个最小可运行的 FastAPI + SQLite 应用基础上继续扩展：该应用可以将自由格式的笔记转换为枚举的行动项清单。

***建议在开始之前先完整阅读本文档。***

提示：预览此 Markdown 文件
- 在 Mac 上，按 `Command (⌘) + Shift + V`
- 在 Windows/Linux 上，按 `Ctrl + Shift + V`


## 开始使用

### Cursor 设置
按照以下步骤设置 Cursor 并打开你的项目：
1. 兑换你免费的 Cursor Pro 一年订阅：`https://cursor.com/students`
2. 下载 Cursor：`https://cursor.com/download`
3. 启用 Cursor 命令行工具：打开 Cursor 后，Mac 用户按 `Command (⌘) + Shift + P`（Windows/Linux 用户按 `Ctrl + Shift + P`）打开命令面板（Command Palette）。输入：`Shell Command: Install 'cursor' command`，选择后回车。
4. 打开一个新的终端窗口，切换到你的项目根目录，运行：`cursor .`

### 当前应用
下面是启动当前 starter 应用的方式：
1. 激活你的 conda 环境。

```
conda activate cs146s
```

2. 在项目根目录运行服务：

```
poetry run uvicorn week2.app.main:app --reload
```

3. 打开浏览器并访问 `http://127.0.0.1:8000/`。
4. 熟悉应用当前状态，确保你能成功输入笔记并生成提取出的行动项清单。

## 练习
对于每个练习，请使用 Cursor 来帮助你实现对当前行动项提取器应用的指定改进。

在你完成作业的过程中，请使用 `writeup.md` 记录你的进展。务必包含你使用的提示词（prompts），以及由你或 Cursor 所做的任何更改。我们将根据写作报告（write-up）的内容进行评分。也请在代码中添加注释来记录你的改动。

### TODO 1：搭建一个新功能（Scaffold a New Feature）

分析 `week2/app/services/extract.py` 中已有的 `extract_action_items()` 函数。该函数目前使用预定义的启发式规则（heuristics）来提取行动项。

你的任务是实现一个 **基于 LLM 的替代方案**：`extract_action_items_llm()`，它通过 Ollama 与大语言模型完成行动项提取。

一些提示：
- 如果你需要生成结构化输出（例如 JSON 字符串数组），可以参考文档：`https://ollama.com/blog/structured-outputs`
- 如果你需要浏览可用的 Ollama 模型，可以参考文档：`https://ollama.com/library`。注意：更大的模型会占用更多资源，建议先从较小的模型开始。拉取并运行模型的命令：`ollama run {MODEL_NAME}`

### TODO 2：添加单元测试（Add Unit Tests）

在 `week2/tests/test_extract.py` 中为 `extract_action_items_llm()` 编写单元测试，覆盖多种输入（例如：项目符号列表、以关键词开头的行、空输入）。

### TODO 3：重构现有代码以提升清晰度（Refactor Existing Code for Clarity）

对后端代码进行重构，重点关注：清晰定义的 API 合约/Schema、数据库层清理、应用生命周期/配置、错误处理。

### TODO 4：使用 Agentic Mode 自动化一些小任务（Use Agentic Mode to Automate Small Tasks）

1. 将基于 LLM 的提取作为一个新接口集成。更新前端，增加一个 “Extract LLM” 按钮：点击后通过新接口触发提取流程。
2. 再暴露一个最终接口，用于获取所有笔记。更新前端，增加一个 “List Notes” 按钮：点击后拉取并展示所有笔记。

### TODO 5：基于代码库生成 README（Generate a README from the Codebase）

***学习目标：***
*学生学习如何让 AI 自省代码库并自动生成文档，展示 Cursor 解析代码上下文并将其转换为可读说明文档的能力。*

使用 Cursor 分析当前代码库并生成一个结构清晰的 `README.md` 文件。README 至少应包含：
- 项目简要概述
- 如何设置并运行项目
- API 接口与功能说明
- 如何运行测试套件的说明

## 交付物（Deliverables）
按照说明填写 `week2/writeup.md`。确保你所有的更改都有记录并体现在代码库中。

## 评分标准（100 分）
- 第 1-5 部分各 20 分（其中 10 分为生成的代码，10 分为每部分的提示词）




