"""
Tag integration tests - End-to-end workflow tests.

Tests complete workflows involving tags, notes, and their interactions.
"""
import pytest


def test_complete_tag_lifecycle(client):
    """Test complete lifecycle: create tag → attach to note → query → delete."""
    # Step 1: Create a note
    note_payload = {"title": "Integration Test Note", "content": "Testing tag lifecycle"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Step 2: Create tags
    tags_to_create = ["Development", "Python", "Testing"]
    tag_ids = []
    for tag_name in tags_to_create:
        tag_payload = {"name": tag_name}
        r = client.post("/tags/", json=tag_payload)
        assert r.status_code == 201
        tag_ids.append(r.json()["id"])

    # Step 3: Attach all tags to note
    attach_payload = {"tag_ids": tag_ids}
    r = client.post(f"/notes/{note_id}/tags", json=attach_payload)
    assert r.status_code == 200
    assert len(r.json()["tags"]) == 3

    # Step 4: Verify note has all tags
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    note = r.json()
    assert len(note["tags"]) == 3
    tag_names = {tag["name"] for tag in note["tags"]}
    assert tag_names == set(tags_to_create)

    # Step 5: Filter notes by one tag
    python_tag_id = tag_ids[1]  # "Python"
    r = client.get("/notes/", params={"tag_id": python_tag_id})
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) == 1
    assert notes[0]["id"] == note_id

    # Step 6: Remove one tag
    r = client.delete(f"/notes/{note_id}/tags/{tag_ids[0]}")  # Remove "Development"
    assert r.status_code == 200
    assert len(r.json()["tags"]) == 2

    # Step 7: Delete the note
    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    # Step 8: Verify tags still exist (not deleted when note is deleted)
    r = client.get("/tags/")
    assert r.status_code == 200
    tags = r.json()
    assert len(tags) >= 3

    # Step 9: Clean up - delete tags
    for tag_id in tag_ids:
        r = client.delete(f"/tags/{tag_id}")
        assert r.status_code == 204


def test_multiple_notes_shared_tags(client):
    """Test multiple notes sharing the same tags."""
    # Create tags
    tag_ids = {}
    for tag_name in ["Backend", "API", "FastAPI"]:
        r = client.post("/tags/", json={"name": tag_name})
        tag_ids[tag_name] = r.json()["id"]

    # Create multiple notes with overlapping tags
    notes_data = [
        {"title": "Note 1", "content": "Content 1", "tags": ["Backend", "API"]},
        {"title": "Note 2", "content": "Content 2", "tags": ["Backend", "FastAPI"]},
        {"title": "Note 3", "content": "Content 3", "tags": ["API", "FastAPI"]},
        {"title": "Note 4", "content": "Content 4", "tags": ["Backend", "API", "FastAPI"]},
    ]

    note_ids = []
    for note_data in notes_data:
        # Create note
        r = client.post("/notes/", json={"title": note_data["title"], "content": note_data["content"]})
        assert r.status_code == 201
        note_id = r.json()["id"]
        note_ids.append(note_id)

        # Attach tags
        tag_ids_to_attach = [tag_ids[tag] for tag in note_data["tags"]]
        r = client.post(f"/notes/{note_id}/tags", json={"tag_ids": tag_ids_to_attach})
        assert r.status_code == 200

    # Filter by "Backend" tag - should return notes 1, 2, 4
    r = client.get("/notes/", params={"tag_id": tag_ids["Backend"]})
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) == 3
    titles = {note["title"] for note in notes}
    assert titles == {"Note 1", "Note 2", "Note 4"}

    # Filter by "API" tag - should return notes 1, 3, 4
    r = client.get("/notes/", params={"tag_id": tag_ids["API"]})
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) == 3
    titles = {note["title"] for note in notes}
    assert titles == {"Note 1", "Note 3", "Note 4"}


def test_tag_organization_workflow(client):
    """Test realistic workflow: organizing project notes with tags."""
    # Scenario: A developer organizing their learning notes

    # Step 1: Create topic tags
    topics = ["Python", "JavaScript", "Databases", "Algorithms"]
    topic_tag_ids = {}
    for topic in topics:
        r = client.post("/tags/", json={"name": topic})
        topic_tag_ids[topic] = r.json()["id"]

    # Step 2: Create difficulty tags
    difficulties = ["Beginner", "Intermediate", "Advanced"]
    difficulty_tag_ids = {}
    for diff in difficulties:
        r = client.post("/tags/", json={"name": diff})
        difficulty_tag_ids[diff] = r.json()["id"]

    # Step 3: Create notes with combinations of tags
    learning_notes = [
        {
            "title": "Python Basics",
            "content": "Variables, loops, and functions",
            "tags": ["Python", "Beginner"]
        },
        {
            "title": "JavaScript Closures",
            "content": "Understanding closures and scope",
            "tags": ["JavaScript", "Intermediate"]
        },
        {
            "title": "SQL Indexing",
            "content": "Database indexing strategies",
            "tags": ["Databases", "Advanced"]
        },
        {
            "title": "Binary Search Trees",
            "content": "BST implementation and traversal",
            "tags": ["Algorithms", "Intermediate"]
        },
    ]

    created_note_ids = []
    for note_data in learning_notes:
        # Create note
        r = client.post("/notes/", json={
            "title": note_data["title"],
            "content": note_data["content"]
        })
        assert r.status_code == 201
        note_id = r.json()["id"]
        created_note_ids.append(note_id)

        # Attach topic and difficulty tags
        tags_to_attach = [
            topic_tag_ids[note_data["tags"][0]],
            difficulty_tag_ids[note_data["tags"][1]]
        ]
        r = client.post(f"/notes/{note_id}/tags", json={"tag_ids": tags_to_attach})
        assert r.status_code == 200
        assert len(r.json()["tags"]) == 2

    # Step 4: Find all Intermediate content
    r = client.get("/notes/", params={"tag_id": difficulty_tag_ids["Intermediate"]})
    assert r.status_code == 200
    intermediate_notes = r.json()
    assert len(intermediate_notes) == 2
    titles = {note["title"] for note in intermediate_notes}
    assert titles == {"JavaScript Closures", "Binary Search Trees"}

    # Step 5: Find all Python content
    r = client.get("/notes/", params={"tag_id": topic_tag_ids["Python"]})
    assert r.status_code == 200
    python_notes = r.json()
    assert len(python_notes) == 1
    assert python_notes[0]["title"] == "Python Basics"

    # Step 6: Search with tag filter
    r = client.get("/notes/search/", params={
        "q": "implementation",
        "tag_id": topic_tag_ids["Algorithms"]
    })
    assert r.status_code == 200
    search_results = r.json()
    assert search_results["total"] == 1
    assert search_results["items"][0]["title"] == "Binary Search Trees"


