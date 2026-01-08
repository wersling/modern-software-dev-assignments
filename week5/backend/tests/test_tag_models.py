"""
Tag model tests - Direct model validation and constraints.

Tests the Tag model's field validation, constraints, and database-level behavior.
"""
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Base, Tag, note_tags
from app.models import Note as NoteModel


def test_tag_name_unique_constraint(db_session: Session):
    """Test that tag names must be unique (database constraint)."""
    # Create first tag
    tag1 = Tag(name="UniqueTag")
    db_session.add(tag1)
    db_session.commit()

    # Try to create duplicate tag (should fail at database level)
    tag2 = Tag(name="UniqueTag")
    db_session.add(tag2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_tag_name_nullable(db_session: Session):
    """Test that tag name cannot be null."""
    tag = Tag(name=None)
    db_session.add(tag)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_tag_name_max_length(db_session: Session):
    """Test that tag name respects max length constraint."""
    # Name at max length (50) should work
    tag = Tag(name="x" * 50)
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    assert tag.name == "x" * 50


def test_tag_auto_fields(db_session: Session):
    """Test that id and created_at are auto-generated."""
    tag = Tag(name="AutoFields")
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)

    assert tag.id is not None
    assert isinstance(tag.id, int)
    assert tag.created_at is not None


def test_note_tags_association_table_structure(db_session: Session):
    """Test that the note_tags association table works correctly."""
    # Create a note and tags
    note = NoteModel(title="Test Note", content="Test content")
    tag1 = Tag(name="Tag1")
    tag2 = Tag(name="Tag2")

    db_session.add_all([note, tag1, tag2])
    db_session.commit()
    db_session.refresh(note)
    db_session.refresh(tag1)
    db_session.refresh(tag2)

    # Manually insert into association table
    db_session.execute(
        note_tags.insert().values(note_id=note.id, tag_id=tag1.id)
    )
    db_session.execute(
        note_tags.insert().values(note_id=note.id, tag_id=tag2.id)
    )
    db_session.commit()

    # Query back through association table
    result = db_session.execute(
        note_tags.select().where(note_tags.c.note_id == note.id)
    ).fetchall()

    assert len(result) == 2
    tag_ids = [row.tag_id for row in result]
    assert tag1.id in tag_ids
    assert tag2.id in tag_ids


def test_note_tags_unique_constraint(db_session: Session):
    """Test that the same note-tag pair cannot be duplicated."""
    # Create a note and tag
    note = NoteModel(title="Test Note", content="Test content")
    tag = Tag(name="UniqueTag")

    db_session.add_all([note, tag])
    db_session.commit()
    db_session.refresh(note)
    db_session.refresh(tag)

    # Insert first association
    db_session.execute(
        note_tags.insert().values(note_id=note.id, tag_id=tag.id)
    )
    db_session.commit()

    # Try to insert duplicate (should fail due to composite PK)
    # Need to rollback first to reset session state
    db_session.rollback()
    with pytest.raises(IntegrityError):
        db_session.execute(
            note_tags.insert().values(note_id=note.id, tag_id=tag.id)
        )
        db_session.commit()


def test_tag_relationship_with_notes(db_session: Session):
    """Test Tag model's relationship with Notes."""
    # Create notes and tags
    note1 = NoteModel(title="Note 1", content="Content 1")
    note2 = NoteModel(title="Note 2", content="Content 2")
    tag = Tag(name="SharedTag")

    db_session.add_all([note1, note2, tag])
    db_session.commit()
    db_session.refresh(note1)
    db_session.refresh(note2)
    db_session.refresh(tag)

    # Associate tag with both notes
    note1.tags.append(tag)
    note2.tags.append(tag)
    db_session.commit()

    # Test relationship from tag side
    db_session.refresh(tag)
    assert len(tag.notes) == 2
    note_titles = [n.title for n in tag.notes]
    assert "Note 1" in note_titles
    assert "Note 2" in note_titles


def test_delete_tag_cascades_to_associations(db_session: Session):
    """Test that deleting a tag removes it from note_tags association table."""
    # Create note and tag
    note = NoteModel(title="Test Note", content="Test content")
    tag = Tag(name="ToDelete")

    db_session.add_all([note, tag])
    db_session.commit()
    db_session.refresh(note)
    db_session.refresh(tag)

    # Associate tag with note
    note.tags.append(tag)
    db_session.commit()

    # Verify association exists
    result = db_session.execute(
        note_tags.select().where(
            note_tags.c.note_id == note.id,
            note_tags.c.tag_id == tag.id
        )
    ).fetchall()
    assert len(result) == 1

    # Delete the tag
    db_session.delete(tag)
    db_session.commit()

    # Verify association is removed
    result = db_session.execute(
        note_tags.select().where(
            note_tags.c.note_id == note.id,
            note_tags.c.tag_id == tag.id
        )
    ).fetchall()
    assert len(result) == 0


def test_delete_note_cascades_to_associations(db_session: Session):
    """Test that deleting a note removes its tag associations."""
    # Create note and tag
    note = NoteModel(title="Test Note", content="Test content")
    tag = Tag(name="KeepTag")

    db_session.add_all([note, tag])
    db_session.commit()
    db_session.refresh(note)
    db_session.refresh(tag)

    # Associate tag with note
    note.tags.append(tag)
    db_session.commit()

    # Delete the note
    db_session.delete(note)
    db_session.commit()

    # Tag should still exist
    assert db_session.get(Tag, tag.id) is not None

    # Association should be removed
    result = db_session.execute(
        note_tags.select().where(note_tags.c.note_id == note.id)
    ).fetchall()
    assert len(result) == 0
