import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..exceptions import BadRequestException, NotFoundException
from ..models import ActionItem
from ..schemas import (
    ActionItemBulkComplete,
    ActionItemBulkCompleteResponse,
    ActionItemCreate,
    ActionItemRead,
    EnvelopeResponse,
    PaginatedResponse,
)
from ..utils.pagination import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    build_paginated_response,
    get_pagination_params,
)

router = APIRouter(prefix="/action-items", tags=["action_items"])

# Constants for bulk operations
MAX_BULK_ITEMS = 1000

# Configure logging
logger = logging.getLogger(__name__)


@router.get("/", response_model=PaginatedResponse[ActionItemRead])
def list_items(
    completed: Optional[bool] = Query(None, description="Filter by completion status (true/false)"),
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
    List action items with optional completion status filter and pagination.

    Args:
        completed: Optional boolean filter for completion status
        page: Page number for pagination (default: 1)
        page_size: Number of items per page (default: 20, max: 100)
        db: Database session

    Returns:
        Paginated list of action items matching the filter criteria
    """
    query = select(ActionItem)

    # Apply filter if completed parameter is provided
    if completed is not None:
        query = query.where(ActionItem.completed == completed)

    # Validate pagination parameters
    validated_page, validated_page_size = get_pagination_params(page, page_size)

    # Get total count
    count_query = select(func.count(ActionItem.id))
    if completed is not None:
        count_query = count_query.where(ActionItem.completed == completed)
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
        model_class=ActionItemRead,
    )


@router.post("/", response_model=EnvelopeResponse[ActionItemRead], status_code=201)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> dict:
    item = ActionItem(description=payload.description, completed=False)
    db.add(item)
    db.flush()
    db.refresh(item)
    return {"ok": True, "data": ActionItemRead.model_validate(item)}


@router.put("/{item_id}/complete", response_model=EnvelopeResponse[ActionItemRead])
def complete_item(item_id: int, db: Session = Depends(get_db)) -> dict:
    item = db.get(ActionItem, item_id)
    if not item:
        raise NotFoundException("ActionItem", f"id={item_id}")
    item.completed = True
    db.add(item)
    db.flush()
    db.refresh(item)
    return {"ok": True, "data": ActionItemRead.model_validate(item)}


@router.post("/bulk-complete", response_model=EnvelopeResponse[ActionItemBulkCompleteResponse], status_code=200)
def bulk_complete_items(
    payload: ActionItemBulkComplete, db: Session = Depends(get_db)
) -> dict:
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
        raise BadRequestException(
            f"Cannot bulk complete more than {MAX_BULK_ITEMS} items at once. "
            f"Received {len(payload.ids)} items."
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
        raise BadRequestException("Database error occurred while updating action items") from e

    # Build response
    return {
        "ok": True,
        "data": ActionItemBulkCompleteResponse(
            updated=[ActionItemRead.model_validate(item) for item in updated_items],
            total_updated=len(updated_items),
            not_found=not_found_ids,
        ),
    }