def test_tag_reorganization_workflow(client):
    """Test reorganizing tags by detaching and attaching."""
    # Initial setup
    r = client.post("/notes/", json={"title": "Note 1", "content": "Content 1"})
    note_id = r.json()["id"]

    old_tag_id = client.post("/tags/", json={"name": "OldCategory"}).json()["id"]
    new_tag_id = client.post("/tags/", json={"name": "NewCategory"}).json()["id"]

    # Attach old tag
    r = client.post(f"/notes/{note_id}/tags", json={"tag_ids": [old_tag_id]})
    assert r.status_code == 200
    assert len(r.json()["tags"]) == 1

    # Reorganize: remove old tag, add new tag
    r = client.delete(f"/notes/{note_id}/tags/{old_tag_id}")
    assert r.status_code == 200
    assert len(r.json()["tags"]) == 0

    r = client.post(f"/notes/{note_id}/tags", json={"tag_ids": [new_tag_id]})
    assert r.status_code == 200
    assert len(r.json()["tags"]) == 1
    assert r.json()["tags"][0]["name"] == "NewCategory"

    # Verify old tag still exists (not deleted)
    r = client.get("/tags/")
    tags = r.json()
    tag_names = {tag["name"] for tag in tags}
    assert "OldCategory" in tag_names
    assert "NewCategory" in tag_names


def test_bulk_tag_operations(client):
    """Test bulk operations with multiple tags and notes."""
    # Create a tag library
    tag_library = {
        "Language": ["Python", "JavaScript", "Go", "Rust"],
        "Level": ["Beginner", "Intermediate", "Advanced"],
        "Topic": ["Web", "Data Science", "DevOps", "Mobile"],
    }

    # Create all tags
    created_tags = {}
    for category, tags in tag_library.items():
        for tag in tags:
            r = client.post("/tags/", json={"name": tag})
            assert r.status_code == 201
            created_tags[tag] = r.json()["id"]

    # Create sample notes with various tag combinations
    sample_notes = [
        {"title": "Flask Tutorial", "tags": ["Python", "Beginner", "Web"]},
        {"title": "React Guide", "tags": ["JavaScript", "Intermediate", "Web"]},
        {"title": "Pandas Analysis", "tags": ["Python", "Intermediate", "Data Science"]},
        {"title": "Docker Basics", "tags": ["Go", "Beginner", "DevOps"]},
    ]

    for note in sample_notes:
        # Create note
        r = client.post("/notes/", json={
            "title": note["title"],
            "content": f"Content for {note['title']}"
        })
        assert r.status_code == 201
        note_id = r.json()["id"]

        # Attach all tags for this note
        tag_ids = [created_tags[tag] for tag in note["tags"]]
        r = client.post(f"/notes/{note_id}/tags", json={"tag_ids": tag_ids})
        assert r.status_code == 200
        assert len(r.json()["tags"]) == 3

    # Verify all tags were created
    r = client.get("/tags/")
    assert r.status_code == 200
    all_tags = r.json()
    assert len(all_tags) == len(created_tags)

    # Filter by multiple criteria (e.g., all Web-related content)
    r = client.get("/notes/", params={"tag_id": created_tags["Web"]})
    assert r.status_code == 200
    web_notes = r.json()
    assert len(web_notes) == 2
    titles = {note["title"] for note in web_notes}
    assert titles == {"Flask Tutorial", "React Guide"}


def test_tag_cleanup_after_note_deletion(client):
    """Test that tags remain after notes are deleted."""
    # Create tags
    tag_ids = []
    for i in range(5):
        r = client.post("/tags/", json={"name": f"Tag{i}"})
        tag_ids.append(r.json()["id"])

    # Create multiple notes with these tags
    note_ids = []
    for i in range(10):
        r = client.post("/notes/", json={
            "title": f"Note{i}",
            "content": f"Content {i}"
        })
        note_id = r.json()["id"]
        note_ids.append(note_id)

        # Attach random subset of tags
        tags_for_note = tag_ids[i % len(tag_ids):i % len(tag_ids) + 2]
        r = client.post(f"/notes/{note_id}/tags", json={"tag_ids": tags_for_note})
        assert r.status_code == 200

    # Delete all notes
    for note_id in note_ids:
        r = client.delete(f"/notes/{note_id}")
        assert r.status_code == 204

    # Verify all tags still exist
    r = client.get("/tags/")
    assert r.status_code == 200
    tags = r.json()
    assert len(tags) == 5

    # Verify tag names
    tag_names = {tag["name"] for tag in tags}
    expected_names = {f"Tag{i}" for i in range(5)}
    assert tag_names == expected_names
