from datetime import datetime

# Forward declarations for type hints
from typing import TYPE_CHECKING, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

if TYPE_CHECKING:
    pass  # All models will be available at runtime

# Generic type variable for paginated responses
T = TypeVar("T")


class NoteCreate(BaseModel):
    title: str = Field(
        ..., min_length=1, max_length=200, description="Note title (1-200 characters)"
    )
    content: str = Field(
        ..., min_length=1, max_length=10000, description="Note content (1-10000 characters)"
    )

    @field_validator("title", "content")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Strip leading and trailing whitespace from title and content."""
        if isinstance(v, str):
            return v.strip()
        return v

    @model_validator(mode="after")
    def validate_not_empty(self) -> "NoteCreate":
        """Validate that title and content are not empty after stripping."""
        if self.title == "":
            raise ValueError("title cannot be empty or whitespace only")
        if self.content == "":
            raise ValueError("content cannot be empty or whitespace only")
        return self


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Note title (1-200 characters)"
    )
    content: Optional[str] = Field(
        None, min_length=1, max_length=10000, description="Note content (1-10000 characters)"
    )

    @field_validator("title", "content")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Strip leading and trailing whitespace from title and content."""
        if isinstance(v, str):
            return v.strip()
        return v

    @model_validator(mode="after")
    def validate_not_empty(self) -> "NoteUpdate":
        """Validate that title and content are not empty after stripping (if provided)."""
        if self.title is not None and self.title == "":
            raise ValueError("title cannot be empty or whitespace only")
        if self.content is not None and self.content == "":
            raise ValueError("content cannot be empty or whitespace only")
        return self


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    created_at: datetime
    tags: list["TagRead"] = Field(default=[], description="List of tags associated with this note")


class ActionItemCreate(BaseModel):
    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Action item description (1-1000 characters)",
    )

    @field_validator("description")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Strip leading and trailing whitespace from description."""
        if isinstance(v, str):
            return v.strip()
        return v

    @model_validator(mode="after")
    def validate_not_empty(self) -> "ActionItemCreate":
        """Validate that description is not empty after stripping."""
        if self.description == "":
            raise ValueError("description cannot be empty or whitespace only")
        return self


class ActionItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    completed: bool
    created_at: datetime


class ActionItemBulkComplete(BaseModel):
    """Request model for bulk completing action items."""

    ids: list[int] = Field(
        ..., min_length=1, description="List of action item IDs to mark as completed"
    )

    @field_validator("ids")
    @classmethod
    def validate_ids(cls, v: list[int]) -> list[int]:
        """Validate that IDs list is not empty and contains positive integers."""
        if not v:
            raise ValueError("ids cannot be empty")
        if any(id < 1 for id in v):
            raise ValueError("all IDs must be positive integers")
        return v


class ActionItemBulkCompleteResponse(BaseModel):
    """Response model for bulk complete operation."""

    updated: list[ActionItemRead]
    total_updated: int
    not_found: list[int] = Field(default=[], description="IDs that were not found in the database")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model.

    This model provides a consistent structure for all paginated endpoints,
    including items, total count, current page, page size, and total pages.
    """

    items: list[T] = Field(..., description="List of items for the current page")
    total: int = Field(..., description="Total number of items across all pages", ge=0)
    page: int = Field(..., description="Current page number (starts from 1)", ge=1)
    page_size: int = Field(..., description="Number of items per page", ge=1, le=100)
    total_pages: int = Field(..., description="Total number of pages", ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [],
                    "total": 150,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 8,
                }
            ]
        }
    )


class PaginatedNotesList(BaseModel):
    """Paginated response for notes search (deprecated - use PaginatedResponse instead)."""

    items: list[NoteRead]
    total: int
    page: int
    page_size: int


class TagCreate(BaseModel):
    """Request model for creating a tag."""

    name: str = Field(..., min_length=1, max_length=50, description="Tag name (1-50 characters)")

    @field_validator("name")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Strip leading and trailing whitespace from tag name."""
        if isinstance(v, str):
            return v.strip()
        return v

    @model_validator(mode="after")
    def validate_not_empty(self) -> "TagCreate":
        """Validate that name is not empty after stripping."""
        if self.name == "":
            raise ValueError("name cannot be empty or whitespace only")
        return self


class TagRead(BaseModel):
    """Response model for a tag."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime


