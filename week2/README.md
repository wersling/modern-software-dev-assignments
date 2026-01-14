# 行动项提取器 (Action Item Extractor)

一个基于 FastAPI + SQLite 的智能行动项提取应用，支持从自由格式文本中自动提取待办事项和行动项。提供基于规则和基于 LLM 两种提取方式。

## 项目概述

本项目是一个 Web 应用，能够：
- 从笔记文本中智能提取行动项（待办事项）
- 支持多种格式：项目符号列表、复选框、关键字前缀（TODO、Action、Next）
- 提供两种提取方式：
  - **规则方式**：基于启发式规则和正则表达式
  - **LLM 方式**：使用 Ollama 和 llama3.1:8b 模型进行智能提取
- 管理笔记和行动项，支持标记完成状态
- 简洁的 Web 前端界面

## 技术栈

- **后端框架**：FastAPI 
- **数据库**：SQLite
- **LLM 集成**：Ollama (llama3.1:8b)
- **数据验证**：Pydantic
- **日志**：Loguru
- **测试**：Pytest
- **依赖管理**：Poetry

## 项目结构

```
week2/
├── app/                        # 应用核心代码
│   ├── main.py                # FastAPI 应用入口和生命周期管理
│   ├── config.py              # 配置管理
│   ├── database.py            # 数据库操作层
│   ├── schemas.py             # Pydantic 数据模型定义
│   ├── exceptions.py          # 自定义异常类
│   ├── dependencies.py        # 依赖注入
│   ├── routers/               # API 路由
│   │   ├── action_items.py   # 行动项相关接口
│   │   └── notes.py          # 笔记相关接口
│   └── services/              # 业务逻辑层
│       └── extract.py        # 行动项提取逻辑（规则 + LLM）
├── frontend/                  # 前端文件
│   └── index.html            # 单页面应用
├── tests/                     # 测试文件
│   └── test_extract.py       # 提取功能测试
├── data/                      # 数据目录
│   └── app.db                # SQLite 数据库文件
└── README.md                  # 本文档
```

## 环境要求

- Python >= 3.10
- Conda 环境管理器
- Ollama（用于 LLM 提取功能）

## 安装与设置

### 1. 创建并激活 Conda 环境

```bash
conda create -n cs146s python=3.10
conda activate cs146s
```

### 2. 安装依赖

在项目根目录（包含 `pyproject.toml` 的目录）运行：

```bash
poetry install
```

### 3. 安装 Ollama（可选，用于 LLM 提取）

如果需要使用 LLM 提取功能，需要安装 Ollama 并下载模型：

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 启动 Ollama 服务
ollama serve

# 在另一个终端下载模型
ollama pull llama3.1:8b
```

## 运行应用

### 启动开发服务器

在项目根目录运行：

```bash
poetry run uvicorn week2.app.main:app --reload
```

服务将在 `http://127.0.0.1:8000` 启动。

### 访问应用

在浏览器中打开：`http://127.0.0.1:8000`

## API 接口说明

### 笔记接口 (Notes)

#### 创建笔记
```http
POST /notes
Content-Type: application/json

{
  "content": "笔记内容"
}
```

#### 获取单个笔记
```http
GET /notes/{note_id}
```

#### 获取所有笔记
```http
GET /notes
```

### 行动项接口 (Action Items)

#### 提取行动项（默认方式）
```http
POST /action-items/extract
Content-Type: application/json

{
  "text": "- [ ] Set up database\nTODO: Write tests",
  "save_note": true
}
```

**响应示例：**
```json
{
  "note_id": 1,
  "items": [
    {"id": 1, "text": "Set up database"},
    {"id": 2, "text": "Write tests"}
  ]
}
```

#### 强制使用 LLM 提取
```http
POST /action-items/extract-llm
Content-Type: application/json

{
  "text": "TODO: Review code\nAction: Deploy",
  "save_note": false
}
```

#### 获取行动项列表
```http
GET /action-items
GET /action-items?note_id=1  # 筛选特定笔记的行动项
```

#### 标记行动项完成状态
```http
POST /action-items/{action_item_id}/done
Content-Type: application/json

{
  "done": true
}
```

### API 文档

FastAPI 自动生成的交互式 API 文档：
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 功能特性

### 1. 规则方式提取

