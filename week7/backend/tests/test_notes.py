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


def test_notes_pagination_skip(client):
    # Create 5 notes
    note_ids = []
    for i in range(5):
        payload = {"title": f"Note {i}", "content": f"Content {i}"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201
        note_ids.append(r.json()["id"])

    # Get all notes
    r = client.get("/notes/")
    assert r.status_code == 200
    all_notes = r.json()
    assert len(all_notes) == 5

    # Skip first 2 notes
    r = client.get("/notes/", params={"skip": 2})
    assert r.status_code == 200
    skipped_notes = r.json()
    assert len(skipped_notes) == 3
    # Should skip first 2 notes (default sort is -created_at)
    assert skipped_notes[0]["id"] == all_notes[2]["id"]


def test_notes_pagination_limit(client):
    # Create 5 notes
    for i in range(5):
        payload = {"title": f"Note {i}", "content": f"Content {i}"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201

    # Get with limit
    r = client.get("/notes/", params={"limit": 3})
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) == 3


def test_notes_pagination_limit_max_validation(client):
    # Create 5 notes
    for i in range(5):
        payload = {"title": f"Note {i}", "content": f"Content {i}"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201

    # Request limit of 300 (should be rejected as > 200)
    r = client.get("/notes/", params={"limit": 300})
    assert r.status_code == 422  # Validation error

    # Request limit of exactly 200 (should work)
    r = client.get("/notes/", params={"limit": 200})
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) == 5


def test_notes_pagination_default(client):
    # Create 60 notes (default limit is 50)
    for i in range(60):
        payload = {"title": f"Note {i}", "content": f"Content {i}"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201

    # Get with default limit
    r = client.get("/notes/")
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) == 50  # Default limit


def test_notes_pagination_skip_exceeds_total(client):
    # Create 3 notes
    for i in range(3):
        payload = {"title": f"Note {i}", "content": f"Content {i}"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201

    # Skip more than total
    r = client.get("/notes/", params={"skip": 10})
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) == 0  # Empty result


def test_notes_pagination_combined_skip_limit(client):
    # Create 10 notes
    for i in range(10):
        payload = {"title": f"Note {i}", "content": f"Content {i}"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201

    # Skip 3, limit 5
    r = client.get("/notes/", params={"skip": 3, "limit": 5})
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) == 5


def test_notes_sort_ascending_created_at(client):
    # Create 3 notes with slight delay to ensure different timestamps
    note_ids = []
    for i in range(3):
        payload = {"title": f"Note {i}", "content": f"Content {i}"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201
        note_ids.append(r.json()["id"])

    # Sort by created_at ascending (oldest first)
    r = client.get("/notes/", params={"sort": "created_at"})
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) >= 3
    # First note should be oldest (created first)
    assert notes[0]["id"] == note_ids[0]


def test_notes_sort_descending_created_at(client):
    # Create 3 notes
    note_ids = []
    for i in range(3):
        payload = {"title": f"Note {i}", "content": f"Content {i}"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201
        note_ids.append(r.json()["id"])

    # Sort by created_at descending (newest first) - this is default
    r = client.get("/notes/", params={"sort": "-created_at"})
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) >= 3
    # First note should be newest (created last)
    assert notes[0]["id"] == note_ids[2]


def test_notes_sort_by_title(client):
    # Create notes with different titles
    titles = ["Zebra", "Apple", "Mango"]
    for title in titles:
        payload = {"title": title, "content": "Content"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201

    # Sort by title ascending
    r = client.get("/notes/", params={"sort": "title"})
    assert r.status_code == 200
    notes = r.json()
    note_titles = [n["title"] for n in notes if n["title"] in titles]
    assert note_titles[0] == "Apple"
    assert note_titles[1] == "Mango"
    assert note_titles[2] == "Zebra"

    # Sort by title descending
    r = client.get("/notes/", params={"sort": "-title"})
    assert r.status_code == 200
    notes = r.json()
    note_titles = [n["title"] for n in notes if n["title"] in titles]
    assert note_titles[0] == "Zebra"
    assert note_titles[1] == "Mango"
    assert note_titles[2] == "Apple"


def test_notes_sort_by_updated_at(client):
    # Create a note
    payload = {"title": "Original", "content": "Content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Create another note
    payload = {"title": "Another", "content": "Content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201

    # Update first note (changes updated_at)
    r = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200

    # Sort by updated_at descending - updated note should be first
    r = client.get("/notes/", params={"sort": "-updated_at"})
    assert r.status_code == 200
    notes = r.json()
    assert notes[0]["id"] == note_id
    assert notes[0]["title"] == "Updated"


def test_notes_sort_by_id(client):
    # Create 3 notes
    for i in range(3):
        payload = {"title": f"Note {i}", "content": "Content"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201

    # Sort by id ascending
    r = client.get("/notes/", params={"sort": "id"})
    assert r.status_code == 200
    notes = r.json()
    ids = [n["id"] for n in notes]
    assert ids == sorted(ids)


def test_notes_sort_invalid_field(client):
    # Create a note
    payload = {"title": "Test", "content": "Content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201

    # Try invalid sort field - should default to -created_at
    r = client.get("/notes/", params={"sort": "invalid_field"})
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) >= 1


def test_notes_search_with_pagination(client):
    # Create notes with matching and non-matching content
    for i in range(10):
        payload = {"title": f"Note {i}", "content": "searchable" if i % 2 == 0 else "other"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201

    # Search with pagination
    r = client.get("/notes/", params={"q": "searchable", "skip": 0, "limit": 3})
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) == 3
    # All should contain "searchable"
    assert all("searchable" in n["content"] or "searchable" in n["title"] for n in notes)


def test_notes_search_with_sorting(client):
    # Create notes
    for i in range(5):
        payload = {"title": f"Searchable {i}", "content": "Content"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201

    # Search with sort
    r = client.get("/notes/", params={"q": "Searchable", "sort": "title"})
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) == 5
    # Should be sorted alphabetically
    titles = [n["title"] for n in notes]
    assert titles == sorted(titles)
