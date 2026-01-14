def test_create_list_and_patch_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"
    assert "created_at" in data and "updated_at" in data

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/", params={"q": "Hello", "limit": 10, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    note_id = data["id"]
    r = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["title"] == "Updated"


def test_get_note_by_id(client):
    payload = {"title": "Get Test", "content": "Content for get"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    note = r.json()
    assert note["id"] == note_id
    assert note["title"] == "Get Test"

    r = client.get("/notes/99999")
    assert r.status_code == 404


def test_delete_note(client):
    payload = {"title": "Delete Me", "content": "Will be deleted"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404

    r = client.delete("/notes/99999")
    assert r.status_code == 404


def test_note_validation_title_too_long(client):
    payload = {"title": "x" * 201, "content": "Valid content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422


def test_note_validation_content_too_long(client):
    payload = {"title": "Valid", "content": "x" * 10001}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422


def test_note_validation_empty_fields(client):
    payload = {"title": "", "content": "   "}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422


def test_note_validation_strip_whitespace(client):
    payload = {"title": "  Whitespace Test  ", "content": "  Content  "}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Whitespace Test"
    assert data["content"] == "Content"
