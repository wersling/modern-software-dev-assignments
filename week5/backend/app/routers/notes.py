from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note
from ..schemas import NoteCreate, NoteRead, NoteUpdate, PaginatedNotesList

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(db: Session = Depends(get_db)) -> list[NoteRead]:
    rows = db.execute(select(Note)).scalars().all()
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
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    sort: Literal["created_desc", "created_asc", "title_asc", "title_desc"] = Query(
        "created_desc", description="Sort order"
    ),
    db: Session = Depends(get_db),
) -> PaginatedNotesList:
    """
    Search notes with pagination and sorting.

    - Case-insensitive search in both title and content
    - Supports pagination with customizable page size
    - Multiple sorting options
    - SQL wildcards (% and _) are escaped for security
    """

    def escape_like_pattern(pattern: str) -> str:
        """Escape SQL LIKE wildcards (% and _) in search pattern."""
        return pattern.replace("%", "\\%").replace("_", "\\_")

    # Build base query
    query = select(Note)
    search_pattern = None

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
        raise HTTPException(status_code=500, detail=f"Failed to update note: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Failed to delete note: {str(e)}")

    return Response(status_code=204)
