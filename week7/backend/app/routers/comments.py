from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Comment
from ..schemas import CommentCreate, CommentPatch, CommentRead

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/", response_model=list[CommentRead])
def list_comments(
    db: Session = Depends(get_db),
    note_id: Optional[int] = None,
    action_item_id: Optional[int] = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
) -> list[CommentRead]:
    stmt = select(Comment)

    if note_id is not None:
        stmt = stmt.where(Comment.note_id == note_id)
    if action_item_id is not None:
        stmt = stmt.where(Comment.action_item_id == action_item_id)

    stmt = stmt.order_by(asc(Comment.created_at))
    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    return [CommentRead.model_validate(row) for row in rows]


@router.post("/", response_model=CommentRead, status_code=201)
def create_comment(payload: CommentCreate, db: Session = Depends(get_db)) -> CommentRead:
    # Validate that exactly one of note_id or action_item_id is provided
    if payload.note_id is None and payload.action_item_id is None:
        raise HTTPException(
            status_code=400, detail="Either note_id or action_item_id must be provided"
        )
    if payload.note_id is not None and payload.action_item_id is not None:
        raise HTTPException(
            status_code=400, detail="Cannot provide both note_id and action_item_id"
        )

    comment = Comment(
        content=payload.content,
        author_name=payload.author_name,
        note_id=payload.note_id,
        action_item_id=payload.action_item_id,
    )
    db.add(comment)
    db.flush()
    db.refresh(comment)
    return CommentRead.model_validate(comment)


@router.get("/{comment_id}", response_model=CommentRead)
def get_comment(comment_id: int, db: Session = Depends(get_db)) -> CommentRead:
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return CommentRead.model_validate(comment)


@router.patch("/{comment_id}", response_model=CommentRead)
def patch_comment(
    comment_id: int, payload: CommentPatch, db: Session = Depends(get_db)
) -> CommentRead:
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if payload.content is not None:
        comment.content = payload.content
    if payload.author_name is not None:
        comment.author_name = payload.author_name

    db.add(comment)
    db.flush()
    db.refresh(comment)
    return CommentRead.model_validate(comment)


@router.delete("/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: Session = Depends(get_db)) -> None:
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.flush()