基于启发式规则识别行动项：
- 项目符号：`-`, `*`, `•`
- 编号列表：`1.`, `2.`, etc.
- 复选框：`[ ]`, `[x]`, `[TODO]`
- 关键字前缀：`TODO:`, `Action:`, `Next:`
- 祈使句识别：以动作动词开头的句子（Add, Create, Implement, Fix, Update, Write, Check, Verify, Refactor, Document, Design, Investigate）

### 2. LLM 方式提取

使用 Ollama 的 llama3.1:8b 模型：
- 智能理解上下文
- 自动清理格式（去除项目符号、编号、前缀等）
- 结构化 JSON 输出
- 更准确的行动项识别

### 3. 切换提取方式

可以通过以下方式选择提取方法：

**前端界面：**
- "Extract" 按钮：使用默认方式
- "Extract LLM" 按钮：强制使用 LLM

**API 调用：**
- `/action-items/extract`：默认方式
- `/action-items/extract-llm`：强制 LLM

### 4. 数据持久化

- 笔记和行动项存储在 SQLite 数据库
- 支持关联笔记和行动项
- 自动创建索引优化查询性能
- 事务管理确保数据一致性

## 运行测试

### 运行所有测试

```bash
poetry run pytest week2/tests/
```

### 运行特定测试

```bash
# 只测试规则方式
poetry run pytest week2/tests/test_extract.py -k "not LLM"

# 只测试 LLM 方式（需要 Ollama 服务运行）
poetry run pytest week2/tests/test_extract.py::TestLLMExtraction
```

### 跳过 LLM 测试

如果没有安装 Ollama 或不想运行 LLM 测试：

```bash
SKIP_LLM_TESTS=1 poetry run pytest week2/tests/
```

### 测试覆盖

测试包含以下场景：
- ✅ 基本格式提取（项目符号、复选框、编号列表）
- ✅ 关键字前缀识别（TODO、Action、Next）
- ✅ 混合格式处理
- ✅ 去重功能
- ✅ 空文本和边界情况
- ✅ 祈使句启发式识别
- ✅ 特殊字符和 Unicode 支持
- ✅ 多行文本和嵌套列表
- ✅ LLM 提取（需要 Ollama）
- ✅ 错误处理和降级

## 配置说明

### 数据库配置

数据库路径在 `app/config.py` 中配置：

```python
DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "app.db"
```

### 日志配置

使用 Loguru 进行日志记录，日志级别和格式可在代码中调整。

## 开发指南

### 代码规范

- 4 空格缩进
- 必要的中文注释
- 单行注释在代码后
- 使用 Loguru 作为统一日志库
- 使用 Pytest 测试框架

### 添加新功能

1. 在 `app/services/` 中实现业务逻辑
2. 在 `app/routers/` 中添加 API 路由
3. 在 `app/schemas.py` 中定义数据模型
4. 在 `tests/` 中添加测试用例

### 数据库迁移

如需修改数据库结构，编辑 `app/database.py` 中的 `_init_schema()` 方法。

## 常见问题

### Q: LLM 提取失败怎么办？

A: 确保：
1. Ollama 服务正在运行：`ollama serve`
2. 模型已下载：`ollama pull llama3.1:8b`
3. 检查日志中的错误信息

### Q: 如何切换 LLM 模型？

A: 在 `app/services/extract.py` 中修改 `extract_action_items_llm()` 的 `model` 参数默认值。

### Q: 数据库文件在哪里？

A: 默认位置是 `week2/data/app.db`。可以在 `app/config.py` 中修改。

### Q: 如何重置数据库？

A: 删除 `week2/data/app.db` 文件，重启应用会自动创建新的数据库。

## 性能优化

- 数据库索引：在 `note_id` 和 `done` 字段上创建索引
- 连接池：使用上下文管理器自动管理连接
- 事务管理：批量操作使用事务确保性能和一致性
- LLM 缓存：考虑添加缓存层减少重复调用

## 安全考虑

- SQL 注入防护：使用参数化查询
- 输入验证：Pydantic 模型自动验证
- 错误处理：自定义异常类统一处理
- 日志记录：记录关键操作便于审计

## 许可证

本项目为课程作业项目。

## 贡献

这是一个课程作业项目，不接受外部贡献。

## 联系方式

如有问题，请联系课程助教或在课程论坛提问。

---

**注意**：本项目为教学目的创建，不建议直接用于生产环境。

