def test_create_comment_on_note(client):
    # Create a note first
    note_payload = {"title": "Test Note", "content": "Content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Create comment on note
    comment_payload = {"content": "Great note!", "author_name": "Alice", "note_id": note_id}
    r = client.post("/comments/", json=comment_payload)
    assert r.status_code == 201
    comment = r.json()
    assert comment["content"] == "Great note!"
    assert comment["author_name"] == "Alice"
    assert comment["note_id"] == note_id
    assert comment["action_item_id"] is None


def test_create_comment_on_action_item(client):
    # Create an action item first
    action_payload = {"description": "Test action"}
    r = client.post("/action-items/", json=action_payload)
    assert r.status_code == 201
    action_id = r.json()["id"]

    # Create comment on action item
    comment_payload = {"content": "Will do!", "author_name": "Bob", "action_item_id": action_id}
    r = client.post("/comments/", json=comment_payload)
    assert r.status_code == 201
    comment = r.json()
    assert comment["content"] == "Will do!"
    assert comment["action_item_id"] == action_id
    assert comment["note_id"] is None


def test_create_comment_validation_both_ids(client):
    # Should not allow both note_id and action_item_id
    payload = {"content": "Test", "author_name": "Alice", "note_id": 1, "action_item_id": 1}
    r = client.post("/comments/", json=payload)
    assert r.status_code == 400


def test_create_comment_validation_no_ids(client):
    # Should require either note_id or action_item_id
    payload = {"content": "Test", "author_name": "Alice"}
    r = client.post("/comments/", json=payload)
    assert r.status_code == 400


def test_list_comments_filtered_by_note(client):
    # Create a note
    note_payload = {"title": "Test", "content": "Content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Create comments
    for i in range(3):
        comment_payload = {"content": f"Comment {i}", "author_name": "User", "note_id": note_id}
        client.post("/comments/", json=comment_payload)

    # Filter by note_id
    r = client.get(f"/comments/?note_id={note_id}")
    assert r.status_code == 200
    comments = r.json()
    assert len(comments) == 3


def test_get_and_delete_comment(client):
    # Create note and comment
    note_payload = {"title": "Test", "content": "Content"}
    r = client.post("/notes/", json=note_payload)
    note_id = r.json()["id"]

    comment_payload = {"content": "Test", "author_name": "Alice", "note_id": note_id}
    r = client.post("/comments/", json=comment_payload)
    comment_id = r.json()["id"]

    # Get comment
    r = client.get(f"/comments/{comment_id}")
    assert r.status_code == 200

    # Delete comment
    r = client.delete(f"/comments/{comment_id}")
    assert r.status_code == 204

    # Verify deletion
    r = client.get(f"/comments/{comment_id}")
    assert r.status_code == 404


def test_comments_pagination_skip(client):
    # Create a note
    note_payload = {"title": "Test", "content": "Content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Create 5 comments
    comment_ids = []
    for i in range(5):
        comment_payload = {"content": f"Comment {i}", "author_name": "User", "note_id": note_id}
        r = client.post("/comments/", json=comment_payload)
        assert r.status_code == 201
        comment_ids.append(r.json()["id"])

    # Get all comments for this note
    r = client.get(f"/comments/?note_id={note_id}")
    assert r.status_code == 200
    all_comments = r.json()
    assert len(all_comments) == 5

    # Skip first 2 comments
    r = client.get(f"/comments/?note_id={note_id}&skip=2")
    assert r.status_code == 200
    skipped_comments = r.json()
    assert len(skipped_comments) == 3
    # Should skip first 2 comments (default sort is created_at ASC)
    assert skipped_comments[0]["id"] == all_comments[2]["id"]


def test_comments_pagination_limit(client):
    # Create a note
    note_payload = {"title": "Test", "content": "Content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Create 5 comments
    for i in range(5):
        comment_payload = {"content": f"Comment {i}", "author_name": "User", "note_id": note_id}
        r = client.post("/comments/", json=comment_payload)
        assert r.status_code == 201

    # Get with limit
    r = client.get(f"/comments/?note_id={note_id}&limit=3")
    assert r.status_code == 200
    comments = r.json()
    assert len(comments) == 3


def test_comments_pagination_limit_max_validation(client):
    # Create a note
    note_payload = {"title": "Test", "content": "Content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Create 5 comments
    for i in range(5):
        comment_payload = {"content": f"Comment {i}", "author_name": "User", "note_id": note_id}
        r = client.post("/comments/", json=comment_payload)
        assert r.status_code == 201

    # Request limit of 300 (should be rejected as > 200)
    r = client.get(f"/comments/?note_id={note_id}&limit=300")
    assert r.status_code == 422  # Validation error

    # Request limit of exactly 200 (should work)
    r = client.get(f"/comments/?note_id={note_id}&limit=200")
    assert r.status_code == 200
    comments = r.json()
    assert len(comments) == 5


def test_comments_pagination_default(client):
    # Create a note
    note_payload = {"title": "Test", "content": "Content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Create 60 comments (default limit is 50)
    for i in range(60):
        comment_payload = {"content": f"Comment {i}", "author_name": "User", "note_id": note_id}
        r = client.post("/comments/", json=comment_payload)
        assert r.status_code == 201

    # Get with default limit
    r = client.get(f"/comments/?note_id={note_id}")
    assert r.status_code == 200
    comments = r.json()
    assert len(comments) == 50  # Default limit


def test_comments_pagination_skip_exceeds_total(client):
    # Create a note
    note_payload = {"title": "Test", "content": "Content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Create 3 comments
    for i in range(3):
        comment_payload = {"content": f"Comment {i}", "author_name": "User", "note_id": note_id}
        r = client.post("/comments/", json=comment_payload)
        assert r.status_code == 201

    # Skip more than total
    r = client.get(f"/comments/?note_id={note_id}&skip=10")
    assert r.status_code == 200
    comments = r.json()
    assert len(comments) == 0  # Empty result


def test_comments_pagination_combined_skip_limit(client):
    # Create a note
    note_payload = {"title": "Test", "content": "Content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Create 10 comments
    for i in range(10):
        comment_payload = {"content": f"Comment {i}", "author_name": "User", "note_id": note_id}
        r = client.post("/comments/", json=comment_payload)
        assert r.status_code == 201

    # Skip 3, limit 5
    r = client.get(f"/comments/?note_id={note_id}&skip=3&limit=5")
    assert r.status_code == 200
    comments = r.json()
    assert len(comments) == 5


def test_comments_filter_by_action_item_id_with_pagination(client):
    # Create an action item
    action_payload = {"description": "Test action"}
    r = client.post("/action-items/", json=action_payload)
    assert r.status_code == 201
    action_id = r.json()["id"]

    # Create 10 comments on this action item
    for i in range(10):
        comment_payload = {
            "content": f"Comment {i}",
            "author_name": "User",
            "action_item_id": action_id,
        }
        r = client.post("/comments/", json=comment_payload)
        assert r.status_code == 201

    # Filter by action_item_id with pagination
    r = client.get(f"/comments/?action_item_id={action_id}&skip=0&limit=5")
    assert r.status_code == 200
    comments = r.json()
    assert len(comments) == 5
    # All should belong to this action item
    assert all(c["action_item_id"] == action_id for c in comments)


def test_comments_no_filter_returns_all(client):
    # Create a note and an action item
    note_payload = {"title": "Test", "content": "Content"}
    r = client.post("/notes/", json=note_payload)
    note_id = r.json()["id"]

    action_payload = {"description": "Test action"}
    r = client.post("/action-items/", json=action_payload)
    action_id = r.json()["id"]

    # Create comments on note
    for i in range(3):
        comment_payload = {
            "content": f"Note comment {i}",
            "author_name": "User",
            "note_id": note_id,
        }
        r = client.post("/comments/", json=comment_payload)
        assert r.status_code == 201

    # Create comments on action item
    for i in range(2):
        comment_payload = {
            "content": f"Action comment {i}",
            "author_name": "User",
            "action_item_id": action_id,
        }
        r = client.post("/comments/", json=comment_payload)
        assert r.status_code == 201

    # Get all comments without filter
    r = client.get("/comments/")
    assert r.status_code == 200
    comments = r.json()
    assert len(comments) == 5
