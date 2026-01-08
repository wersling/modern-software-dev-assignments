import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem
from ..schemas import (
    ActionItemBulkComplete,
    ActionItemBulkCompleteResponse,
    ActionItemCreate,
    ActionItemRead,
)

router = APIRouter(prefix="/action-items", tags=["action_items"])

# Constants for bulk operations
MAX_BULK_ITEMS = 1000

# Configure logging
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[ActionItemRead])
def list_items(
    completed: Optional[bool] = Query(None, description="Filter by completion status (true/false)"),
    db: Session = Depends(get_db),
) -> list[ActionItemRead]:
    """
    List action items with optional completion status filter.

    Args:
        completed: Optional boolean filter for completion status
        db: Database session

    Returns:
        List of action items matching the filter criteria
    """
    query = select(ActionItem)

    # Apply filter if completed parameter is provided
    if completed is not None:
        query = query.where(ActionItem.completed == completed)

    rows = db.execute(query).scalars().all()
    return [ActionItemRead.model_validate(row) for row in rows]


@router.post("/", response_model=ActionItemRead, status_code=201)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> ActionItemRead:
    item = ActionItem(description=payload.description, completed=False)
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.put("/{item_id}/complete", response_model=ActionItemRead)
def complete_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    item.completed = True
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.post("/bulk-complete", response_model=ActionItemBulkCompleteResponse, status_code=200)
def bulk_complete_items(
    payload: ActionItemBulkComplete, db: Session = Depends(get_db)
) -> ActionItemBulkCompleteResponse:
    """
    Bulk complete action items by marking them as completed.

    This endpoint accepts a list of action item IDs and marks all of them as completed.
    The operation is performed within a database transaction to ensure atomicity.
    If any ID is not found, it will be included in the 'not_found' list in the response.

    Args:
        payload: Bulk complete request containing list of IDs to complete
        db: Database session

    Returns:
        Response containing updated items, count of updated items, and any not found IDs
    """
    # Validate bulk operation size limit
    if len(payload.ids) > MAX_BULK_ITEMS:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot bulk complete more than {MAX_BULK_ITEMS} items at once. "
            f"Received {len(payload.ids)} items.",
        )

    # Find all existing items
    stmt = select(ActionItem).where(ActionItem.id.in_(payload.ids))
    items = db.execute(stmt).scalars().all()

    # Determine which IDs were not found
    found_ids = {item.id for item in items}
    not_found_ids = [id for id in payload.ids if id not in found_ids]

    # Update all found items
    updated_items = []
    for item in items:
        item.completed = True
        db.add(item)
        updated_items.append(item)

    # Flush changes to database within transaction
    # If any error occurs, the transaction will be rolled back automatically
    try:
        db.flush()
        # Refresh all items to get updated state
        for item in updated_items:
            db.refresh(item)
    except Exception as e:
        # Log the detailed error for debugging
        logger.error(
            "Failed to bulk complete action items. IDs: %s, Error: %s",
            payload.ids,
            str(e),
            exc_info=True,
        )
        # Return generic error message to client
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while updating action items",
        ) from e

    # Build response
    return ActionItemBulkCompleteResponse(
        updated=[ActionItemRead.model_validate(item) for item in updated_items],
        total_updated=len(updated_items),
        not_found=not_found_ids,
    )
