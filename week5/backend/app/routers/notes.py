import logging
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note, Tag
from ..schemas import NoteCreate, NoteRead, NoteUpdate, PaginatedNotesList, TagAttach

router = APIRouter(prefix="/notes", tags=["notes"])

# Configure logging
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[NoteRead])
def list_notes(
    tag_id: Optional[int] = Query(None, description="Filter notes by tag ID"),
    tag: Optional[str] = Query(None, description="Filter notes by tag name (case-insensitive)"),
    db: Session = Depends(get_db),
) -> list[NoteRead]:
    """
    List all notes with optional tag filtering.

    Args:
        tag_id: Optional tag ID to filter notes (only notes with this tag will be returned)
        tag: Optional tag name to filter notes (case-insensitive search)
        db: Database session

    Returns:
        List of notes ordered by creation time (newest first)

    Note:
        If both tag_id and tag are provided, tag_id takes precedence.
        The tags relationship is automatically loaded via selectin loading.
    """
    query = select(Note).order_by(Note.created_at.desc())

    # Apply tag filtering if provided
    if tag_id is not None:
        # Filter by tag ID
        # Join with note_tags association table to filter by tag
        query = query.join(Note.tags).where(Tag.id == tag_id)
    elif tag is not None:
        # Filter by tag name (case-insensitive)
        # Escape SQL wildcards to prevent unexpected behavior
        escaped_tag = tag.replace("%", "\\%").replace("_", "\\_")
        tag_pattern = f"%{escaped_tag}%"
        query = query.join(Note.tags).where(
            func.lower(Tag.name).like(func.lower(tag_pattern), escape="\\")
        )

    rows = db.execute(query).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/search/", response_model=PaginatedNotesList)
