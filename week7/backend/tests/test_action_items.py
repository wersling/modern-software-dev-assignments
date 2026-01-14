def test_create_complete_list_and_patch_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False
    assert "created_at" in item and "updated_at" in item

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/", params={"completed": True, "limit": 5, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.patch(f"/action-items/{item['id']}", json={"description": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["description"] == "Updated"


def test_get_action_item_by_id(client):
    payload = {"description": "Get Test Item"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201
    item_id = r.json()["id"]

    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 200
    item = r.json()
    assert item["id"] == item_id
    assert item["description"] == "Get Test Item"

    r = client.get("/action-items/99999")
    assert r.status_code == 404


def test_delete_action_item(client):
    payload = {"description": "Delete Me"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201
    item_id = r.json()["id"]

    r = client.delete(f"/action-items/{item_id}")
    assert r.status_code == 204

    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 404

    r = client.delete("/action-items/99999")
    assert r.status_code == 404


def test_action_item_validation_description_too_long(client):
    payload = {"description": "x" * 501}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 422


def test_action_item_validation_empty_description(client):
    payload = {"description": ""}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 422


def test_action_item_validation_strip_whitespace(client):
    payload = {"description": "  Action with spaces  "}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["description"] == "Action with spaces"


def test_action_items_pagination_skip(client):
    # Create 5 action items
    item_ids = []
    for i in range(5):
        payload = {"description": f"Action {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201
        item_ids.append(r.json()["id"])

    # Get all items
    r = client.get("/action-items/")
    assert r.status_code == 200
    all_items = r.json()
    assert len(all_items) == 5

    # Skip first 2 items
    r = client.get("/action-items/", params={"skip": 2})
    assert r.status_code == 200
    skipped_items = r.json()
    assert len(skipped_items) == 3
    # Should skip first 2 items (default sort is -created_at)
    assert skipped_items[0]["id"] == all_items[2]["id"]


def test_action_items_pagination_limit(client):
    # Create 5 action items
    for i in range(5):
        payload = {"description": f"Action {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201

    # Get with limit
    r = client.get("/action-items/", params={"limit": 3})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3


def test_action_items_pagination_limit_max_validation(client):
    # Create 5 action items
    for i in range(5):
        payload = {"description": f"Action {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201

    # Request limit of 300 (should be rejected as > 200)
    r = client.get("/action-items/", params={"limit": 300})
    assert r.status_code == 422  # Validation error

    # Request limit of exactly 200 (should work)
    r = client.get("/action-items/", params={"limit": 200})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 5


def test_action_items_pagination_default(client):
    # Create 60 action items (default limit is 50)
    for i in range(60):
        payload = {"description": f"Action {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201

    # Get with default limit
    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 50  # Default limit


def test_action_items_pagination_skip_exceeds_total(client):
    # Create 3 action items
    for i in range(3):
        payload = {"description": f"Action {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201

    # Skip more than total
    r = client.get("/action-items/", params={"skip": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 0  # Empty result


def test_action_items_pagination_combined_skip_limit(client):
    # Create 10 action items
    for i in range(10):
        payload = {"description": f"Action {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201

    # Skip 3, limit 5
    r = client.get("/action-items/", params={"skip": 3, "limit": 5})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 5


def test_action_items_filter_completed_true(client):
    # Create completed and incomplete items
    completed_ids = []

    for i in range(3):
        payload = {"description": f"Action {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201
        item_id = r.json()["id"]

        # Mark first 2 as completed
        if i < 2:
            r = client.put(f"/action-items/{item_id}/complete")
            assert r.status_code == 200
            completed_ids.append(item_id)

    # Filter completed=true
    r = client.get("/action-items/", params={"completed": True})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2
    assert all(item["completed"] is True for item in items)


def test_action_items_filter_completed_false(client):
    # Create completed and incomplete items
    for i in range(3):
        payload = {"description": f"Action {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201
        item_id = r.json()["id"]

        # Mark first 2 as completed
        if i < 2:
            r = client.put(f"/action-items/{item_id}/complete")
            assert r.status_code == 200

    # Filter completed=false
    r = client.get("/action-items/", params={"completed": False})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["completed"] is False


def test_action_items_filter_with_pagination(client):
    # Create completed and incomplete items
    for i in range(10):
        payload = {"description": f"Action {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201
        item_id = r.json()["id"]

        # Mark even items as completed
        if i % 2 == 0:
            r = client.put(f"/action-items/{item_id}/complete")
            assert r.status_code == 200

    # Filter completed=true with pagination
    r = client.get("/action-items/", params={"completed": True, "skip": 0, "limit": 3})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3
    assert all(item["completed"] is True for item in items)


def test_action_items_sort_ascending_created_at(client):
    # Create 3 action items
    item_ids = []
    for i in range(3):
        payload = {"description": f"Action {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201
        item_ids.append(r.json()["id"])

    # Sort by created_at ascending (oldest first)
    r = client.get("/action-items/", params={"sort": "created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 3
    # First item should be oldest (created first)
    assert items[0]["id"] == item_ids[0]


def test_action_items_sort_descending_created_at(client):
    # Create 3 action items
    item_ids = []
    for i in range(3):
        payload = {"description": f"Action {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201
        item_ids.append(r.json()["id"])

    # Sort by created_at descending (newest first) - this is default
    r = client.get("/action-items/", params={"sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 3
    # First item should be newest (created last)
    assert items[0]["id"] == item_ids[2]


def test_action_items_sort_by_description(client):
    # Create action items with different descriptions
    descriptions = ["Zebra task", "Apple task", "Mango task"]
    for desc in descriptions:
        payload = {"description": desc}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201

    # Sort by description ascending
    r = client.get("/action-items/", params={"sort": "description"})
    assert r.status_code == 200
    items = r.json()
    item_descriptions = [i["description"] for i in items if i["description"] in descriptions]
    assert item_descriptions[0] == "Apple task"
    assert item_descriptions[1] == "Mango task"
    assert item_descriptions[2] == "Zebra task"

    # Sort by description descending
    r = client.get("/action-items/", params={"sort": "-description"})
    assert r.status_code == 200
    items = r.json()
    item_descriptions = [i["description"] for i in items if i["description"] in descriptions]
    assert item_descriptions[0] == "Zebra task"
    assert item_descriptions[1] == "Mango task"
    assert item_descriptions[2] == "Apple task"


def test_action_items_sort_by_updated_at(client):
    # Create an action item
    payload = {"description": "Original"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201
    item_id = r.json()["id"]

    # Create another action item
    payload = {"description": "Another"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201

    # Update first item (changes updated_at)
    r = client.patch(f"/action-items/{item_id}", json={"description": "Updated"})
    assert r.status_code == 200

    # Sort by updated_at descending - updated item should be first
    r = client.get("/action-items/", params={"sort": "-updated_at"})
    assert r.status_code == 200
    items = r.json()
    assert items[0]["id"] == item_id
    assert items[0]["description"] == "Updated"


def test_action_items_sort_by_id(client):
    # Create 3 action items
    for i in range(3):
        payload = {"description": f"Action {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201

    # Sort by id ascending
    r = client.get("/action-items/", params={"sort": "id"})
    assert r.status_code == 200
    items = r.json()
    ids = [i["id"] for i in items]
    assert ids == sorted(ids)


def test_action_items_sort_invalid_field(client):
    # Create an action item
    payload = {"description": "Test"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201

    # Try invalid sort field - should default to -created_at
    r = client.get("/action-items/", params={"sort": "invalid_field"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_action_items_filter_with_sorting(client):
    # Create action items
    for i in range(5):
        payload = {"description": f"Task {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201
        item_id = r.json()["id"]

        # Mark odd items as completed
        if i % 2 == 1:
            r = client.put(f"/action-items/{item_id}/complete")
            assert r.status_code == 200

    # Filter completed=true with sort by description
    r = client.get("/action-items/", params={"completed": True, "sort": "description"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2
    # Should be sorted alphabetically
    descriptions = [i["description"] for i in items]
    assert descriptions == sorted(descriptions)
