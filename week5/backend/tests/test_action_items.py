def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["ok"] is True
    assert item["data"]["completed"] is False
    item_id = item["data"]["id"]

    r = client.put(f"/action-items/{item_id}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["ok"] is True
    assert done["data"]["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    response = r.json()
    # List endpoint returns PaginatedResponse directly
    items = response["items"]
    assert len(items) == 1


def test_list_action_items_filter_by_completed(client):
    """Test filtering action items by completion status."""
    # Create three items
    items_data = [
        {"description": "Task 1"},
        {"description": "Task 2"},
        {"description": "Task 3"},
    ]

    created_ids = []
    for payload in items_data:
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201, r.text
        created_ids.append(r.json()["data"]["id"])

    # Complete one item
    r = client.put(f"/action-items/{created_ids[0]}/complete")
    assert r.status_code == 200

    # Test filter: completed=true
    r = client.get("/action-items/?completed=true")
    assert r.status_code == 200
    response = r.json()
    completed_items = response["items"]
    assert len(completed_items) == 1
    assert completed_items[0]["completed"] is True
    assert completed_items[0]["id"] == created_ids[0]

    # Test filter: completed=false
    r = client.get("/action-items/?completed=false")
    assert r.status_code == 200
    response = r.json()
    incomplete_items = response["items"]
    assert len(incomplete_items) == 2
    assert all(item["completed"] is False for item in incomplete_items)

    # Test no filter (should return all)
    r = client.get("/action-items/")
    assert r.status_code == 200
    response = r.json()
    all_items = response["items"]
    assert len(all_items) == 3


def test_bulk_complete_action_items(client):
    """Test bulk completing multiple action items."""
    # Create four items
    items_data = [
        {"description": "Task 1"},
        {"description": "Task 2"},
        {"description": "Task 3"},
        {"description": "Task 4"},
    ]

    created_ids = []
    for payload in items_data:
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201, r.text
        created_ids.append(r.json()["data"]["id"])

    # Bulk complete first three items
    bulk_payload = {"ids": created_ids[:3]}
    r = client.post("/action-items/bulk-complete", json=bulk_payload)
    assert r.status_code == 200
    response = r.json()
    assert response["ok"] is True
    data = response["data"]

    # Verify response structure
    assert "updated" in data
    assert "total_updated" in data
    assert "not_found" in data
    assert data["total_updated"] == 3
    assert len(data["updated"]) == 3
    assert all(item["completed"] is True for item in data["updated"])
    assert data["not_found"] == []

    # Verify fourth item is still incomplete
    r = client.get("/action-items/")
    assert r.status_code == 200
    response = r.json()
    all_items = response["items"]
    completed_items = [item for item in all_items if item["completed"] is True]
    incomplete_items = [item for item in all_items if item["completed"] is False]

    assert len(completed_items) == 3
    assert len(incomplete_items) == 1
    assert incomplete_items[0]["id"] == created_ids[3]


def test_bulk_complete_with_some_invalid_ids(client):
    """Test bulk complete with some IDs that don't exist."""
    # Create two items
    item1 = client.post("/action-items/", json={"description": "Task 1"}).json()
    item2 = client.post("/action-items/", json={"description": "Task 2"}).json()

    # Try to complete with some non-existent IDs
    bulk_payload = {"ids": [item1["data"]["id"], 99999, 88888, item2["data"]["id"]]}
    r = client.post("/action-items/bulk-complete", json=bulk_payload)
    assert r.status_code == 200
    response = r.json()

    # Should update only the two existing items
    assert response["ok"] is True
    data = response["data"]
    assert data["total_updated"] == 2
    assert len(data["updated"]) == 2
    assert data["not_found"] == [99999, 88888]

    # Verify the items were actually completed
    r = client.get("/action-items/")
    response = r.json()
    all_items = response["items"]
    assert all(item["completed"] is True for item in all_items)


def test_bulk_complete_validation(client):
    """Test bulk complete request validation."""
    # Test empty list
    r = client.post("/action-items/bulk-complete", json={"ids": []})
    assert r.status_code == 422  # Validation error

    # Test invalid IDs (zero or negative)
    r = client.post("/action-items/bulk-complete", json={"ids": [1, -1, 0]})
    assert r.status_code == 422  # Validation error


def test_bulk_complete_exceeds_limit(client):
    """Test bulk complete with more than MAX_BULK_ITEMS."""
    # Create a payload with 1001 IDs (exceeds MAX_BULK_ITEMS=1000)
    bulk_payload = {"ids": list(range(1, 1002))}
    r = client.post("/action-items/bulk-complete", json=bulk_payload)
    assert r.status_code == 400
    assert "Cannot bulk complete more than 1000 items" in r.json()["error"]["message"]


def test_create_action_item_validation(client):
    """Test action item creation validation."""
    # Test empty description
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422  # Validation error

    # Test whitespace-only description
    r = client.post("/action-items/", json={"description": "   "})
    assert r.status_code == 422  # Validation error

    # Test description exceeding max length
    r = client.post("/action-items/", json={"description": "a" * 1001})
    assert r.status_code == 422  # Validation error

    # Test valid description with leading/trailing whitespace
    r = client.post("/action-items/", json={"description": "  Valid task  "})
    assert r.status_code == 201
    item = r.json()
    assert item["data"]["description"] == "Valid task"  # Whitespace stripped


def test_create_action_item_max_length(client):
    """Test action item with exactly 1000 characters."""
    description = "a" * 1000
    r = client.post("/action-items/", json={"description": description})
    assert r.status_code == 201
    item = r.json()
    assert item["data"]["description"] == description
