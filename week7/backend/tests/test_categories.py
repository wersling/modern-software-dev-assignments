def test_create_and_list_categories(client):
    # Create a category
    payload = {"name": "Work", "description": "Work-related items"}
    r = client.post("/categories/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "Work"
    assert data["description"] == "Work-related items"

    # List categories
    r = client.get("/categories/")
    assert r.status_code == 200
    categories = r.json()
    assert len(categories) >= 1
    assert any(c["name"] == "Work" for c in categories)


def test_create_category_duplicate_name(client):
    payload = {"name": "Duplicate", "description": "Test"}
    r = client.post("/categories/", json=payload)
    assert r.status_code == 201

    # Try to create duplicate
    r = client.post("/categories/", json=payload)
    assert r.status_code == 400
    assert "already exists" in r.json()["detail"]


def test_get_category_by_id(client):
    # Create a category
    payload = {"name": "Personal"}
    r = client.post("/categories/", json=payload)
    assert r.status_code == 201
    category_id = r.json()["id"]

    # Get by id
    r = client.get(f"/categories/{category_id}")
    assert r.status_code == 200
    category = r.json()
    assert category["name"] == "Personal"

    # Get non-existent
    r = client.get("/categories/99999")
    assert r.status_code == 404


def test_patch_category(client):
    # Create a category
    payload = {"name": "Old Name", "description": "Old desc"}
    r = client.post("/categories/", json=payload)
    assert r.status_code == 201
    category_id = r.json()["id"]

    # Patch it
    r = client.patch(f"/categories/{category_id}", json={"name": "New Name"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["name"] == "New Name"
    assert patched["description"] == "Old desc"


def test_delete_category(client):
    # Create a category
    payload = {"name": "ToDelete"}
    r = client.post("/categories/", json=payload)
    assert r.status_code == 201
    category_id = r.json()["id"]

    # Delete it
    r = client.delete(f"/categories/{category_id}")
    assert r.status_code == 204

    # Verify deletion
    r = client.get(f"/categories/{category_id}")
    assert r.status_code == 404


def test_categories_pagination_skip(client):
    # Create 5 categories
    category_ids = []
    for i in range(5):
        payload = {"name": f"Category {i}"}
        r = client.post("/categories/", json=payload)
        assert r.status_code == 201
        category_ids.append(r.json()["id"])

    # Get all categories
    r = client.get("/categories/")
    assert r.status_code == 200
    all_categories = r.json()
    assert len(all_categories) == 5

    # Skip first 2 categories
    r = client.get("/categories/", params={"skip": 2})
    assert r.status_code == 200
    skipped_categories = r.json()
    assert len(skipped_categories) == 3
    # Should skip first 2 categories (default sort is -created_at)
    assert skipped_categories[0]["id"] == all_categories[2]["id"]


def test_categories_pagination_limit(client):
    # Create 5 categories
    for i in range(5):
        payload = {"name": f"Category {i}"}
        r = client.post("/categories/", json=payload)
        assert r.status_code == 201

    # Get with limit
    r = client.get("/categories/", params={"limit": 3})
    assert r.status_code == 200
    categories = r.json()
    assert len(categories) == 3


def test_categories_pagination_limit_max_validation(client):
    # Create 5 categories
    for i in range(5):
        payload = {"name": f"Category {i}"}
        r = client.post("/categories/", json=payload)
        assert r.status_code == 201

    # Request limit of 300 (should be rejected as > 200)
    r = client.get("/categories/", params={"limit": 300})
    assert r.status_code == 422  # Validation error

    # Request limit of exactly 200 (should work)
    r = client.get("/categories/", params={"limit": 200})
    assert r.status_code == 200
    categories = r.json()
    assert len(categories) == 5


def test_categories_pagination_default(client):
    # Create 60 categories (default limit is 50)
    for i in range(60):
        payload = {"name": f"Category {i}"}
        r = client.post("/categories/", json=payload)
        assert r.status_code == 201

    # Get with default limit
    r = client.get("/categories/")
    assert r.status_code == 200
    categories = r.json()
    assert len(categories) == 50  # Default limit


def test_categories_pagination_skip_exceeds_total(client):
    # Create 3 categories
    for i in range(3):
        payload = {"name": f"Category {i}"}
        r = client.post("/categories/", json=payload)
        assert r.status_code == 201

    # Skip more than total
    r = client.get("/categories/", params={"skip": 10})
    assert r.status_code == 200
    categories = r.json()
    assert len(categories) == 0  # Empty result


def test_categories_pagination_combined_skip_limit(client):
    # Create 10 categories
    for i in range(10):
        payload = {"name": f"Category {i}"}
        r = client.post("/categories/", json=payload)
        assert r.status_code == 201

    # Skip 3, limit 5
    r = client.get("/categories/", params={"skip": 3, "limit": 5})
    assert r.status_code == 200
    categories = r.json()
    assert len(categories) == 5
