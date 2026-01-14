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
