import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Tag
from ..schemas import TagCreate, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])

# Configure logging
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[TagRead])
def list_tags(
    search: Optional[str] = Query(None, description="Filter tags by name (case-insensitive)"),
    db: Session = Depends(get_db),
) -> list[TagRead]:
    """
    List all tags with optional name filtering.

    Args:
        search: Optional search string to filter tags by name (case-insensitive)
        db: Database session

    Returns:
        List of tags ordered by creation time (newest first)
    """
    query = select(Tag).order_by(Tag.created_at.desc())

    # Apply search filter if provided
    if search:
        # Case-insensitive search in tag name
        # Escape SQL wildcards to prevent unexpected behavior
        escaped_search = search.replace("%", "\\%").replace("_", "\\_")
        search_pattern = f"%{escaped_search}%"
        query = query.where(func.lower(Tag.name).like(func.lower(search_pattern), escape="\\"))

    rows = db.execute(query).scalars().all()
    return [TagRead.model_validate(row) for row in rows]


@router.post("/", response_model=TagRead, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)) -> TagRead:
    """
    Create a new tag.

    Args:
        payload: Tag creation request with name
        db: Database session

    Returns:
        Created tag

    Raises:
        HTTPException 400: If a tag with the same name already exists
    """
    # Check if tag with same name already exists
    existing_tag = db.execute(
        select(Tag).where(func.lower(Tag.name) == func.lower(payload.name))
    ).scalar_one_or_none()

    if existing_tag:
        raise HTTPException(
            status_code=400,
            detail=f"Tag with name '{payload.name}' already exists (case-insensitive)",
        )

    # Create new tag
    tag = Tag(name=payload.name)
    db.add(tag)

    try:
        db.flush()
        db.refresh(tag)
    except Exception as e:
        logger.error("Failed to create tag. Error: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail="Database error occurred while creating tag"
        ) from e

    return TagRead.model_validate(tag)


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)) -> Response:
    """
    Delete a tag by ID.

    This will also remove all associations between this tag and notes
    through the note_tags association table (CASCADE delete).

    Args:
        tag_id: ID of the tag to delete
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        HTTPException 404: If tag not found
        HTTPException 500: If database error occurs
    """
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail=f"Tag with id {tag_id} not found")

    try:
        db.delete(tag)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Failed to delete tag with ID %s. Error: %s", tag_id, str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail="Database error occurred while deleting tag"
        ) from e

    return Response(status_code=204)
