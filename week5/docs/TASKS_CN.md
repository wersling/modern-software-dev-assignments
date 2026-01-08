# 仓库任务清单

## 1) 将前端迁移到 Vite + React（复杂）- 已完成
- 在 `week5/frontend/`（或子文件夹如 `week5/frontend/ui/`）中搭建 Vite + React 应用。
- 将当前的静态资源替换为由 FastAPI 提供的构建包：
  - 构建到 `week5/frontend/dist/`。
  - 更新 FastAPI 静态挂载以提供 `dist` 目录，并将根路径（`/`）指向 `dist` 中的 `index.html`。
- 在 React 中对接现有端点：
  - 笔记列表、创建、删除、编辑。
  - 行动项列表、创建、完成。
- 更新 `Makefile`，添加以下目标：`web-install`、`web-dev`、`web-build`，并确保 `make run` 自动构建 Web 包（或在文档中说明工作流程）。
- 为至少两个组件添加组件/单元测试（React Testing Library），并在 `backend/tests` 中添加集成测试以确保 API 兼容性。

## 2) 带分页和排序的笔记搜索（中等）- 已完成
- 实现 `GET /notes/search?q=...&page=1&page_size=10&sort=created_desc|title_asc`。
- 对标题/内容使用不区分大小写的匹配。
- 返回包含 `items`、`total`、`page`、`page_size` 的有效载荷。
- 添加 SQLAlchemy 查询组合以支持过滤、排序和分页。
- 更新 React UI，添加搜索输入框、结果计数和上一页/下一页分页控制。
- 在 `backend/tests/test_notes.py` 中为查询边界情况和分页添加测试。

## 3) 完整的笔记 CRUD 操作与乐观 UI 更新（中等）- 已完成
- 添加 `PUT /notes/{id}` 和 `DELETE /notes/{id}`。
- 在前端中乐观地更新状态，同时处理错误回滚。
- 在 `schemas.py` 中验证有效载荷（合理设置最小长度、最大长度）。
- 添加成功和验证错误的测试。

## 4) 行动项：过滤器和批量完成（中等）- 进行中
- 添加 `GET /action-items?completed=true|false` 以按完成状态过滤。
- 添加 `POST /action-items/bulk-complete`，接受 ID 列表并在事务中标记为已完成。
- 更新前端，添加过滤器切换和批量操作 UI。
- 添加测试以覆盖过滤器、批量行为以及错误时的事务回滚。

## 5) 带多对多关系的标签功能（复杂）
- 添加 `Tag` 模型和连接表 `note_tags`（`Note` 和 `Tag` 之间的多对多关系）。
- 端点：
  - `GET /tags`、`POST /tags`、`DELETE /tags/{id}`
  - `POST /notes/{id}/tags` 用于附加，`DELETE /notes/{id}/tags/{tag_id}` 用于分离
- 更新提取功能（见下一任务），从 `#标签` 自动创建/附加标签。
- 更新 UI，将标签显示为芯片，并按标签过滤笔记。
- 添加模型关系和端点行为的测试。

## 6) 改进提取逻辑和端点（中等）
- 扩展 `backend/app/services/extract.py` 以解析：
  - `#标签` → 标签
  - `- [ ] 任务文本` → 行动项
- 添加 `POST /notes/{id}/extract`：
  - 返回结构化的提取结果，当 `apply=true` 时可选地持久化新标签/行动项。
- 为提取解析和 `apply=true` 持久化路径添加测试。

## 7) 健壮的错误处理和响应信封（简单-中等）
- 使用 Pydantic 模型添加验证（最小长度约束、非空字符串）。
- 添加全局异常处理器以返回一致的 JSON 信封：
  - `{ "ok": false, "error": { "code": "NOT_FOUND", "message": "..." } }`
  - 成功响应：`{ "ok": true, "data": ... }`
- 更新测试以断言成功和错误情况下的信封格式。

## 8) 所有集合的列表端点分页（简单）
- 为 `GET /notes` 和 `GET /action-items` 添加 `page` 和 `page_size`。
- 为每个端点返回 `items` 和 `total`。
- 更新前端以分页列表；添加边界测试（空的最后一页、过大的页面大小）。

## 9) 查询性能和索引（简单-中等）
- 在有益的地方添加 SQLite 索引（例如，`notes.title`、标签的连接表）。
- 验证改进的查询计划，并通过测试更大数据集确保没有性能倒退。

## 10) 测试覆盖率改进（简单）
- 添加覆盖以下内容的测试：
  - 每个端点的 400/404 场景
  - 批量操作的并发/事务行为
  - 搜索、分页和乐观更新的前端集成测试（可以是模拟或轻量级的）

## 11) 可部署到 Vercel（中等-复杂）
- Vite + React 前端：
  - 添加带有 `build` 和 `preview` 脚本的 `package.json`，并配置 Vite 输出到 `frontend/dist`（或 `frontend/ui/dist`）。
  - 添加 `vercel.json`，将项目根目录设置为 `week5/frontend`，`outputDirectory` 设置为 `dist`。
  - 在构建时注入 `VITE_API_BASE_URL` 以指向 API。
- Vercel 上的 API（选项 A，无服务器 FastAPI）：
  - 创建 `week5/api/index.py`，从 `backend/app/main.py` 导入 FastAPI `app`。
  - 确保 Python 依赖项可供 Vercel 使用（为函数使用 `pyproject.toml` 或 `requirements.txt`）。
  - 配置 CORS 以允许 Vercel 前端源。
  - 更新 `vercel.json`，将 `/api/*` 路由到 Python 函数，并为其他路由提供 React 应用。
- 在其他地方部署 API（选项 B）：
  - 将后端部署到 Fly.io 或 Render 等服务。
  - 配置 Vercel 前端通过 `VITE_API_BASE_URL` 使用外部 API，并设置任何所需的重写/代理。
- 在 `README.md` 中添加简短的部署指南，包括环境变量、构建命令和回滚。
