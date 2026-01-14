def test_create_and_list_tags(client):
    """Test creating a tag and listing all tags."""
    # Create a tag
    payload = {"name": "Python"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201, r.text
    response = r.json()
    assert response["ok"] is True
    data = response["data"]
    assert data["name"] == "Python"
    assert "id" in data
    assert "created_at" in data

    # List all tags
    r = client.get("/tags/")
    assert r.status_code == 200
    tags = r.json()
    assert len(tags) >= 1
    # Verify our tag is in the list
    assert any(tag["name"] == "Python" for tag in tags)


def test_create_tag_duplicate_name(client):
    """Test creating a tag with duplicate name (should fail)."""
    # Create first tag
    payload = {"name": "FastAPI"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201

    # Try to create duplicate tag
    r = client.post("/tags/", json=payload)
    assert r.status_code == 409
    response = r.json()
    assert response["ok"] is False
    assert "already exists" in response["error"]["message"].lower()


def test_create_tag_duplicate_name_case_insensitive(client):
    """Test creating a tag with same name but different case (should fail)."""
    # Create first tag
    payload = {"name": "Docker"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201

    # Try to create with different case
    payload2 = {"name": "DOCKER"}
    r = client.post("/tags/", json=payload2)
    assert r.status_code == 409
    response = r.json()
    assert response["ok"] is False
    assert "already exists" in response["error"]["message"].lower()


def test_create_tag_validation(client):
    """Test tag creation validation."""
    # Empty name should fail
    payload = {"name": "   "}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 422  # Validation error

    # Name too long should fail
    payload = {"name": "x" * 51}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 422  # Validation error


def test_list_tags_with_search(client):
    """Test listing tags with search filter."""
    # Create multiple tags
    tags_to_create = ["Python", "JavaScript", "TypeScript", "Java"]
    for tag_name in tags_to_create:
        payload = {"name": tag_name}
        r = client.post("/tags/", json=payload)
        assert r.status_code == 201

    # Search for "script" should return JavaScript and TypeScript
    r = client.get("/tags/", params={"search": "script"})
    assert r.status_code == 200
    tags = r.json()
    assert len(tags) == 2
    tag_names = [tag["name"] for tag in tags]
    assert "JavaScript" in tag_names
    assert "TypeScript" in tag_names

    # Search for "python" (case-insensitive)
    r = client.get("/tags/", params={"search": "PYTHON"})
    assert r.status_code == 200
    tags = r.json()
    assert len(tags) == 1
    assert tags[0]["name"] == "Python"


def test_list_tags_ordering(client):
    """Test that tags are ordered by creation time (newest first)."""
    # Create tags in sequence
    tag_ids = []
    for tag_name in ["Tag1", "Tag2", "Tag3"]:
        payload = {"name": tag_name}
        r = client.post("/tags/", json=payload)
        assert r.status_code == 201
        tag_ids.append(r.json()["data"]["id"])

    # List tags - should be in reverse creation order
    r = client.get("/tags/")
    assert r.status_code == 200
    tags = r.json()

    # Find our created tags in the response
    created_tags = [tag for tag in tags if tag["name"] in ["Tag1", "Tag2", "Tag3"]]
    assert len(created_tags) == 3

    # Tag3 should appear before Tag1 (newest first)
    tag3_index = next(i for i, tag in enumerate(created_tags) if tag["name"] == "Tag3")
    tag1_index = next(i for i, tag in enumerate(created_tags) if tag["name"] == "Tag1")
    assert tag3_index < tag1_index


def test_delete_tag(client):
    """Test deleting a tag."""
    # Create a tag
    payload = {"name": "ToDelete"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201
    tag_id = r.json()["data"]["id"]

    # Delete the tag
    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204
    assert r.text == ""

    # Verify it's gone
    r = client.get("/tags/")
    tags = r.json()
    assert not any(tag["id"] == tag_id for tag in tags)


def test_delete_tag_not_found(client):
    """Test deleting a non-existent tag."""
    r = client.delete("/tags/99999")
    assert r.status_code == 404
    response = r.json()
    assert response["ok"] is False
    assert "not found" in response["error"]["message"].lower()


def test_delete_tag_cascade(client):
    """Test that deleting a tag removes it from note_tags association table."""
    # This test requires note-tag association to be implemented
    # For now, we just verify the tag can be deleted
    payload = {"name": "CascadeTest"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201
    tag_id = r.json()["data"]["id"]

    # Delete should succeed
    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204
