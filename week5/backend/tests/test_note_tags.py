def test_attach_tags_to_note(client):
    """Test attaching tags to a note."""
    # Create a note
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Create tags
    tag1_payload = {"name": "Python"}
    tag2_payload = {"name": "FastAPI"}
    r1 = client.post("/tags/", json=tag1_payload)
    r2 = client.post("/tags/", json=tag2_payload)
    assert r1.status_code == 201
    assert r2.status_code == 201
    tag1_id = r1.json()["data"]["id"]
    tag2_id = r2.json()["data"]["id"]

    # Attach tags to note
    attach_payload = {"tag_ids": [tag1_id, tag2_id]}
    r = client.post(f"/notes/{note_id}/tags", json=attach_payload)
    assert r.status_code == 200
    data = r.json()
    assert len(data["data"]["tags"]) == 2
    tag_names = [tag["name"] for tag in data["data"]["tags"]]
    assert "Python" in tag_names
    assert "FastAPI" in tag_names


def test_attach_tags_duplicate_handling(client):
    """Test that duplicate tag IDs are handled correctly."""
    # Create a note
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Create a tag
    tag_payload = {"name": "Docker"}
    r = client.post("/tags/", json=tag_payload)
    assert r.status_code == 201
    tag_id = r.json()["data"]["id"]

    # Attach the same tag twice (with duplicate IDs in request)
    attach_payload = {"tag_ids": [tag_id, tag_id, tag_id]}
    r = client.post(f"/notes/{note_id}/tags", json=attach_payload)
    assert r.status_code == 200
    data = r.json()
    assert len(data["data"]["tags"]) == 1
    assert data["data"]["tags"][0]["name"] == "Docker"

    # Attach again (should not duplicate)
    attach_payload = {"tag_ids": [tag_id]}
    r = client.post(f"/notes/{note_id}/tags", json=attach_payload)
    assert r.status_code == 200
    data = r.json()
    assert len(data["data"]["tags"]) == 1


def test_attach_tags_non_existent_tag(client):
    """Test attaching non-existent tags to a note."""
    # Create a note
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Try to attach non-existent tags
    attach_payload = {"tag_ids": [99999, 88888]}
    r = client.post(f"/notes/{note_id}/tags", json=attach_payload)
    assert r.status_code == 400
    assert "not found" in r.json()["error"]["message"].lower()


def test_attach_tags_to_non_existent_note(client):
    """Test attaching tags to a non-existent note."""
    # Create a tag
    tag_payload = {"name": "React"}
    r = client.post("/tags/", json=tag_payload)
    assert r.status_code == 201
    tag_id = r.json()["data"]["id"]

    # Try to attach to non-existent note
    attach_payload = {"tag_ids": [tag_id]}
    r = client.post("/notes/99999/tags", json=attach_payload)
    assert r.status_code == 404
    assert "not found" in r.json()["error"]["message"].lower()


def test_remove_tag_from_note(client):
    """Test removing a tag from a note."""
    # Create a note
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Create tags
    tag1_payload = {"name": "Python"}
    tag2_payload = {"name": "FastAPI"}
    r1 = client.post("/tags/", json=tag1_payload)
    r2 = client.post("/tags/", json=tag2_payload)
    tag1_id = r1.json()["data"]["id"]
    tag2_id = r2.json()["data"]["id"]

    # Attach tags to note
    attach_payload = {"tag_ids": [tag1_id, tag2_id]}
    r = client.post(f"/notes/{note_id}/tags", json=attach_payload)
    assert r.status_code == 200
    assert len(r.json()["data"]["tags"]) == 2

    # Remove one tag
    r = client.delete(f"/notes/{note_id}/tags/{tag1_id}")
    assert r.status_code == 200
    data = r.json()
    assert len(data["data"]["tags"]) == 1
    assert data["data"]["tags"][0]["name"] == "FastAPI"


