"""
Performance tests for database queries.

This module tests the performance of common query patterns with large datasets.
Tests create 1000+ records and measure execution time to ensure acceptable performance.
"""
import time
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ActionItem, Note, Tag


class TestActionItemsPerformance:
    """Performance tests for ActionItem queries."""

    @pytest.fixture
    def large_action_items_dataset(self, db_session: Session):
        """Create a large dataset of action items for performance testing."""
        items = []
        # Create 1000 completed items
        for i in range(1000):
            item = ActionItem(
                description=f"Completed task {i}", completed=True, created_at=datetime.utcnow()
            )
            items.append(item)

        # Create 1000 incomplete items
        for i in range(1000):
            item = ActionItem(
                description=f"Incomplete task {i}",
                completed=False,
                created_at=datetime.utcnow(),
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()
        return items

    def test_list_completed_items_performance(
        self, db_session: Session, large_action_items_dataset
    ):
        """Test performance of filtering completed items."""
        start_time = time.time()

        query = select(ActionItem).where(ActionItem.completed == True)
        items = db_session.execute(query).scalars().all()

        end_time = time.time()
        execution_time = end_time - start_time

        # Should return 1000 items
        assert len(items) == 1000

        # Execution time should be under 1 second for 2000 total records
        assert execution_time < 1.0, f"Query took {execution_time:.3f}s, expected < 1.0s"

    def test_list_incomplete_items_performance(
        self, db_session: Session, large_action_items_dataset
    ):
        """Test performance of filtering incomplete items."""
        start_time = time.time()

        query = select(ActionItem).where(ActionItem.completed == False)
        items = db_session.execute(query).scalars().all()

        end_time = time.time()
        execution_time = end_time - start_time

        # Should return 1000 items
        assert len(items) == 1000

        # Execution time should be under 1 second
        assert execution_time < 1.0, f"Query took {execution_time:.3f}s, expected < 1.0s"

    def test_list_all_items_performance(
        self, db_session: Session, large_action_items_dataset
    ):
        """Test performance of listing all items without filter."""
        start_time = time.time()

        query = select(ActionItem)
        items = db_session.execute(query).scalars().all()

        end_time = time.time()
        execution_time = end_time - start_time

        # Should return 2000 items
        assert len(items) == 2000

        # Execution time should be under 1 second
        assert execution_time < 1.0, f"Query took {execution_time:.3f}s, expected < 1.0s"


class TestNotesPerformance:
    """Performance tests for Note queries."""

    @pytest.fixture
    def large_notes_dataset(self, db_session: Session):
        """Create a large dataset of notes for performance testing."""
        notes = []
        for i in range(1000):
            note = Note(
                title=f"Note title {i}",
                content=f"This is the content for note {i}. " * 10,  # Longer content
                created_at=datetime.utcnow(),
            )
            notes.append(note)

        db_session.add_all(notes)
        db_session.commit()

        # Create some tags
        tags = []
        for i in range(10):
            tag = Tag(name=f"tag{i}", created_at=datetime.utcnow())
            tags.append(tag)
        db_session.add_all(tags)
        db_session.commit()

        # Attach tags to notes (each note gets 2-3 random tags)
        import random

        for note in notes:
            num_tags = random.randint(1, 3)
            selected_tags = random.sample(tags, num_tags)
            for tag in selected_tags:
                if tag not in note.tags:
                    note.tags.append(tag)

        db_session.commit()
        return notes, tags

    def test_list_all_notes_performance(
        self, db_session: Session, large_notes_dataset
    ):
        """Test performance of listing all notes ordered by created_at DESC."""
        notes, tags = large_notes_dataset

        start_time = time.time()

        query = select(Note).order_by(Note.created_at.desc())
        items = db_session.execute(query).scalars().all()

        end_time = time.time()
        execution_time = end_time - start_time

        # Should return 1000 items
        assert len(items) == 1000

        # Execution time should be under 1 second
        assert execution_time < 1.0, f"Query took {execution_time:.3f}s, expected < 1.0s"

    def test_list_notes_by_tag_performance(
        self, db_session: Session, large_notes_dataset
    ):
        """Test performance of filtering notes by tag with ordering."""
        notes, tags = large_notes_dataset

        # Use the first tag
        tag = tags[0]

        start_time = time.time()

        query = (
            select(Note)
            .join(Note.tags)
            .where(Tag.id == tag.id)
            .order_by(Note.created_at.desc())
        )
        items = db_session.execute(query).scalars().all()

        end_time = time.time()
        execution_time = end_time - start_time

        # Should return some notes (random distribution)
        assert len(items) > 0

        # Execution time should be under 1 second
        assert execution_time < 1.0, f"Query took {execution_time:.3f}s, expected < 1.0s"

    def test_search_notes_performance(self, db_session: Session, large_notes_dataset):
        """Test performance of searching notes with pagination."""
        notes, tags = large_notes_dataset

        start_time = time.time()

        # Search for notes containing specific text
        from sqlalchemy import func, or_

        query = select(Note).where(
            or_(
                func.lower(Note.title).like("%500%"),
                func.lower(Note.content).like("%500%"),
            )
        )
        query = query.order_by(Note.created_at.desc())
        query = query.offset(0).limit(10)

        items = db_session.execute(query).scalars().all()

        end_time = time.time()
        execution_time = end_time - start_time

        # Should return up to 10 items
        assert len(items) <= 10

        # Execution time should be under 1 second
        assert execution_time < 1.0, f"Query took {execution_time:.3f}s, expected < 1.0s"


class TestTagsPerformance:
    """Performance tests for Tag queries."""

    @pytest.fixture
    def large_tags_dataset(self, db_session: Session):
        """Create a large dataset of tags for performance testing."""
        tags = []
        for i in range(1000):
            tag = Tag(name=f"tag{i}", created_at=datetime.utcnow())
            tags.append(tag)

        db_session.add_all(tags)
        db_session.commit()
        return tags

    def test_list_all_tags_performance(self, db_session: Session, large_tags_dataset):
        """Test performance of listing all tags ordered by created_at DESC."""
        start_time = time.time()

        query = select(Tag).order_by(Tag.created_at.desc())
        items = db_session.execute(query).scalars().all()

        end_time = time.time()
        execution_time = end_time - start_time

        # Should return 1000 items
        assert len(items) == 1000

        # Execution time should be under 1 second
        assert execution_time < 1.0, f"Query took {execution_time:.3f}s, expected < 1.0s"

    def test_search_tags_performance(self, db_session: Session, large_tags_dataset):
        """Test performance of case-insensitive tag name search."""
        from sqlalchemy import func

        start_time = time.time()

        # Search for tags containing '5'
        query = select(Tag).where(func.lower(Tag.name).like("%5%"))
        items = db_session.execute(query).scalars().all()

        end_time = time.time()
        execution_time = end_time - start_time

        # Should return tags with '5' in name
        assert len(items) > 0

        # Execution time should be under 1 second
        assert execution_time < 1.0, f"Query took {execution_time:.3f}s, expected < 1.0s"
