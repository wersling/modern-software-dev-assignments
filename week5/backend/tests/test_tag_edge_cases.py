"""
Tag edge cases and boundary condition tests.

Tests edge cases, empty inputs, and boundary conditions for tag functionality.
"""
import pytest


def test_create_tag_empty_name(client):
    """Test creating a tag with empty name."""
    payload = {"name": ""}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 422


def test_create_tag_whitespace_only(client):
    """Test creating a tag with whitespace-only name." """
    payload = {"name": "   \t  "}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 422


def test_attach_empty_tag_list(client):
    """Test attaching an empty list of tags to a note."""
    # Create a note
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Attach empty tag list - should fail validation
    attach_payload = {"tag_ids": []}
    r = client.post(f"/notes/{note_id}/tags", json=attach_payload)
    assert r.status_code == 422  # Validation error: tag_ids must have at least 1 element


def test_attach_many_tags_to_note(client):
    """Test attaching many tags to a single note."""
    # Create a note
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Create many tags
    tag_ids = []
    num_tags = 20
    for i in range(num_tags):
        payload = {"name": f"Tag{i}"}
        r = client.post("/tags/", json=payload)
        assert r.status_code == 201
        tag_ids.append(r.json()["id"])

    # Attach all tags
    attach_payload = {"tag_ids": tag_ids}
    r = client.post(f"/notes/{note_id}/tags", json=attach_payload)
    assert r.status_code == 200
    data = r.json()
    assert len(data["tags"]) == num_tags


def test_list_tags_empty_database(client):
    """Test listing tags when database is empty."""
    r = client.get("/tags/")
    assert r.status_code == 200
    tags = r.json()
    assert len(tags) == 0


def test_search_tags_no_results(client):
    """Test searching tags with a term that has no matches."""
    # Create some tags
    for name in ["Python", "JavaScript", "Docker"]:
        payload = {"name": name}
        client.post("/tags/", json=payload)

    # Search for non-existent tag
    r = client.get("/tags/", params={"search": "NonExistent"})
    assert r.status_code == 200
    tags = r.json()
    assert len(tags) == 0


def test_search_tags_special_characters(client):
    """Test searching tags with special characters."""
    # Create tags with special characters
    for name in ["C++", "C#", ".NET", "Node.js"]:
        payload = {"name": name}
        r = client.post("/tags/", json=payload)
        assert r.status_code == 201

    # Search for "."
    r = client.get("/tags/", params={"search": "."})
    assert r.status_code == 200
    tags = r.json()
    assert len(tags) >= 2  # .NET and Node.js


def test_search_tags_sql_injection_attempt(client):
    """Test that search handles SQL special characters safely."""
    # Create a normal tag
    payload = {"name": "Python"}
    client.post("/tags/", json=payload)

    # Try SQL injection in search
    r = client.get("/tags/", params={"search": "'; DROP TABLE tags; --"})
    assert r.status_code == 200  # Should not error
    tags = r.json()
    # Should just return empty or filtered results, not crash


def test_tag_name_with_unicode(client):
    """Test creating tags with unicode characters."""
    # Test various unicode characters
    # Note: Leading/trailing whitespace will be stripped by the schema
    unicode_names = [
        "中文标签",
        "日本語タグ",
        "태그",
        "Тег",
        "etiqueta",  # " etiqueta" with leading space will be stripped to "etiqueta"
        "🐍 Python",
    ]

    for i, name in enumerate(unicode_names):
        payload = {"name": name}
        r = client.post("/tags/", json=payload)
        assert r.status_code == 201, f"Failed to create tag: {name}"
        data = r.json()
        assert data["name"] == name

    # Also test that leading/trailing whitespace is stripped
    # Use a different name to avoid duplicate tag error
    payload = {"name": "  spaced  "}  # Has leading and trailing spaces
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "spaced"  # Whitespace stripped

    # Verify all tags are in the list
    r = client.get("/tags/")
    assert r.status_code == 200
    tags = r.json()
    for name in unicode_names:
        assert any(tag["name"] == name for tag in tags)


def test_tag_name_case_preserved_on_create(client):
    """Test that tag name case is preserved when created."""
    test_cases = [
        "python",
        "Python",
        "PYTHON",
        "PyThOn",
    ]

    created_names = []
    for name in test_cases:
        payload = {"name": name}
        r = client.post("/tags/", json=payload)
        # Should fail after first due to case-insensitive unique constraint
        if name == test_cases[0]:
            assert r.status_code == 201
            created_names.append(r.json()["name"])
        else:
            assert r.status_code == 400

    # First tag's case should be preserved
    assert created_names[0] == test_cases[0]


def test_get_single_tag_by_filtering_list(client):
    """Test getting a single tag by filtering the tag list."""
    # Create a specific tag
    payload = {"name": "SpecificTag"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201

    # Search for it
    r = client.get("/tags/", params={"search": "SpecificTag"})
    assert r.status_code == 200
    tags = r.json()
    assert len(tags) == 1
    assert tags[0]["name"] == "SpecificTag"


def test_concurrent_tag_attachment_idempotency(client):
    """Test that attaching the same tag multiple times is idempotent."""
    # Create a note and tag
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    note_id = r.json()["id"]

    tag_payload = {"name": "ConcurrentTag"}
    r = client.post("/tags/", json=tag_payload)
    tag_id = r.json()["id"]

    # Attach the same tag 5 times
    for _ in range(5):
        attach_payload = {"tag_ids": [tag_id]}
        r = client.post(f"/notes/{note_id}/tags", json=attach_payload)
        assert r.status_code == 200
        data = r.json()
        assert len(data["tags"]) == 1  # Should only have one tag

    # Verify only one association exists
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    data = r.json()
    assert len(data["tags"]) == 1
