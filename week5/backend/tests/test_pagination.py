"""Comprehensive pagination tests for Notes and ActionItems endpoints.

This test module covers:
- Default pagination parameters
- Custom pagination parameters
- Edge cases (empty last page, page size limits)
- Integration with filters (tag_id, completed)
- Response structure validation
- total_pages calculation

Note: All tests use the client fixture to create data via API calls to ensure
data is visible to the API endpoints being tested.
"""

from fastapi.testclient import TestClient


class TestNotesPagination:
    """Test suite for Notes list endpoint pagination."""

    def test_notes_pagination_default(self, client: TestClient):
        """Test default pagination parameters."""
        # Create test data via API
        for i in range(25):
            payload = {"title": f"Note {i}", "content": f"Content {i}"}
            r = client.post("/notes/", json=payload)
            assert r.status_code == 201

        r = client.get("/notes/")
        assert r.status_code == 200
        data = r.json()

        # Verify default pagination
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total"] == 25
        assert data["total_pages"] == 2
        assert len(data["items"]) == 20
        assert "items" in data
        assert "total" in data
        assert "total_pages" in data

    def test_notes_pagination_custom_params(self, client: TestClient):
        """Test custom pagination parameters."""
        # Create test data via API
        for i in range(50):
            payload = {"title": f"Note {i}", "content": f"Content {i}"}
            r = client.post("/notes/", json=payload)
            assert r.status_code == 201

        r = client.get("/notes/?page=2&page_size=10")
        assert r.status_code == 200
        data = r.json()

        assert data["page"] == 2
        assert data["page_size"] == 10
        assert data["total"] == 50
        assert data["total_pages"] == 5
        assert len(data["items"]) == 10

    def test_notes_empty_last_page(self, client: TestClient):
        """Test empty last page when page exceeds available data."""
        # Create test data via API
        for i in range(15):
            payload = {"title": f"Note {i}", "content": f"Content {i}"}
            r = client.post("/notes/", json=payload)
            assert r.status_code == 201

        r = client.get("/notes/?page=999&page_size=10")
        assert r.status_code == 200
        data = r.json()

        # Should return empty items for out-of-range page
        assert data["page"] == 999
        assert data["page_size"] == 10
        assert data["total"] == 15
        assert data["total_pages"] == 2
        assert len(data["items"]) == 0

    def test_notes_exact_last_page(self, client: TestClient):
        """Test accessing the exact last page."""
        # Create test data via API
        for i in range(45):
            payload = {"title": f"Note {i}", "content": f"Content {i}"}
            r = client.post("/notes/", json=payload)
            assert r.status_code == 201

        r = client.get("/notes/?page=3&page_size=15")
        assert r.status_code == 200
        data = r.json()

        assert data["page"] == 3
        assert data["page_size"] == 15
        assert data["total"] == 45
        assert data["total_pages"] == 3
        assert len(data["items"]) == 15

    def test_notes_page_size_exceeds_maximum(self, client: TestClient):
        """Test that page_size > 100 returns validation error."""
        # Create a test note
        payload = {"title": "Test Note", "content": "Test content"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201

        r = client.get("/notes/?page_size=101")
        assert r.status_code == 422

    def test_notes_page_size_zero(self, client: TestClient):
        """Test that page_size = 0 returns validation error."""
        r = client.get("/notes/?page_size=0")
        assert r.status_code == 422

    def test_notes_page_less_than_one(self, client: TestClient):
        """Test that page < 1 returns validation error."""
        r = client.get("/notes/?page=0")
        assert r.status_code == 422

        r = client.get("/notes/?page=-1")
        assert r.status_code == 422

    def test_notes_with_tag_filter_pagination(self, client: TestClient):
        """Test pagination combined with tag_id filter."""
        # Create tags
        tag1_response = client.post("/tags/", json={"name": "python"})
        assert tag1_response.status_code == 201
        tag1_id = tag1_response.json()["id"]

        tag2_response = client.post("/tags/", json={"name": "javascript"})
        assert tag2_response.status_code == 201
        tag2_id = tag2_response.json()["id"]

        # Create notes with different tags
        for i in range(30):
            payload = {"title": f"Note {i}", "content": f"Content {i}"}
            r = client.post("/notes/", json=payload)
            assert r.status_code == 201
            note_id = r.json()["id"]

            # Add tag1 to first 15 notes, tag2 to next 15 notes
            tag_id = tag1_id if i < 15 else tag2_id
            r = client.post(f"/notes/{note_id}/tags", json={"tag_ids": [tag_id]})
            assert r.status_code == 200

        # Test pagination with tag_id filter
        r = client.get(f"/notes/?tag_id={tag1_id}&page=1&page_size=10")
        assert r.status_code == 200
        data = r.json()

        assert data["total"] == 15
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 2
        assert len(data["items"]) == 10

        # Verify all returned notes have the correct tag
        for item in data["items"]:
            assert any(tag["id"] == tag1_id for tag in item["tags"])

    def test_notes_with_tag_name_filter_pagination(self, client: TestClient):
        """Test pagination combined with tag name filter."""
        # Create tag
        tag_response = client.post("/tags/", json={"name": "urgent"})
        assert tag_response.status_code == 201
        tag_id = tag_response.json()["id"]

        # Create notes with the tag
        for i in range(25):
            payload = {"title": f"Urgent Note {i}", "content": f"Content {i}"}
            r = client.post("/notes/", json=payload)
            assert r.status_code == 201
            note_id = r.json()["id"]

            r = client.post(f"/notes/{note_id}/tags", json={"tag_ids": [tag_id]})
            assert r.status_code == 200

        # Create some notes without the tag
        for i in range(10):
            payload = {"title": f"Normal Note {i}", "content": f"Content {i}"}
            r = client.post("/notes/", json=payload)
            assert r.status_code == 201

        # Test pagination with tag name filter
        r = client.get("/notes/?tag=urgent&page=2&page_size=10")
        assert r.status_code == 200
        data = r.json()

        assert data["total"] == 25
        assert data["page"] == 2
        assert data["page_size"] == 10
        assert data["total_pages"] == 3
        assert len(data["items"]) == 10

    def test_notes_empty_database(self, client: TestClient):
        """Test pagination with empty database."""
        r = client.get("/notes/")
        assert r.status_code == 200
        data = r.json()

        assert data["total"] == 0
        assert data["total_pages"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert len(data["items"]) == 0

    def test_notes_single_item(self, client: TestClient):
        """Test pagination with a single item."""
        payload = {"title": "Only Note", "content": "Only content"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201

        r = client.get("/notes/")
        assert r.status_code == 200
        data = r.json()

        assert data["total"] == 1
        assert data["total_pages"] == 1
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert len(data["items"]) == 1

    def test_notes_response_structure(self, client: TestClient):
        """Test that response has all required fields with correct types."""
        payload = {"title": "Test", "content": "Content"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201

        r = client.get("/notes/")
        assert r.status_code == 200
        data = r.json()

        # Verify all fields exist
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

        # Verify field types
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["page_size"], int)
        assert isinstance(data["total_pages"], int)

        # Verify item structure
        if len(data["items"]) > 0:
            item = data["items"][0]
            assert "id" in item
            assert "title" in item
            assert "content" in item
            assert "created_at" in item
            assert "tags" in item


class TestActionItemsPagination:
    """Test suite for ActionItems list endpoint pagination."""

    def test_action_items_pagination_default(self, client: TestClient):
        """Test default pagination parameters."""
        # Create test data via API
        for i in range(25):
            payload = {"description": f"Task {i}"}
            r = client.post("/action-items/", json=payload)
            assert r.status_code == 201

        r = client.get("/action-items/")
        assert r.status_code == 200
        data = r.json()

        # Verify default pagination
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total"] == 25
        assert data["total_pages"] == 2
        assert len(data["items"]) == 20

    def test_action_items_pagination_custom_params(self, client: TestClient):
        """Test custom pagination parameters."""
        # Create test data via API
        for i in range(50):
            payload = {"description": f"Task {i}"}
            r = client.post("/action-items/", json=payload)
            assert r.status_code == 201

            # Mark half as completed
            if i % 2 == 0:
                item_id = r.json()["id"]
                r = client.put(f"/action-items/{item_id}/complete")
                assert r.status_code == 200

        r = client.get("/action-items/?page=4&page_size=15")
        assert r.status_code == 200
        data = r.json()

        assert data["page"] == 4
        assert data["page_size"] == 15
        assert data["total"] == 50
        assert data["total_pages"] == 4
        assert len(data["items"]) == 5  # Last page has fewer items

    def test_action_items_empty_last_page(self, client: TestClient):
        """Test empty last page when page exceeds available data."""
        # Create test data via API
        for i in range(10):
            payload = {"description": f"Task {i}"}
            r = client.post("/action-items/", json=payload)
            assert r.status_code == 201

        r = client.get("/action-items/?page=100&page_size=5")
        assert r.status_code == 200
        data = r.json()

        assert data["page"] == 100
        assert data["page_size"] == 5
        assert data["total"] == 10
        assert data["total_pages"] == 2
        assert len(data["items"]) == 0

    def test_action_items_with_completed_filter_pagination(self, client: TestClient):
        """Test pagination combined with completed filter."""
        # Create test data via API
        for i in range(30):
            payload = {"description": f"Task {i}"}
            r = client.post("/action-items/", json=payload)
            assert r.status_code == 201
            item_id = r.json()["id"]

            # Mark first 10 as completed
            if i < 10:
                r = client.put(f"/action-items/{item_id}/complete")
                assert r.status_code == 200

        # Test pagination with completed=true filter
        r = client.get("/action-items/?completed=true&page=1&page_size=5")
        assert r.status_code == 200
        data = r.json()

        assert data["total"] == 10
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert data["total_pages"] == 2
        assert len(data["items"]) == 5

        # Verify all items are completed
        for item in data["items"]:
            assert item["completed"] is True

    def test_action_items_with_uncompleted_filter_pagination(self, client: TestClient):
        """Test pagination with completed=false filter."""
        # Create test data via API
        for i in range(35):
            payload = {"description": f"Task {i}"}
            r = client.post("/action-items/", json=payload)
            assert r.status_code == 201
            item_id = r.json()["id"]

            # Mark first 15 as completed
            if i < 15:
                r = client.put(f"/action-items/{item_id}/complete")
                assert r.status_code == 200

        r = client.get("/action-items/?completed=false&page=2&page_size=10")
        assert r.status_code == 200
        data = r.json()

        assert data["total"] == 20  # 35 - 15 completed
        assert data["page"] == 2
        assert data["page_size"] == 10
        assert data["total_pages"] == 2
        assert len(data["items"]) == 10

        # Verify all items are not completed
        for item in data["items"]:
            assert item["completed"] is False

    def test_action_items_page_size_exceeds_maximum(self, client: TestClient):
        """Test that page_size > 100 returns validation error."""
        r = client.get("/action-items/?page_size=101")
        assert r.status_code == 422

    def test_action_items_page_less_than_one(self, client: TestClient):
        """Test that page < 1 returns validation error."""
        r = client.get("/action-items/?page=0")
        assert r.status_code == 422

    def test_action_items_empty_database(self, client: TestClient):
        """Test pagination with empty database."""
        r = client.get("/action-items/")
        assert r.status_code == 200
        data = r.json()

        assert data["total"] == 0
        assert data["total_pages"] == 0
        assert len(data["items"]) == 0

    def test_action_items_response_structure(self, client: TestClient):
        """Test that response has all required fields with correct types."""
        payload = {"description": "Test task"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201
        item_id = r.json()["id"]

        # Mark as completed
        r = client.put(f"/action-items/{item_id}/complete")
        assert r.status_code == 200

        r = client.get("/action-items/")
        assert r.status_code == 200
        data = r.json()

        # Verify all fields exist
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

        # Verify field types
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["page_size"], int)
        assert isinstance(data["total_pages"], int)

        # Verify item structure
        if len(data["items"]) > 0:
            item = data["items"][0]
            assert "id" in item
            assert "description" in item
            assert "completed" in item
            assert "created_at" in item


class TestPaginationEdgeCases:
    """Test suite for pagination edge cases and corner scenarios."""

    def test_notes_pagination_page_size_1(self, client: TestClient):
        """Test pagination with page_size=1 (minimum allowed)."""
        for i in range(5):
            payload = {"title": f"Note {i}", "content": f"Content {i}"}
            r = client.post("/notes/", json=payload)
            assert r.status_code == 201

        r = client.get("/notes/?page=3&page_size=1")
        assert r.status_code == 200
        data = r.json()

        assert data["page"] == 3
        assert data["page_size"] == 1
        assert data["total"] == 5
        assert data["total_pages"] == 5
        assert len(data["items"]) == 1

    def test_notes_pagination_max_page_size(self, client: TestClient):
        """Test pagination with page_size=100 (maximum allowed)."""
        for i in range(150):
            payload = {"title": f"Note {i}", "content": f"Content {i}"}
            r = client.post("/notes/", json=payload)
            assert r.status_code == 201

        r = client.get("/notes/?page=1&page_size=100")
        assert r.status_code == 200
        data = r.json()

        assert data["page"] == 1
        assert data["page_size"] == 100
        assert data["total"] == 150
        assert data["total_pages"] == 2
        assert len(data["items"]) == 100

    def test_action_items_pagination_page_size_1(self, client: TestClient):
        """Test pagination with page_size=1 for action items."""
        for i in range(3):
            payload = {"description": f"Task {i}"}
            r = client.post("/action-items/", json=payload)
            assert r.status_code == 201

        r = client.get("/action-items/?page=2&page_size=1")
        assert r.status_code == 200
        data = r.json()

        assert data["page"] == 2
        assert data["page_size"] == 1
        assert data["total"] == 3
        assert data["total_pages"] == 3
        assert len(data["items"]) == 1

    def test_notes_pagination_with_zero_total(self, client: TestClient):
        """Test pagination calculations when total=0."""
        r = client.get("/notes/?page=1&page_size=20")
        assert r.status_code == 200
        data = r.json()

        assert data["total"] == 0
        assert data["total_pages"] == 0
        assert len(data["items"]) == 0

    def test_pagination_total_pages_calculation(self, client: TestClient):
        """Test total_pages calculation in various scenarios."""
        # Create exactly 20 items (one full page)
        for i in range(20):
            payload = {"title": f"Note {i}", "content": f"Content {i}"}
            r = client.post("/notes/", json=payload)
            assert r.status_code == 201

        r = client.get("/notes/?page_size=20")
        data = r.json()
        assert data["total"] == 20
        assert data["total_pages"] == 1

        # Add one more item
        payload = {"title": "Extra", "content": "Extra"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201

        r = client.get("/notes/?page_size=20")
        data = r.json()
        assert data["total"] == 21
        assert data["total_pages"] == 2
