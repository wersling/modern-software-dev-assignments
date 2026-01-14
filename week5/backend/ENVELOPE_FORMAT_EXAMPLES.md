# 错误处理和信封响应格式示例

## 概述

本文档展示了任务 7 实现的统一信封响应格式的实际使用示例。

## 成功响应格式

### 示例 1：创建笔记

**请求**：
```bash
POST /notes/
Content-Type: application/json

{
  "title": "Meeting Notes",
  "content": "Discussed project roadmap and milestones"
}
```

**成功响应（201 Created）**：
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "title": "Meeting Notes",
    "content": "Discussed project roadmap and milestones",
    "created_at": "2026-01-14T10:30:00.000000",
    "tags": []
  }
}
```

### 示例 2：获取笔记

**请求**：
```bash
GET /notes/1
```

**成功响应（200 OK）**：
```json
{
  "ok": true,
  "data": {
    "id": 1,
    "title": "Meeting Notes",
    "content": "Discussed project roadmap and milestones",
    "created_at": "2026-01-14T10:30:00.000000",
    "tags": [
      {
        "id": 5,
        "name": "urgent",
        "created_at": "2026-01-14T10:31:00.000000"
      }
    ]
  }
}
```

### 示例 3：创建待办事项

**请求**：
```bash
POST /action-items/
Content-Type: application/json

{
  "description": "Review pull requests"
}
```

**成功响应（201 Created）**：
```json
{
  "ok": true,
  "data": {
    "id": 42,
    "description": "Review pull requests",
    "completed": false,
    "created_at": "2026-01-14T10:35:00.000000"
  }
}
```

### 示例 4：批量完成待办事项

**请求**：
```bash
POST /action-items/bulk-complete
Content-Type: application/json

{
  "ids": [1, 2, 3]
}
```

**成功响应（200 OK）**：
```json
{
  "ok": true,
  "data": {
    "updated": [
      {
        "id": 1,
        "description": "Task 1",
        "completed": true,
        "created_at": "2026-01-14T10:00:00.000000"
      },
      {
        "id": 2,
        "description": "Task 2",
        "completed": true,
        "created_at": "2026-01-14T10:01:00.000000"
      },
      {
        "id": 3,
        "description": "Task 3",
        "completed": true,
        "created_at": "2026-01-14T10:02:00.000000"
      }
    ],
    "total_updated": 3,
    "not_found": []
  }
}
```

### 示例 5：创建标签

**请求**：
```bash
POST /tags/
Content-Type: application/json

{
  "name": "backend"
}
```

**成功响应（201 Created）**：
```json
{
  "ok": true,
  "data": {
    "id": 10,
    "name": "backend",
    "created_at": "2026-01-14T10:40:00.000000"
  }
}
```

## 错误响应格式

### 示例 1：资源未找到（404）

**请求**：
```bash
GET /notes/99999
```

**错误响应（404 Not Found）**：
```json
{
  "ok": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Note with id=99999 not found"
  }
}
```

### 示例 2：验证错误（422）

**请求**：
```bash
POST /notes/
Content-Type: application/json

{
  "title": "",
  "content": "Some content"
}
```

**错误响应（422 Unprocessable Entity）**：
```json
{
  "ok": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "title -> Field required [type=missing, input_value={'content': 'Some content'}, input_type=dict] or title cannot be empty or whitespace only"
  }
}
```

### 示例 3：字段过长（422）

**请求**：
```bash
POST /notes/
Content-Type: application/json

{
  "title": "This title is way too long and exceeds the maximum allowed length of 200 characters...",
  "content": "Valid content"
}
```

**错误响应（422 Unprocessable Entity）**：
```json
{
  "ok": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "title -> String should have at most 200 characters [type=string_too_long, max_length=200, input_value='This title is way too long...']"
  }
}
```

### 示例 4：冲突错误（409）

**请求**：
```bash
POST /tags/
Content-Type: application/json

{
  "name": "backend"
}
# 假设已经存在名为 "backend" 的标签（大小写不敏感）
```

**错误响应（409 Conflict）**：
```json
{
  "ok": false,
  "error": {
    "code": "CONFLICT",
    "message": "Tag conflict: name 'backend' already exists (case-insensitive)"
  }
}
```

### 示例 5：错误请求（400）

**请求**：
```bash
POST /action-items/bulk-complete
Content-Type: application/json

{
  "ids": [1, 2, 3, ..., 1001]
}
```

**错误响应（400 Bad Request）**：
```json
{
  "ok": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "Cannot bulk complete more than 1000 items at once. Received 1001 items."
  }
}
```

### 示例 6：标签不存在（400）

**请求**：
```bash
POST /notes/1/tags
Content-Type: application/json

