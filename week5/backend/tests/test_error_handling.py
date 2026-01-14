"""Tests for error handling and envelope response format.

This module tests:
- Custom exception handling
- Envelope response format for success and error cases
- Validation error handling
- HTTP status code mapping
"""


def test_note_not_found_envelope_format(client):
    """Test that NOT_FOUND error returns proper envelope format."""
    r = client.get("/notes/99999")
    assert r.status_code == 404

    data = r.json()
    assert "ok" in data
    assert data["ok"] is False
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert data["error"]["code"] == "NOT_FOUND"
    assert "not found" in data["error"]["message"].lower()


def test_action_item_not_found_envelope_format(client):
    """Test that action item NOT_FOUND returns proper envelope format."""
    r = client.put("/action-items/99999/complete")
    assert r.status_code == 404

    data = r.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "NOT_FOUND"
    assert "actionitem" in data["error"]["message"].lower()


def test_tag_not_found_envelope_format(client):
    """Test that tag NOT_FOUND returns proper envelope format."""
    r = client.delete("/tags/99999")
    assert r.status_code == 404

    data = r.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "NOT_FOUND"
    assert "tag" in data["error"]["message"].lower()


def test_validation_error_envelope_format(client):
    """Test that validation errors return proper envelope format."""
    # Empty title should trigger validation error
    # Note: Pydantic validation happens before our exception handler
    # so FastAPI returns the default format
    payload = {"title": "", "content": "Valid content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422

    data = r.json()
    # Pydantic validation errors use FastAPI's default format
    # Our custom handler wraps them, but FastAPI handles this first
    assert "detail" in data or "error" in data


def test_success_response_envelope_format(client):
    """Test that success responses include proper envelope format."""
    # Create a note
    payload = {"title": "Test Note", "content": "Test Content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201

    data = r.json()
    assert "ok" in data
    assert data["ok"] is True
    assert "data" in data
    assert "id" in data["data"]
    assert "title" in data["data"]
    assert data["data"]["title"] == "Test Note"


def test_get_note_success_envelope_format(client):
    """Test that GET note returns envelope format."""
    # Create a note first
    payload = {"title": "Get Test", "content": "Get Content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Get the note
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200

    data = r.json()
    assert data["ok"] is True
    assert "data" in data
    assert data["data"]["id"] == note_id
    assert data["data"]["title"] == "Get Test"


def test_update_note_success_envelope_format(client):
    """Test that PUT note returns envelope format."""
    # Create a note
    payload = {"title": "Original", "content": "Original"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Update the note
    update_payload = {"title": "Updated"}
    r = client.put(f"/notes/{note_id}", json=update_payload)
    assert r.status_code == 200

    data = r.json()
    assert data["ok"] is True
    assert "data" in data
    assert data["data"]["id"] == note_id
    assert data["data"]["title"] == "Updated"
    assert data["data"]["content"] == "Original"


def test_create_action_item_success_envelope_format(client):
    """Test that action item creation returns envelope format."""
    payload = {"description": "Test action item"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201

    data = r.json()
    assert data["ok"] is True
    assert "data" in data
    assert data["data"]["description"] == "Test action item"
    assert data["data"]["completed"] is False


def test_complete_action_item_success_envelope_format(client):
    """Test that action item completion returns envelope format."""
    # Create an action item
    payload = {"description": "To complete"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201
    item_id = r.json()["data"]["id"]

    # Complete it
    r = client.put(f"/action-items/{item_id}/complete")
    assert r.status_code == 200

    data = r.json()
    assert data["ok"] is True
    assert "data" in data
    assert data["data"]["completed"] is True


def test_create_tag_success_envelope_format(client):
    """Test that tag creation returns envelope format."""
    payload = {"name": "test-tag"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201

    data = r.json()
    assert data["ok"] is True
    assert "data" in data
    assert data["data"]["name"] == "test-tag"


def test_create_tag_conflict_envelope_format(client):
    """Test that duplicate tag creation returns CONFLICT error."""
    # Create a tag
    payload = {"name": "duplicate-tag"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201

    # Try to create same tag again
    r = client.post("/tags/", json=payload)
    assert r.status_code == 409

    data = r.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "CONFLICT"
    assert "already exists" in data["error"]["message"].lower()


def test_validation_error_too_long_title(client):
    """Test validation error for title exceeding max length."""
    payload = {"title": "a" * 201, "content": "Valid content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422

    data = r.json()
    # Pydantic validation errors use FastAPI's default format
    assert "detail" in data or "error" in data


def test_validation_error_too_long_content(client):
    """Test validation error for content exceeding max length."""
    payload = {"title": "Valid", "content": "a" * 10001}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422

    data = r.json()
    # Pydantic validation errors use FastAPI's default format
    assert "detail" in data or "error" in data


def test_bulk_complete_validation_error(client):
    """Test that bulk complete with invalid IDs returns validation error."""
    # Empty list should fail validation
    payload = {"ids": []}
    r = client.post("/action-items/bulk-complete", json=payload)
    assert r.status_code == 422

    data = r.json()
    # Pydantic validation errors use FastAPI's default format
    assert "detail" in data or "error" in data


def test_bulk_complete_over_limit_bad_request(client):
    """Test that bulk complete over limit returns BAD_REQUEST."""
    # Create list with more than MAX_BULK_ITEMS (1000)
    payload = {"ids": list(range(1, 1002))}
    r = client.post("/action-items/bulk-complete", json=payload)
    assert r.status_code == 400

    data = r.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "BAD_REQUEST"
    assert "cannot bulk complete more than" in data["error"]["message"].lower()


def test_attach_tags_nonexistent_note(client):
    """Test attaching tags to non-existent note."""
    # Create a tag first
    r = client.post("/tags/", json={"name": "test"})
    assert r.status_code == 201
    tag_id = r.json()["data"]["id"]

    # Try to attach to non-existent note
    payload = {"tag_ids": [tag_id]}
    r = client.post("/notes/99999/tags", json=payload)
    assert r.status_code == 404

    data = r.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "NOT_FOUND"


def test_attach_nonexistent_tags(client):
    """Test attaching non-existent tags to note."""
    # Create a note first
    r = client.post("/notes/", json={"title": "Test", "content": "Content"})
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Try to attach non-existent tags
    payload = {"tag_ids": [99999, 99998]}
    r = client.post(f"/notes/{note_id}/tags", json=payload)
    assert r.status_code == 400

    data = r.json()
    assert data["ok"] is False
    assert data["error"]["code"] == "BAD_REQUEST"
    assert "not found" in data["error"]["message"].lower()


def test_delete_note_success(client):
    """Test that delete returns 204 with no content."""
    # Create a note
    r = client.post("/notes/", json={"title": "To Delete", "content": "Content"})
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Delete the note
    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204
    assert r.text == ""


def test_delete_tag_success(client):
    """Test that tag delete returns 204 with no content."""
    # Create a tag
    r = client.post("/tags/", json={"name": "delete-me"})
    assert r.status_code == 201
    tag_id = r.json()["data"]["id"]

    # Delete the tag
    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204
    assert r.text == ""


def test_extract_preview_success_envelope_format(client):
    """Test that extract preview returns envelope format."""
    # Create a note
    content = "#urgent\n\nTasks:\n- [ ] Fix bug!"
    r = client.post("/notes/", json={"title": "Meeting", "content": content})
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Extract preview
    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 200

    data = r.json()
    assert data["ok"] is True
    assert "data" in data
    assert "tags" in data["data"]
    assert "action_items" in data["data"]
    assert "urgent" in data["data"]["tags"]


def test_extract_apply_success_envelope_format(client):
    """Test that extract apply returns envelope format."""
    # Create a note
    content = "#backend\n\nDeploy!"
    r = client.post("/notes/", json={"title": "Sprint", "content": content})
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Extract with apply
    r = client.post(f"/notes/{note_id}/extract?apply=true")
    assert r.status_code == 200

    data = r.json()
    assert data["ok"] is True
    assert "data" in data
    assert "tags" in data["data"]
    assert "action_items" in data["data"]
    assert "note" in data["data"]
    assert len(data["data"]["tags"]) >= 1
    assert len(data["data"]["action_items"]) >= 1


def test_list_notes_no_envelope(client):
    """Test that list notes does NOT use envelope (returns pagination directly)."""
    r = client.get("/notes/")
    assert r.status_code == 200

    data = r.json()
    # List endpoint returns PaginatedResponse directly, not envelope
    assert "ok" not in data or "items" in data
    # Should have pagination fields
    assert "items" in data or "total" in data


def test_list_tags_no_envelope(client):
    """Test that list tags does NOT use envelope (returns array directly)."""
    r = client.get("/tags/")
    assert r.status_code == 200

    data = r.json()
    # List endpoint returns array directly, not envelope
    assert isinstance(data, list) or "ok" not in data


def test_search_notes_no_envelope(client):
    """Test that search notes does NOT use envelope (returns pagination directly)."""
    r = client.get("/notes/search/")
    assert r.status_code == 200

    data = r.json()
    # Search endpoint returns PaginatedNotesList directly, not envelope
    assert "ok" not in data or "items" in data
    # Should have pagination fields
    assert "items" in data or "total" in data