def test_remove_tag_from_note_not_associated(client):
    """Test removing a tag that is not associated with the note."""
    # Create a note
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Create a tag (but don't attach it)
    tag_payload = {"name": "Kubernetes"}
    r = client.post("/tags/", json=tag_payload)
    assert r.status_code == 201
    tag_id = r.json()["data"]["id"]

    # Try to remove the tag (should fail)
    r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 404
    assert "not associated" in r.json()["error"]["message"].lower()


def test_remove_tag_from_non_existent_note(client):
    """Test removing a tag from a non-existent note."""
    # Create a tag
    tag_payload = {"name": "GraphQL"}
    r = client.post("/tags/", json=tag_payload)
    assert r.status_code == 201
    tag_id = r.json()["data"]["id"]

    # Try to remove from non-existent note
    r = client.delete(f"/notes/99999/tags/{tag_id}")
    assert r.status_code == 404
    assert "not found" in r.json()["error"]["message"].lower()


def test_get_note_includes_tags(client):
    """Test that getting a note includes its tags."""
    # Create a note
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Create and attach tags
    tag1_payload = {"name": "Python"}
    tag2_payload = {"name": "FastAPI"}
    r1 = client.post("/tags/", json=tag1_payload)
    r2 = client.post("/tags/", json=tag2_payload)
    tag1_id = r1.json()["data"]["id"]
    tag2_id = r2.json()["data"]["id"]

    attach_payload = {"tag_ids": [tag1_id, tag2_id]}
    client.post(f"/notes/{note_id}/tags", json=attach_payload)

    # Get the note
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "tags" in data["data"]
    assert len(data["data"]["tags"]) == 2
    tag_names = [tag["name"] for tag in data["data"]["tags"]]
    assert "Python" in tag_names
    assert "FastAPI" in tag_names


def test_list_notes_filter_by_tag_id(client):
    """Test listing notes filtered by tag ID."""
    # Create notes
    note1_payload = {"title": "Python Note", "content": "Python content"}
    note2_payload = {"title": "JavaScript Note", "content": "JS content"}
    r1 = client.post("/notes/", json=note1_payload)
    r2 = client.post("/notes/", json=note2_payload)
    note1_id = r1.json()["data"]["id"]
    note2_id = r2.json()["data"]["id"]

    # Create tags
    tag1_payload = {"name": "Python"}
    tag2_payload = {"name": "JavaScript"}
    r1 = client.post("/tags/", json=tag1_payload)
    r2 = client.post("/tags/", json=tag2_payload)
    tag1_id = r1.json()["data"]["id"]
    tag2_id = r2.json()["data"]["id"]

    # Attach tags to notes
    client.post(f"/notes/{note1_id}/tags", json={"tag_ids": [tag1_id]})
    client.post(f"/notes/{note2_id}/tags", json={"tag_ids": [tag2_id]})

    # List notes filtered by tag_id
    r = client.get("/notes/", params={"tag_id": tag1_id})
    assert r.status_code == 200
    response = r.json()
    notes = response["items"]
    assert len(notes) == 1
    assert notes[0]["title"] == "Python Note"
    assert len(notes[0]["tags"]) == 1
    assert notes[0]["tags"][0]["name"] == "Python"


def test_list_notes_filter_by_tag_name(client):
    """Test listing notes filtered by tag name (case-insensitive)."""
    # Create notes
    note1_payload = {"title": "Docker Note", "content": "Docker content"}
    note2_payload = {"title": "Kubernetes Note", "content": "K8s content"}
    r1 = client.post("/notes/", json=note1_payload)
    r2 = client.post("/notes/", json=note2_payload)
    note1_id = r1.json()["data"]["id"]
    note2_id = r2.json()["data"]["id"]

    # Create tags
    tag1_payload = {"name": "Docker"}
    tag2_payload = {"name": "Kubernetes"}
    r1 = client.post("/tags/", json=tag1_payload)
    r2 = client.post("/tags/", json=tag2_payload)
    tag1_id = r1.json()["data"]["id"]
    tag2_id = r2.json()["data"]["id"]

    # Attach tags to notes
    client.post(f"/notes/{note1_id}/tags", json={"tag_ids": [tag1_id]})
    client.post(f"/notes/{note2_id}/tags", json={"tag_ids": [tag2_id]})

    # List notes filtered by tag name (case-insensitive)
    r = client.get("/notes/", params={"tag": "docker"})
    assert r.status_code == 200
    response = r.json()
    notes = response["items"]
    assert len(notes) == 1
    assert notes[0]["title"] == "Docker Note"

    # Try with different case
    r = client.get("/notes/", params={"tag": "DOCKER"})
    assert r.status_code == 200
    response = r.json()
    notes = response["items"]
    assert len(notes) == 1


def test_search_notes_with_tag_filter(client):
    """Test searching notes with tag filter."""
    # Create notes
    note1_payload = {"title": "Python Tutorial", "content": "Learn Python programming"}
    note2_payload = {"title": "FastAPI Guide", "content": "Build APIs with Python"}
    r1 = client.post("/notes/", json=note1_payload)
    r2 = client.post("/notes/", json=note2_payload)
    note1_id = r1.json()["data"]["id"]
    note2_id = r2.json()["data"]["id"]

    # Create tags
    tag1_payload = {"name": "Python"}
    tag2_payload = {"name": "Backend"}
    r1 = client.post("/tags/", json=tag1_payload)
    r2 = client.post("/tags/", json=tag2_payload)
    tag1_id = r1.json()["data"]["id"]
    tag2_id = r2.json()["data"]["id"]

    # Attach tags: note1 gets both tags, note2 gets only Backend
    client.post(f"/notes/{note1_id}/tags", json={"tag_ids": [tag1_id, tag2_id]})
    client.post(f"/notes/{note2_id}/tags", json={"tag_ids": [tag2_id]})

    # Search for "Python" without tag filter (should return both notes)
    r = client.get("/notes/search/", params={"q": "python"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2

    # Search for "Python" with tag_id filter (should return only note1)
    r = client.get("/notes/search/", params={"q": "python", "tag_id": tag1_id})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Python Tutorial"

    # Search with tag name filter
    r = client.get("/notes/search/", params={"q": "python", "tag": "python"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Python Tutorial"


def test_note_tags_persistence(client):
    """Test that note-tag associations persist across note updates."""
    # Create a note
    note_payload = {"title": "Original Title", "content": "Original content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Create and attach tags
    tag_payload = {"name": "Persistent"}
    r = client.post("/tags/", json=tag_payload)
    tag_id = r.json()["data"]["id"]

    client.post(f"/notes/{note_id}/tags", json={"tag_ids": [tag_id]})

    # Update the note
    update_payload = {"title": "Updated Title"}
    r = client.put(f"/notes/{note_id}", json=update_payload)
    assert r.status_code == 200
    assert len(r.json()["data"]["tags"]) == 1
    assert r.json()["data"]["tags"][0]["name"] == "Persistent"

    # Get the note to verify tags are still there
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert len(r.json()["data"]["tags"]) == 1
    assert r.json()["data"]["tags"][0]["name"] == "Persistent"


def test_cascade_delete_tag_from_note(client):
    """Test that deleting a note removes its tag associations."""
    # Create a note
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Create and attach tags
    tag_payload = {"name": "ToDelete"}
    r = client.post("/tags/", json=tag_payload)
    tag_id = r.json()["data"]["id"]

    client.post(f"/notes/{note_id}/tags", json={"tag_ids": [tag_id]})

    # Delete the note
    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    # Tag should still exist (no CASCADE from note to tag)
    # List all tags to verify the tag still exists
    r = client.get("/tags/")
    assert r.status_code == 200
    tags = r.json()
    assert any(tag["id"] == tag_id for tag in tags)
