# LLM 行动项提取实现说明

## 实现概述

已成功实现基于 LLM 的行动项提取功能，使用 `llama3.1:8b` 模型通过 Ollama 进行结构化输出。

## 核心实现

### 1. 提取函数 (`app/services/extract.py`)

```python
def extract_action_items_llm(text: str, model: str = "llama3.1:8b") -> List[str]
```

**特性：**
- 使用 Pydantic 模型定义结构化输出格式
- 智能提取行动项并自动清理格式（去除项目符号、编号、前缀等）
- 完整的错误处理和去重逻辑
- 支持自定义模型参数

**关键技术：**
- `ActionItemsResponse` Pydantic 模型用于 JSON Schema
- `ollama.chat()` API 调用与 `format` 参数实现结构化输出
- 详细的 System Prompt 指导模型提取准确的行动项

### 2. API 路由 (`app/routers/action_items.py`)

提供三个端点：

| 端点 | 说明 | 提取方式 |
|------|------|----------|
| `POST /action-items/extract` | 默认端点 | 使用 `get_extract_function()` 自动选择 |
| `POST /action-items/extract-llm` | 强制 LLM | 始终使用 LLM |
| `POST /action-items/extract-rule` | 强制规则 | 始终使用规则 |

**设计原则：**
- 路由层不关心使用什么模型
- 通过 `get_extract_function()` 统一管理配置
- 保持关注点分离，配置逻辑集中在 `extract.py`

## 切换方式

### 全局配置

在 `app/services/extract.py` 中设置：

```python
USE_LLM_EXTRACTION = True   # 使用 LLM
USE_LLM_EXTRACTION = False  # 使用规则
```

### API 调用示例

```python
import requests

# 使用默认方式（当前为LLM）
requests.post("http://localhost:8000/action-items/extract", 
              json={"text": "TODO: Review code"})

# 强制使用LLM
requests.post("http://localhost:8000/action-items/extract-llm",
              json={"text": "TODO: Review code"})

# 强制使用规则
requests.post("http://localhost:8000/action-items/extract-rule",
              json={"text": "TODO: Review code"})
```

## 效果对比

**输入文本：**
```
- [ ] Set up database
TODO: Review code
Action: Deploy to production
```

**规则方式输出：**
- Set up database
- TODO: Review code
- Action: Deploy to production

**LLM 方式输出：**
- Set up database
- Review code ✨（自动去除 TODO:）
- Deploy to production ✨（自动去除 Action:）

## 前置要求

### 安装 Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
```

### 下载模型
```bash
ollama pull llama3.1:8b
```

## 业务一致性保证

✅ **返回格式一致**：两种方式都返回 `List[str]`  
✅ **去重逻辑一致**：都保持顺序去重  
✅ **空输入处理**：都返回空列表  
✅ **API 兼容性**：无需修改现有调用代码  

## 技术要点

1. **结构化输出**：使用 Pydantic 的 `model_json_schema()` 生成 JSON Schema
2. **Prompt 工程**：详细的 System Prompt 定义提取规则和清理逻辑
3. **灵活切换**：通过配置变量和独立端点支持多种使用方式
4. **保留原函数**：原有的规则方式完全保留，互不影响

## 测试验证

所有 API 端点已测试通过：
- ✅ 默认提取端点（LLM）
- ✅ 强制 LLM 端点
- ✅ 强制规则端点
- ✅ 结果去重和格式清理
- ✅ 错误处理（空输入、LLM 失败等）

