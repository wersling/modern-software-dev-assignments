# Week 5 项目 - AI 开发团队配置

欢迎使用 AI 开发代理来帮助完成 Week 5 项目。这是一个基于 FastAPI 的全栈应用，专注于自主编码代理工作流的实验。

## 项目概述

**Week 5** 是一个最小化的全栈入门应用，用于实验自主编码代理。该项目使用现代 Python 技术栈，包含多个待完成的任务，特别适合练习代理驱动的工作流。

## 技术栈

- **后端框架**: FastAPI (现代异步 Python Web 框架)
- **数据库**: SQLite + SQLAlchemy 2.0 (ORM)
- **数据验证**: Pydantic V2
- **前端**: 纯静态 HTML/CSS/JavaScript (未来可能迁移到 Vite + React)
- **测试框架**: pytest
- **代码质量**: Black (格式化) + Ruff (Linting) + Pre-commit hooks
- **API 文档**: FastAPI 自动生成的 OpenAPI/Swagger 文档
- **异步运行时**: Uvicorn

---

## AI 团队配置 (自动生成于 2026-01-07)

**重要提示：当任务有对应的子代理可用时，您必须使用子代理来完成。**

### 推荐的 AI 专家团队

| 任务类型 | 推荐代理 | 说明 |
|---------|---------|------|
| **FastAPI 后端开发** | `@fastapi-expert` | FastAPI 专用专家，处理路由、Pydantic 模型、依赖注入、异步编程和 API 设计 |
| **Python 后端逻辑** | `@python-expert` | Python 通用专家，处理项目架构、数据模型、服务和复杂业务逻辑 |
| **数据库与 ORM** | `@python-expert` + `@fastapi-expert` | SQLAlchemy 2.0 查询优化、关系设计、迁移和索引策略 |
| **测试策略与实施** | `@testing-expert` | pytest 测试、fixtures、参数化测试、覆盖率分析和测试架构设计 |
| **前端开发 (迁移到 React)** | `@react-component-architect` | React 19 组件架构、Vite 配置、状态管理和现代 UI 模式 |
| **前端开发 (当前静态)** | `@frontend-developer` | HTML/CSS/JavaScript 优化、响应式设计和交互增强 |
| **API 设计与架构** | `@api-architect` | RESTful API 设计、端点规划、API 版本控制和 OpenAPI 规范 |
| **性能优化** | `@performance-optimizer` | 数据库查询优化、异步性能、索引策略和响应时间优化 |
| **代码审查** | `@code-reviewer` | **每次功能完成后必须使用** - 安全审查、性能分析、代码质量检查 |
| **文档编写** | `@documentation-specialist` | API 文档、README 更新、架构指南和用户手册 |
| **代码质量分析** | `@code-archaeologist` | 深度代码分析、技术债务识别和架构改进建议 |

---

### 使用场景与代理选择指南

#### 后端开发场景

1. **新增 API 端点或路由**
   ```
   使用 @fastapi-expert
   示例: "@fastapi-expert 实现 POST /notes/{id}/extract 端点，用于提取标签和待办事项"
   ```

2. **数据库模型修改或查询优化**
   ```
   使用 @python-expert 和 @fastapi-expert
   示例: "@python-expert 为 Note 模型添加多对多标签关系，并创建必要的 SQLAlchemy 关系"
   ```

3. **复杂业务逻辑或服务层**
   ```
   使用 @python-expert
   示例: "@python-expert 改进 extract.py 中的解析逻辑，支持 #hashtags 和 - [ ] 任务提取"
   ```

#### 前端开发场景

4. **迁移到 Vite + React**
   ```
   使用 @react-component-architect
   示例: "@react-component-architect 将现有前端迁移到 Vite + React，实现 Notes 列表和 CRUD 功能"
   ```

5. **当前静态前端优化**
   ```
   使用 @frontend-developer
   示例: "@frontend-developer 为现有前端添加搜索和分页 UI 控件"
   ```

#### 测试与质量保证场景

6. **编写或改进测试**
   ```
   使用 @testing-expert
   示例: "@testing-expert 为新的搜索端点编写全面的 pytest 测试，包括边界情况"
   ```

7. **功能完成后的代码审查**
   ```
   使用 @code-reviewer (必须)
   示例: "@code-reviewer 审查最近的 Notes CRUD 功能实现，重点关注安全性和性能"
   ```

8. **性能问题诊断**
   ```
   使用 @performance-optimizer
   示例: "@performance-optimizer 分析 Notes 搜索查询的性能，并添加必要的索引"
   ```

#### 文档与知识管理场景

9. **更新项目文档**
   ```
   使用 @documentation-specialist
   示例: "@documentation-specialist 更新 README.md，添加新端点的使用说明和 API 文档链接"
   ```

