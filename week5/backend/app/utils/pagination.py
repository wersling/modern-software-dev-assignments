"""Pagination utilities for database queries.

This module provides reusable functions for paginating SQLAlchemy queries,
including parameter validation, query construction, and response building.
"""

from math import ceil
from typing import Any, Optional

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from ..schemas import PaginatedResponse

# Pagination constants
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def get_pagination_params(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> tuple[int, int]:
    """Validate and normalize pagination parameters.

    Args:
        page: Page number (1-indexed). If None, defaults to DEFAULT_PAGE.
        page_size: Number of items per page. If None, defaults to DEFAULT_PAGE_SIZE.

    Returns:
        Tuple of (validated_page, validated_page_size)

    Raises:
        ValueError: If page < 1, page_size < 1, or page_size > MAX_PAGE_SIZE
    """
    validated_page = page if page is not None else DEFAULT_PAGE
    validated_page_size = page_size if page_size is not None else DEFAULT_PAGE_SIZE

    # Validate page number
    if validated_page < 1:
        raise ValueError("page must be >= 1")

    # Validate page size
    if validated_page_size < 1:
        raise ValueError("page_size must be >= 1")
    if validated_page_size > MAX_PAGE_SIZE:
        raise ValueError(f"page_size must be <= {MAX_PAGE_SIZE}")

    return validated_page, validated_page_size


def paginate_query(
    query: Select[tuple[Any]],
    db: Session,
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> PaginatedResponse[Any]:
    """Apply pagination to a SQLAlchemy query and return a paginated response.

    This function:
    1. Counts the total number of records matching the query
    2. Applies offset/limit to get the current page
    3. Calculates total_pages
    4. Returns a PaginatedResponse with all pagination metadata

    Args:
        query: SQLAlchemy select query (will be modified in place)
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        PaginatedResponse containing items, total, page, page_size, and total_pages

    Example:
        ```python
        from sqlalchemy import select

        query = select(Note).order_by(Note.created_at.desc())
        response = paginate_query(query, db, page=2, page_size=10)
        # Returns: PaginatedResponse[Note] with items from page 2
        ```
    """
    # Validate pagination parameters
    page, page_size = get_pagination_params(page, page_size)

    # Get total count
    # Extract the base entity from the query
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar()

    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 0

    # Apply pagination
    offset = (page - 1) * page_size
    paginated_query = query.offset(offset).limit(page_size)

    # Execute query
    items = db.execute(paginated_query).scalars().all()

    # Return raw items - the calling code should handle Pydantic validation
    # This allows the function to be generic and work with any model
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def build_paginated_response(
    items: list[Any],
    total: int,
    page: int,
    page_size: int,
    model_class: type,
) -> dict:
    """Build a paginated response dictionary with Pydantic-validated items.

    This is a helper function to convert database models to Pydantic models
    and prepare the response dictionary.

    Args:
        items: List of database model instances
        total: Total number of records
        page: Current page number
        page_size: Number of items per page
        model_class: Pydantic model class for validation (e.g., NoteRead)

    Returns:
        Dictionary with all pagination fields ready for JSON response

    Example:
        ```python
        result = paginate_query(query, db, page=1, page_size=20)
        response_data = build_paginated_response(
            items=result["items"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            model_class=NoteRead
        )
        return response_data
        ```
    """
    # Validate items using the provided Pydantic model
    validated_items = [model_class.model_validate(item) for item in items]

    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 0

    return {
        "items": validated_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