{
  "tag_ids": [999, 998]
}
```

**错误响应（400 Bad Request）**：
```json
{
  "ok": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "Tags with ids [998, 999] not found"
  }
}
```

## 特殊端点格式

### 分页列表端点（不使用信封格式）

**请求**：
```bash
GET /notes/?page=1&page_size=20
```

**响应（200 OK）**：
```json
{
  "items": [
    {
      "id": 1,
      "title": "Note 1",
      "content": "Content 1",
      "created_at": "2026-01-14T10:00:00.000000",
      "tags": []
    },
    {
      "id": 2,
      "title": "Note 2",
      "content": "Content 2",
      "created_at": "2026-01-14T10:01:00.000000",
      "tags": [
        {
          "id": 1,
          "name": "tag1",
          "created_at": "2026-01-14T09:50:00.000000"
        }
      ]
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 20,
  "total_pages": 2
}
```

**说明**：分页端点不使用信封格式，以避免过度嵌套。

### 删除操作（无内容）

**请求**：
```bash
DELETE /notes/1
```

**响应（204 No Content）**：
```
（无响应体）
```

**说明**：删除操作返回 204 状态码，不包含响应体，符合 REST 最佳实践。

### 列表端点（数组格式）

**请求**：
```bash
GET /tags/
```

**响应（200 OK）**：
```json
[
  {
    "id": 1,
    "name": "python",
    "created_at": "2026-01-14T09:00:00.000000"
  },
  {
    "id": 2,
    "name": "fastapi",
    "created_at": "2026-01-14T09:01:00.000000"
  },
  {
    "id": 3,
    "name": "sqlalchemy",
    "created_at": "2026-01-14T09:02:00.000000"
  }
]
```

**说明**：标签列表端点返回数组格式，不使用信封。

## 客户端使用示例

### JavaScript/TypeScript

```typescript
// 创建笔记
const response = await fetch('/notes/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ title: 'New Note', content: 'Content' })
});

const result = await response.json();

if (result.ok) {
  // 成功响应
  const note = result.data;
  console.log('Created note:', note.id, note.title);
} else {
  // 错误响应
  console.error('Error:', result.error.code, result.error.message);
}
```

### Python

```python
import requests

# 创建笔记
response = requests.post('/notes/', json={
    'title': 'New Note',
    'content': 'Content'
})

result = response.json()

if result['ok']:
    # 成功响应
    note = result['data']
    print(f"Created note: {note['id']} - {note['title']}")
else:
    # 错误响应
    error = result['error']
    print(f"Error {error['code']}: {error['message']}")
```

### cURL

```bash
# 成功响应
curl -X POST http://localhost:8000/notes/ \
  -H "Content-Type: application/json" \
  -d '{"title":"New Note","content":"Content"}' \
  | jq '.'

# 输出：
# {
#   "ok": true,
#   "data": {
#     "id": 1,
#     "title": "New Note",
#     "content": "Content",
#     "created_at": "2026-01-14T10:30:00.000000",
#     "tags": []
#   }
# }

# 错误响应
curl -X GET http://localhost:8000/notes/99999 \
  | jq '.'

# 输出：
# {
#   "ok": false,
#   "error": {
#     "code": "NOT_FOUND",
#     "message": "Note with id=99999 not found"
#   }
# }
```

## 错误代码参考

| 代码 | HTTP状态 | 描述 | 示例场景 |
|------|---------|------|---------|
| `BAD_REQUEST` | 400 | 错误的请求 | 批量操作超过限制、不存在的标签ID |
| `UNAUTHORIZED` | 401 | 未授权 | 需要登录的端点（未实现） |
| `FORBIDDEN` | 403 | 禁止访问 | 权限不足（未实现） |
| `NOT_FOUND` | 404 | 资源未找到 | 获取不存在的笔记/标签/待办事项 |
| `CONFLICT` | 409 | 资源冲突 | 创建重复名称的标签 |
| `VALIDATION_ERROR` | 422 | 验证失败 | 空字符串、字段过长、格式错误 |
| `INTERNAL_ERROR` | 500 | 内部错误 | 未捕获的服务器错误 |

## 总结

统一信封响应格式提供了一致的 API 交互方式：

1. **成功响应**：`{ "ok": true, "data": {...} }`
2. **错误响应**：`{ "ok": false, "error": {...} }`
3. **特殊端点**：分页（直接对象）、删除（204无内容）、列表（数组）

这种格式使得客户端代码更容易处理成功和错误情况，并提供了清晰的错误信息用于调试和用户反馈。
