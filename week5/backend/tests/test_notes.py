def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_update_note(client):
    # Create a note first
    payload = {"title": "Original Title", "content": "Original Content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Update both fields
    update_payload = {"title": "Updated Title", "content": "Updated Content"}
    r = client.put(f"/notes/{note_id}", json=update_payload)
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"
    assert data["id"] == note_id

    # Partial update - only title
    partial_update = {"title": "Partial Title"}
    r = client.put(f"/notes/{note_id}", json=partial_update)
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Partial Title"
    assert data["content"] == "Updated Content"  # Should remain unchanged

    # Partial update - only content
    content_update = {"content": "New Content Only"}
    r = client.put(f"/notes/{note_id}", json=content_update)
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Partial Title"  # Should remain unchanged
    assert data["content"] == "New Content Only"


def test_update_note_not_found(client):
    update_payload = {"title": "Updated", "content": "Content"}
    r = client.put("/notes/99999", json=update_payload)
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


def test_delete_note(client):
    # Create a note first
    payload = {"title": "To Delete", "content": "This will be deleted"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Delete the note
    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204
    assert r.text == ""

    # Verify it's gone
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/notes/99999")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


def test_get_note(client):
    # Create a note
    payload = {"title": "Get Test", "content": "Testing get endpoint"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Get the note
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == note_id
    assert data["title"] == "Get Test"
    assert data["content"] == "Testing get endpoint"
    assert "created_at" in data


def test_get_note_not_found(client):
    r = client.get("/notes/99999")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()
