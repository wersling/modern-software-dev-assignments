from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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


class PaginatedNotesList(BaseModel):
    """Paginated response for notes search."""

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
