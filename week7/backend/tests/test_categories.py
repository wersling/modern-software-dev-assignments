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