def search_notes(
    q: Optional[str] = Query(None, description="Search query for title and content"),
    tag_id: Optional[int] = Query(None, description="Filter notes by tag ID"),
    tag: Optional[str] = Query(None, description="Filter notes by tag name (case-insensitive)"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    sort: Literal["created_desc", "created_asc", "title_asc", "title_desc"] = Query(
        "created_desc", description="Sort order"
    ),
    db: Session = Depends(get_db),
) -> PaginatedNotesList:
    """
    Search notes with pagination, sorting, and optional tag filtering.

    - Case-insensitive search in both title and content
    - Supports pagination with customizable page size
    - Multiple sorting options
    - Optional filtering by tag ID or tag name
    - SQL wildcards (% and _) are escaped for security

    Note:
        If both tag_id and tag are provided, tag_id takes precedence.
    """

    def escape_like_pattern(pattern: str) -> str:
        """Escape SQL LIKE wildcards (% and _) in search pattern."""
        return pattern.replace("%", "\\%").replace("_", "\\_")

    # Build base query
    query = select(Note)
    search_pattern = None
    tag_filter_applied = False

    # Apply tag filtering if provided
    if tag_id is not None:
        query = query.join(Note.tags).where(Tag.id == tag_id)
        tag_filter_applied = True
    elif tag is not None:
        escaped_tag = tag.replace("%", "\\%").replace("_", "\\_")
        tag_pattern = f"%{escaped_tag}%"
        query = query.join(Note.tags).where(
            func.lower(Tag.name).like(func.lower(tag_pattern), escape="\\")
        )
        tag_filter_applied = True

    # Apply search filter if query is provided
    if q:
        # Case-insensitive search in both title and content
        # Escape SQL wildcards to prevent unexpected behavior
        escaped_q = escape_like_pattern(q)
        search_pattern = f"%{escaped_q}%"
        query = query.where(
            or_(
                func.lower(Note.title).like(func.lower(search_pattern), escape="\\"),
                func.lower(Note.content).like(func.lower(search_pattern), escape="\\"),
            )
        )

    # Get total count before pagination (optimized to avoid subquery)
    count_query = select(func.count(Note.id))

    # Apply the same filters to count query
    if tag_filter_applied:
        if tag_id is not None:
            count_query = count_query.join(Note.tags).where(Tag.id == tag_id)
        elif tag is not None:
            escaped_tag = tag.replace("%", "\\%").replace("_", "\\_")
            tag_pattern = f"%{escaped_tag}%"
            count_query = count_query.join(Note.tags).where(
                func.lower(Tag.name).like(func.lower(tag_pattern), escape="\\")
            )

    if q:
        count_query = count_query.where(
            or_(
                func.lower(Note.title).like(func.lower(search_pattern), escape="\\"),
                func.lower(Note.content).like(func.lower(search_pattern), escape="\\"),
            )
        )
    total = db.execute(count_query).scalar()

    # Apply sorting
    if sort == "created_desc":
        query = query.order_by(Note.created_at.desc())
    elif sort == "created_asc":
        query = query.order_by(Note.created_at.asc())
    elif sort == "title_asc":
        query = query.order_by(Note.title.asc())
    elif sort == "title_desc":
        query = query.order_by(Note.title.desc())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    rows = db.execute(query).scalars().all()

    return PaginatedNotesList(
        items=[NoteRead.model_validate(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)


@router.put("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Update only provided fields (partial update)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)

    try:
        db.commit()
        db.refresh(note)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to update note: {str(e)}"
        ) from e

    return NoteRead.model_validate(note)


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> Response:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    try:
        db.delete(note)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to delete note: {str(e)}"
        ) from e

    return Response(status_code=204)


@router.post("/{note_id}/tags", response_model=NoteRead)
def attach_tags_to_note(
    note_id: int, payload: TagAttach, db: Session = Depends(get_db)
) -> NoteRead:
    """
    Attach tags to a note.

    This endpoint adds the specified tags to a note. If a tag doesn't exist,
    it will be created automatically. Duplicate tags are automatically removed.

    Args:
        note_id: ID of the note to attach tags to
        payload: TagAttach request containing list of tag IDs
        db: Database session

    Returns:
        Updated note with all associated tags

    Raises:
        HTTPException 404: If note not found
        HTTPException 400: If some tags don't exist
        HTTPException 500: If database error occurs

    Example:
        POST /notes/1/tags
        {
            "tag_ids": [1, 2, 3]
        }
    """
    # Get the note
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail=f"Note with id {note_id} not found")

    # Remove duplicates from tag_ids list
    unique_tag_ids = list(set(payload.tag_ids))

    # Validate that all tags exist
    existing_tags = db.execute(select(Tag).where(Tag.id.in_(unique_tag_ids))).scalars().all()

    existing_tag_ids = {tag.id for tag in existing_tags}
    missing_tag_ids = set(unique_tag_ids) - existing_tag_ids

    if missing_tag_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Tags with ids {sorted(missing_tag_ids)} not found",
        )

    try:
        # Add tags to the note (SQLAlchemy automatically handles duplicates)
        for tag in existing_tags:
            if tag not in note.tags:
                note.tags.append(tag)

        db.commit()
        db.refresh(note)
    except Exception as e:
        db.rollback()
        logger.error("Failed to attach tags to note %s. Error: %s", note_id, str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail="Database error occurred while attaching tags"
        ) from e

    return NoteRead.model_validate(note)


@router.delete("/{note_id}/tags/{tag_id}", response_model=NoteRead)
def remove_tag_from_note(note_id: int, tag_id: int, db: Session = Depends(get_db)) -> NoteRead:
    """
    Remove a tag from a note.

    This endpoint removes the specified tag from a note. If the tag is not
    associated with the note, a 404 error is returned.

    Args:
        note_id: ID of the note to remove tag from
        tag_id: ID of the tag to remove
        db: Database session

    Returns:
        Updated note with remaining tags

    Raises:
        HTTPException 404: If note not found or tag not associated with note
        HTTPException 500: If database error occurs

    Example:
        DELETE /notes/1/tags/2
    """
    # Get the note
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail=f"Note with id {note_id} not found")

    # Check if the tag is associated with the note
    tag_to_remove = None
    for tag in note.tags:
        if tag.id == tag_id:
            tag_to_remove = tag
            break

    if not tag_to_remove:
        raise HTTPException(
            status_code=404,
            detail=f"Tag with id {tag_id} is not associated with note {note_id}",
        )

    try:
        # Remove the tag from the note
        note.tags.remove(tag_to_remove)
        db.commit()
        db.refresh(note)
    except Exception as e:
        db.rollback()
        logger.error(
            "Failed to remove tag %s from note %s. Error: %s",
            tag_id,
            note_id,
            str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Database error occurred while removing tag"
        ) from e

    return NoteRead.model_validate(note)