class TagAttach(BaseModel):
    """Request model for attaching tags to a note."""

    tag_ids: list[int] = Field(
        ..., min_length=1, description="List of tag IDs to attach to the note"
    )

    @field_validator("tag_ids")
    @classmethod
    def validate_tag_ids(cls, v: list[int]) -> list[int]:
        """Validate that tag IDs list is not empty and contains positive integers."""
        if not v:
            raise ValueError("tag_ids cannot be empty")
        if any(tag_id < 1 for tag_id in v):
            raise ValueError("all tag IDs must be positive integers")
        return v


# =============================================================================
# Envelope Response Schemas
# =============================================================================


class EnvelopeErrorDetail(BaseModel):
    """Error detail for envelope error responses.

    This structure provides consistent error information across all endpoints.
    """

    code: str = Field(..., description="Error code (e.g., 'NOT_FOUND', 'VALIDATION_ERROR')")
    message: str = Field(..., description="Human-readable error message")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "code": "NOT_FOUND",
                    "message": "Note with id=999 not found",
                }
            ]
        }
    )


class EnvelopeErrorResponse(BaseModel):
    """Standard error response envelope.

    All error responses follow this structure for consistent client-side handling.

    Example:
        {
            "ok": false,
            "error": {
                "code": "NOT_FOUND",
                "message": "Note with id=999 not found"
            }
        }
    """

    ok: bool = Field(False, description="Always false for error responses")
    error: EnvelopeErrorDetail = Field(..., description="Error details")


class EnvelopeResponse(BaseModel, Generic[T]):
    """Standard success response envelope.

    All success responses follow this structure for consistent client-side handling.

    Type Parameters:
        T: The type of data being returned

    Example:
        {
            "ok": true,
            "data": {
                "id": 1,
                "title": "Note Title",
                "content": "Note Content"
            }
        }
    """

    ok: bool = Field(True, description="Always true for success responses")
    data: T = Field(..., description="Response data")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "ok": True,
                    "data": {"id": 1, "title": "Example", "content": "Content"},
                }
            ]
        }
    )


# =============================================================================
# Extraction Schemas
# =============================================================================


class ExtractResponse(BaseModel):
    """Response model for extraction preview (apply=false).

    Returns extracted data without persisting to the database.
    """

    tags: list[str] = Field(
        default=[], description="List of extracted tag names (hashtags from content)"
    )
    action_items: list[str] = Field(
        default=[],
        description="List of extracted action item descriptions (lines ending with '!' or starting with 'todo:')",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "tags": ["urgent", "frontend"],
                    "action_items": ["Fix the navigation bug!", "todo: Update documentation"],
                }
            ]
        }
    )


class ExtractApplyResponse(BaseModel):
    """Response model for extraction with apply (apply=true).

    Returns persisted database objects after applying extraction results.
    """

    tags: list[TagRead] = Field(default=[], description="List of Tag objects created or found")
    action_items: list[ActionItemRead] = Field(
        default=[], description="List of ActionItem objects created"
    )
    note: NoteRead = Field(..., description="Updated Note object with new tags attached")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "tags": [
                        {
                            "id": 1,
                            "name": "urgent",
                            "created_at": "2025-01-14T10:00:00Z",
                        },
                        {
                            "id": 2,
                            "name": "frontend",
                            "created_at": "2025-01-14T10:00:00Z",
                        },
                    ],
                    "action_items": [
                        {
                            "id": 1,
                            "description": "Fix the navigation bug!",
                            "completed": False,
                            "created_at": "2025-01-14T10:00:00Z",
                        },
                        {
                            "id": 2,
                            "description": "todo: Update documentation",
                            "completed": False,
                            "created_at": "2025-01-14T10:00:00Z",
                        },
                    ],
                    "note": {
                        "id": 1,
                        "title": "Meeting Notes",
                        "content": "Discussed #urgent #frontend issues. Fix the navigation bug!\ntodo: Update documentation",
                        "created_at": "2025-01-14T09:00:00Z",
                        "tags": [
                            {
                                "id": 1,
                                "name": "urgent",
                                "created_at": "2025-01-14T10:00:00Z",
                            },
                            {
                                "id": 2,
                                "name": "frontend",
                                "created_at": "2025-01-14T10:00:00Z",
                            },
                        ],
                    },
                }
            ]
        }
    )
