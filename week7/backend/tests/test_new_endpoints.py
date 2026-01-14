"""测试新增端点和输入验证功能"""

from fastapi.testclient import TestClient


def test_delete_note(client: TestClient):
    """测试删除笔记端点"""
    # 创建一个测试笔记
    response = client.post("/notes/", json={"title": "Test Note", "content": "Test content"})
    note_id = response.json()["id"]
    assert response.status_code == 201

    # 删除笔记
    response = client.delete(f"/notes/{note_id}")
    assert response.status_code == 204
    assert response.content == b""

    # 尝试删除不存在的笔记
    response = client.delete("/notes/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_get_action_item(client: TestClient):
    """测试获取单个 action item 端点"""
    # 创建一个测试 action item
    response = client.post("/action-items/", json={"description": "Test action"})
    item_id = response.json()["id"]
    assert response.status_code == 201

    # 获取单个 action item
    response = client.get(f"/action-items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["description"] == "Test action"
    assert data["completed"] is False

    # 尝试获取不存在的 item
    response = client.get("/action-items/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Action item not found"


def test_delete_action_item(client: TestClient):
    """测试删除 action item 端点"""
    # 创建一个测试 action item
    response = client.post("/action-items/", json={"description": "Test action"})
    item_id = response.json()["id"]
    assert response.status_code == 201

    # 删除 action item
    response = client.delete(f"/action-items/{item_id}")
    assert response.status_code == 204
    assert response.content == b""

    # 尝试删除不存在的 item
    response = client.delete("/action-items/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Action item not found"


def test_note_create_validation_empty_title(client: TestClient):
    """测试空标题验证"""
    response = client.post("/notes/", json={"title": "", "content": "content"})
    assert response.status_code == 422


def test_note_create_validation_whitespace_only_title(client: TestClient):
    """测试纯空格标题验证"""
    response = client.post("/notes/", json={"title": "   ", "content": "content"})
    assert response.status_code == 422


def test_note_create_validation_title_too_long(client: TestClient):
    """测试标题超过200字符验证"""
    long_title = "a" * 201
    response = client.post("/notes/", json={"title": long_title, "content": "content"})
    assert response.status_code == 422


def test_note_create_validation_empty_content(client: TestClient):
    """测试空内容验证"""
    response = client.post("/notes/", json={"title": "Title", "content": ""})
    assert response.status_code == 422


def test_note_create_validation_whitespace_only_content(client: TestClient):
    """测试纯空格内容验证"""
    response = client.post("/notes/", json={"title": "Title", "content": "   "})
    assert response.status_code == 422


def test_note_create_validation_strips_whitespace(client: TestClient):
    """测试自动去除前后空格"""
    response = client.post(
        "/notes/", json={"title": "  Valid Title  ", "content": "  Valid content  "}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Valid Title"
    assert data["content"] == "Valid content"


def test_action_item_create_validation_empty_description(client: TestClient):
    """测试空描述验证"""
    response = client.post("/action-items/", json={"description": ""})
    assert response.status_code == 422


def test_action_item_create_validation_whitespace_only_description(client: TestClient):
    """测试纯空格描述验证"""
    response = client.post("/action-items/", json={"description": "   "})
    assert response.status_code == 422


def test_action_item_create_validation_strips_whitespace(client: TestClient):
    """测试描述自动去除前后空格"""
    response = client.post("/action-items/", json={"description": "  Valid action  "})
    assert response.status_code == 201
    assert response.json()["description"] == "Valid action"
