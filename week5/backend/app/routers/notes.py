import logging
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..exceptions import BadRequestException, ConflictException, NotFoundException
from ..models import ActionItem, Note, Tag
from ..schemas import (
    ActionItemRead,
    EnvelopeResponse,
    ExtractApplyResponse,
    ExtractResponse,
    NoteCreate,
    NoteRead,
    NoteUpdate,
    PaginatedNotesList,
    PaginatedResponse,
    TagAttach,
    TagRead,
)
from ..services.extract import extract_from_content
from ..utils.pagination import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    build_paginated_response,
    get_pagination_params,
)

router = APIRouter(prefix="/notes", tags=["notes"])

# Configure logging
logger = logging.getLogger(__name__)


@router.get("/", response_model=PaginatedResponse[NoteRead])
def list_notes(
    tag_id: Optional[int] = Query(None, description="Filter notes by tag ID"),
    tag: Optional[str] = Query(None, description="Filter notes by tag name (case-insensitive)"),
    page: int = Query(DEFAULT_PAGE, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(
        DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description="Number of items per page (max 100)",
    ),
    db: Session = Depends(get_db),
) -> dict:
    """
    List all notes with optional tag filtering and pagination.

    Args:
        tag_id: Optional tag ID to filter notes (only notes with this tag will be returned)
        tag: Optional tag name to filter notes (case-insensitive search)
        page: Page number for pagination (default: 1)
        page_size: Number of items per page (default: 20, max: 100)
        db: Database session

    Returns:
        Paginated list of notes ordered by creation time (newest first)

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

    # Validate pagination parameters
    validated_page, validated_page_size = get_pagination_params(page, page_size)

    # Get total count - we need to count the base query before pagination
    # For queries with joins, we count distinct note ids to avoid duplicates
    if tag_id is not None or tag is not None:
        # When tag filter is applied, count distinct notes
        count_query = select(func.count(Note.id)).select_from(Note)
        if tag_id is not None:
            count_query = count_query.join(Note.tags).where(Tag.id == tag_id)
        elif tag is not None:
            escaped_tag = tag.replace("%", "\\%").replace("_", "\\_")
            tag_pattern = f"%{escaped_tag}%"
            count_query = count_query.join(Note.tags).where(
                func.lower(Tag.name).like(func.lower(tag_pattern), escape="\\")
            )
    else:
        # No tag filter, simple count
        count_query = select(func.count(Note.id))

    total = db.execute(count_query).scalar()

    # Apply pagination
    offset = (validated_page - 1) * validated_page_size
    paginated_query = query.offset(offset).limit(validated_page_size)

    rows = db.execute(paginated_query).scalars().all()

    # Build paginated response
    return build_paginated_response(
        items=rows,
        total=total,
        page=validated_page,
        page_size=validated_page_size,
        model_class=NoteRead,
    )


@router.post("/", response_model=EnvelopeResponse[NoteRead], status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> dict:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return {"ok": True, "data": NoteRead.model_validate(note)}


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


@router.get("/{note_id}", response_model=EnvelopeResponse[NoteRead])
def get_note(note_id: int, db: Session = Depends(get_db)) -> dict:
    note = db.get(Note, note_id)
    if not note:
        raise NotFoundException("Note", f"id={note_id}")
    return {"ok": True, "data": NoteRead.model_validate(note)}


@router.put("/{note_id}", response_model=EnvelopeResponse[NoteRead])
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)) -> dict:
    note = db.get(Note, note_id)
    if not note:
        raise NotFoundException("Note", f"id={note_id}")

    # Update only provided fields (partial update)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)

    try:
        db.commit()
        db.refresh(note)
    except Exception as e:
        db.rollback()
        logger.error("Failed to update note %s. Error: %s", note_id, str(e), exc_info=True)
        raise BadRequestException(f"Failed to update note: {str(e)}") from e

    return {"ok": True, "data": NoteRead.model_validate(note)}


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> Response:
    note = db.get(Note, note_id)
    if not note:
        raise NotFoundException("Note", f"id={note_id}")

    try:
        db.delete(note)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Failed to delete note %s. Error: %s", note_id, str(e), exc_info=True)
        raise BadRequestException(f"Failed to delete note: {str(e)}") from e

    return Response(status_code=204)


@router.post("/{note_id}/tags", response_model=EnvelopeResponse[NoteRead])
def attach_tags_to_note(
    note_id: int, payload: TagAttach, db: Session = Depends(get_db)
) -> dict:
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
        NotFoundException: If note not found
        BadRequestException: If some tags don't exist
        BadRequestException: If database error occurs

    Example:
        POST /notes/1/tags
        {
            "tag_ids": [1, 2, 3]
        }
    """
    # Get the note
    note = db.get(Note, note_id)
    if not note:
        raise NotFoundException("Note", f"id={note_id}")

    # Remove duplicates from tag_ids list
    unique_tag_ids = list(set(payload.tag_ids))

    # Validate that all tags exist
    existing_tags = db.execute(select(Tag).where(Tag.id.in_(unique_tag_ids))).scalars().all()

    existing_tag_ids = {tag.id for tag in existing_tags}
    missing_tag_ids = set(unique_tag_ids) - existing_tag_ids

    if missing_tag_ids:
        raise BadRequestException(f"Tags with ids {sorted(missing_tag_ids)} not found")

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
        raise BadRequestException("Database error occurred while attaching tags") from e

    return {"ok": True, "data": NoteRead.model_validate(note)}


@router.delete("/{note_id}/tags/{tag_id}", response_model=EnvelopeResponse[NoteRead])
def remove_tag_from_note(note_id: int, tag_id: int, db: Session = Depends(get_db)) -> dict:
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
        NotFoundException: If note not found or tag not associated with note
        BadRequestException: If database error occurs

    Example:
        DELETE /notes/1/tags/2
    """
    # Get the note
    note = db.get(Note, note_id)
    if not note:
        raise NotFoundException("Note", f"id={note_id}")

    # Check if the tag is associated with the note
    tag_to_remove = None
    for tag in note.tags:
        if tag.id == tag_id:
            tag_to_remove = tag
            break

    if not tag_to_remove:
        raise NotFoundException(
            "Tag", f"id={tag_id} is not associated with note {note_id}"
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
        raise BadRequestException("Database error occurred while removing tag") from e

    return {"ok": True, "data": NoteRead.model_validate(note)}


@router.post("/{note_id}/extract", response_model=EnvelopeResponse[ExtractResponse | ExtractApplyResponse])
def extract_from_note(
    note_id: int,
    apply: bool = Query(False, description="Whether to persist extracted tags and action items to database"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Extract tags and action items from a note's content.

    This endpoint analyzes the note content and extracts:
    - Tags: #hashtag patterns (e.g., #urgent, #frontend)
    - Action items: Lines ending with '!', starting with 'todo:', or - [ ] task format

    When apply=false (default), returns extracted data without persisting.
    When apply=true, creates/links tags and action items in the database.

    Args:
        note_id: ID of the note to extract from
        apply: If true, persist results; if false, preview only
        db: Database session

    Returns:
        ExtractResponse: Preview of extracted data (apply=false)
        ExtractApplyResponse: Persisted database objects (apply=true)

    Raises:
        NotFoundException: If note not found
        BadRequestException: If database error occurs

    Examples:
        # Preview extraction (no persistence)
        POST /notes/1/extract

        # Apply extraction (persist to database)
        POST /notes/1/extract?apply=true

    Extraction Rules:
        Tags:
        - Match standalone #tag patterns
        - Support Chinese: #中文标签
        - Support special chars: #tag-1, #tag_2
        - Avoid matching in code blocks or markdown headers

        Action Items:
        - Lines ending with ! (e.g., "Fix this bug!")
        - Lines starting with todo: (case-insensitive)
        - - [ ] task format (Markdown checkbox)
        - All extracted descriptions are deduplicated
    """
    # Get the note
    note = db.get(Note, note_id)
    if not note:
        raise NotFoundException("Note", f"id={note_id}")

    # Extract content using the extract service
    extract_result = extract_from_content(note.content)

    # If apply=false, return preview without persisting
    if not apply:
        return {
            "ok": True,
            "data": ExtractResponse(
                tags=extract_result.tags,
                action_items=extract_result.action_items,
            ),
        }

    # Apply=true: Persist tags and action items to database
    try:
        # Process tags: get or create, then link to note
        tag_objects = []
        for tag_name in extract_result.tags:
            # Check if tag already exists
            existing_tag = db.execute(select(Tag).where(Tag.name == tag_name)).scalar_one_or_none()

            if existing_tag:
                # Use existing tag
                tag_obj = existing_tag
            else:
                # Create new tag
                tag_obj = Tag(name=tag_name)
                db.add(tag_obj)
                db.flush()  # Get the ID without committing

            tag_objects.append(tag_obj)

            # Link tag to note (SQLAlchemy handles duplicates in many-to-many)
            if tag_obj not in note.tags:
                note.tags.append(tag_obj)

        # Process action items: create new records
        action_item_objects = []
        for description in extract_result.action_items:
            # Create new action item (ActionItem has no note_id FK)
            action_item = ActionItem(description=description, completed=False)
            db.add(action_item)
            db.flush()  # Get the ID without committing
            action_item_objects.append(action_item)

        # Commit all changes atomically
        db.commit()

        # Refresh to get database-generated values
        db.refresh(note)
        for tag_obj in tag_objects:
            db.refresh(tag_obj)
        for action_item_obj in action_item_objects:
            db.refresh(action_item_obj)

    except Exception as e:
        # Rollback on any error
        db.rollback()
        logger.error(
            "Failed to extract and persist data for note %s. Error: %s",
            note_id,
            str(e),
            exc_info=True,
        )
        raise BadRequestException(f"Database error occurred while extracting content: {str(e)}") from e

    # Return persisted objects
    return {
        "ok": True,
        "data": ExtractApplyResponse(
            tags=[TagRead.model_validate(tag) for tag in tag_objects],
            action_items=[ActionItemRead.model_validate(item) for item in action_item_objects],
            note=NoteRead.model_validate(note),
        ),
    }