10. **深度代码分析**
    ```
    使用 @code-archaeologist
    示例: "@code-archaeologist 分析当前项目架构，识别技术债务并提供重构建议"
    ```

---

### 开发工作流程建议

#### 标准开发流程

1. **分析任务**
   - 使用 `@code-archaeologist` 理解现有代码库架构
   - 阅读 `docs/TASKS.md` 中的具体任务要求

2. **实施功能**
   - 后端任务: `@fastapi-expert` 或 `@python-expert`
   - 前端任务: `@react-component-architect` 或 `@frontend-developer`

3. **编写测试**
   - 使用 `@testing-expert` 创建全面的测试覆盖

4. **代码审查**
   - **关键步骤**: 使用 `@code-reviewer` 进行安全和性能审查

5. **性能优化**
   - 如需要: 使用 `@performance-optimizer` 优化瓶颈

6. **文档更新**
   - 使用 `@documentation-specialist` 更新相关文档

#### 多代理协作示例

**场景: 实现带搜索和分页的 Notes 列表**

```
步骤 1: @fastapi-expert 
"实现 GET /notes/search 端点，支持查询参数 q、page、page_size 和排序"

步骤 2: @testing-expert
"为新搜索端点编写 pytest 测试，覆盖查询边界和分页逻辑"

步骤 3: @code-reviewer
"审查搜索端点实现，检查 SQL 注入风险和查询性能"

步骤 4: @performance-optimizer
"优化搜索查询性能，添加适当的数据库索引"

步骤 5: @frontend-developer
"为前端添加搜索输入框和分页控件"

步骤 6: @documentation-specialist
"更新 README.md，添加搜索端点的使用示例"
```

---

### 代理协作最佳实践

1. **明确任务边界**
   - 每次对话专注于一个特定任务
   - 提供清晰的上下文和期望输出

2. **使用正确的代理**
   - FastAPI 特定功能 → `@fastapi-expert`
   - 通用 Python 逻辑 → `@python-expert`
   - 测试相关 → `@testing-expert`
   - 审查必须 → `@code-reviewer`

3. **代码审查是强制性的**
   - 所有新功能完成后使用 `@code-reviewer`
   - 合并到 main 分支前必须经过审查

4. **文档同步更新**
   - 使用 `@documentation-specialist` 保持文档最新
   - API 变更后立即更新文档

5. **性能意识**
   - 遇到性能问题时使用 `@performance-optimizer`
   - 数据库查询优化优先考虑索引

---

### 项目特定注意事项

#### 数据库操作
- 使用 SQLAlchemy 2.0 语法
- 所有数据库操作应在服务层或路由中正确处理
- 注意 SQLite 的并发限制（适合开发，生产考虑 PostgreSQL）

#### 异步编程
- FastAPI 支持 async/await
- I/O 密集型操作应使用异步
- 数据库查询使用 SQLAlchemy 的异步支持

#### 测试要求
- 所有新端点必须有测试覆盖
- 使用 fixtures 进行测试数据管理
- 测试应包括成功路径和错误情况

#### 代码风格
- 使用 Black 进行代码格式化
- 使用 Ruff 进行 linting
- Pre-commit hooks 已配置，确保提交前自动运行

---

### 可用任务列表

详见 `docs/TASKS.md`，包括：

1. 迁移前端到 Vite + React (复杂)
2. Notes 搜索与分页 (中等)
3. 完整的 Notes CRUD (中等)
4. Action Items 过滤和批量完成 (中等)
5. Tags 功能和多对多关系 (复杂)
6. 改进提取逻辑 (中等)
7. 错误处理和响应封装 (简单-中等)
8. 列表端点分页 (简单)
9. 查询性能和索引 (简单-中等)
10. 测试覆盖率改进 (简单)
11. 部署到 Vercel (中等-复杂)

---

### 快速开始示例

```
# 示例 1: 添加搜索功能
"@fastapi-expert 实现 Notes 搜索端点，支持标题和内容搜索，以及分页"

# 示例 2: 优化性能
"@performance-optimizer 分析当前数据库查询性能，建议并实现索引优化"

# 示例 3: 代码审查
"@code-reviewer 审查最近的代码变更，重点关注安全性和可维护性"

# 示例 4: 添加测试
"@testing-expert 为 Action Items 批量完成功能编写全面的测试"

# 示例 5: 迁移到 React
"@react-component-architect 将前端迁移到 Vite + React，首先实现 Notes 列表页面"
```

---

## 配置更新记录

- **2026-01-07**: 初始 AI 团队配置创建，针对 FastAPI + SQLite 技术栈

