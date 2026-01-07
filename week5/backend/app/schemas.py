from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Note title (1-200 characters)")
    content: str = Field(..., min_length=1, max_length=10000, description="Note content (1-10000 characters)")

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
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Note title (1-200 characters)")
    content: Optional[str] = Field(None, min_length=1, max_length=10000, description="Note content (1-10000 characters)")

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


class ActionItemCreate(BaseModel):
    description: str


class ActionItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    completed: bool
    created_at: datetime
