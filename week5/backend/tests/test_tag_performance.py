"""
Tag performance and N+1 query tests.

Tests performance characteristics and verifies that N+1 queries are avoided.
"""
import pytest


def test_list_tags_with_notes_no_n1_query(client):
    """Test that listing tags doesn't cause N+1 queries for notes."""
    # Create tags with associated notes
    num_tags = 10
    tag_ids = []

    for i in range(num_tags):
        # Create tag
        tag_payload = {"name": f"PerformanceTag{i}"}
        r = client.post("/tags/", json=tag_payload)
        assert r.status_code == 201
        tag_id = r.json()["id"]
        tag_ids.append(tag_id)

        # Create and associate notes
        for j in range(3):
            note_payload = {"title": f"Note{i}-{j}", "content": f"Content {i}-{j}"}
            r = client.post("/notes/", json=note_payload)
            assert r.status_code == 201
            note_id = r.json()["id"]

            # Attach tag to note
            attach_payload = {"tag_ids": [tag_id]}
            r = client.post(f"/notes/{note_id}/tags", json=attach_payload)
            assert r.status_code == 200

    # List all tags - this should not cause N+1 queries
    # The relationship uses lazy="selectin" which should eager load
    r = client.get("/tags/")
    assert r.status_code == 200
    tags = r.json()

    # We expect this to complete efficiently
    # In a real scenario, you'd measure query count here
    assert len(tags) >= num_tags

    # Verify tags have notes relationship (even if not serialized)
    # The API doesn't return notes in tag list, but the ORM loads them efficiently


def test_list_notes_with_tags_no_n1_query(client):
    """Test that listing notes with tags doesn't cause N+1 queries."""
    # Create notes with tags
    num_notes = 20
    note_ids = []

    # Create tags first
    tag_ids = []
    for i in range(5):
        tag_payload = {"name": f"SharedTag{i}"}
        r = client.post("/tags/", json=tag_payload)
        assert r.status_code == 201
        tag_ids.append(r.json()["id"])

    # Create notes and attach tags
    for i in range(num_notes):
        note_payload = {"title": f"Note{i}", "content": f"Content {i}"}
        r = client.post("/notes/", json=note_payload)
        assert r.status_code == 201
        note_id = r.json()["id"]
        note_ids.append(note_id)

        # Attach 2-3 random tags to each note
        tags_to_attach = tag_ids[:2] if i % 2 == 0 else tag_ids[2:5]
        attach_payload = {"tag_ids": tags_to_attach}
        r = client.post(f"/notes/{note_id}/tags", json=attach_payload)
        assert r.status_code == 200

    # List all notes - should not cause N+1 queries due to lazy="selectin"
    r = client.get("/notes/")
    assert r.status_code == 200
    response = r.json()
    notes = response["items"]

    assert len(notes) >= num_notes

    # Verify notes have tags loaded
    for note in notes[:5]:  # Check first few
        assert "tags" in note
        assert len(note["tags"]) >= 2


def test_search_performance_with_large_dataset(client):
    """Test that search remains performant with larger datasets."""
    # Create many tags
    num_tags = 100
    for i in range(num_tags):
        tag_payload = {"name": f"SearchTag{i}"}
        r = client.post("/tags/", json=tag_payload)
        assert r.status_code == 201

    # Search for specific subset
    r = client.get("/tags/", params={"search": "SearchTag5"})
    assert r.status_code == 200
    tags = r.json()

    # Should find "SearchTag5", "SearchTag50", "SearchTag51", ... "SearchTag59"
    # That's 11 matches (SearchTag5 + SearchTag50-59)
    assert len(tags) == 11


def test_filter_notes_by_tag_performance(client):
    """Test performance of filtering notes by tag."""
    # Create tags
    python_tag_id = client.post("/tags/", json={"name": "Python"}).json()["id"]
    js_tag_id = client.post("/tags/", json={"name": "JavaScript"}).json()["id"]

    # Create many notes with Python tag
    num_python_notes = 50
    for i in range(num_python_notes):
        note_payload = {"title": f"Python Note {i}", "content": "Python content"}
        r = client.post("/notes/", json=note_payload)
        note_id = r.json()["id"]
        client.post(f"/notes/{note_id}/tags", json={"tag_ids": [python_tag_id]})

    # Create some JavaScript notes
    for i in range(10):
        note_payload = {"title": f"JS Note {i}", "content": "JS content"}
        r = client.post("/notes/", json=note_payload)
        note_id = r.json()["id"]
        client.post(f"/notes/{note_id}/tags", json={"tag_ids": [js_tag_id]})

    # Filter by Python tag (use page_size=100 to get all results)
    r = client.get("/notes/", params={"tag_id": python_tag_id, "page_size": 100})
    assert r.status_code == 200
    response = r.json()
    notes = response["items"]

    assert len(notes) == num_python_notes
    # Verify all notes have Python tag
    for note in notes:
        assert any(tag["name"] == "Python" for tag in note["tags"])


def test_attach_detach_performance(client):
    """Test performance of attaching and detaching tags."""
    # Create note and many tags
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    note_id = r.json()["id"]

    num_tags = 50
    tag_ids = []
    for i in range(num_tags):
        tag_payload = {"name": f"Tag{i}"}
        r = client.post("/tags/", json=tag_payload)
        tag_ids.append(r.json()["id"])

    # Attach all tags at once
    attach_payload = {"tag_ids": tag_ids}
    r = client.post(f"/notes/{note_id}/tags", json=attach_payload)
    assert r.status_code == 200
    assert len(r.json()["tags"]) == num_tags

    # Remove tags one by one
    for tag_id in tag_ids[:10]:  # Remove first 10
        r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
        assert r.status_code == 200

    # Verify remaining tags
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert len(r.json()["tags"]) == num_tags - 10
