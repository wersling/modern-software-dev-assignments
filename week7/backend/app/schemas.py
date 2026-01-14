from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)

    @field_validator("title", "content")
    @classmethod
    def strip_and_validate(cls, v: str) -> str:
        """Strip whitespace and ensure non-empty string."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("must not be empty or whitespace only")
        return stripped


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotePatch(BaseModel):
    title: str | None = None
    content: str | None = None


class ActionItemCreate(BaseModel):
    description: str = Field(..., min_length=1)

    @field_validator("description")
    @classmethod
    def strip_and_validate(cls, v: str) -> str:
        """Strip whitespace and ensure non-empty string."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("must not be empty or whitespace only")
        return stripped


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionItemPatch(BaseModel):
    description: str | None = None
    completed: bool | None = None
