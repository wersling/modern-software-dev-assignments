from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: str | None = Field(None, max_length=500, description="Category description")

    @field_validator("name", "description")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        return v.strip() if v else None


class CategoryRead(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryPatch(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)

    @field_validator("name", "description")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        return v.strip() if v else None


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, max_length=10000, description="Note content")
    category_id: int | None = Field(None, description="Category ID")

    @field_validator("title", "content")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    category_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotePatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1, max_length=10000)
    category_id: int | None = None

    @field_validator("title", "content")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        return v.strip() if v else None


class ActionItemCreate(BaseModel):
    description: str = Field(
        ..., min_length=1, max_length=500, description="Action item description"
    )
    category_id: int | None = Field(None, description="Category ID")

    @field_validator("description")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    category_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionItemPatch(BaseModel):
    description: str | None = Field(None, min_length=1, max_length=500)
    completed: bool | None = None
    category_id: int | None = None

    @field_validator("description")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        return v.strip() if v else None


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="Comment content")
    author_name: str = Field(..., min_length=1, max_length=100, description="Author name")
    note_id: int | None = Field(None, description="Note ID (use with action_item_id)")
    action_item_id: int | None = Field(None, description="Action item ID (use with note_id)")

    @field_validator("content", "author_name")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class CommentRead(BaseModel):
    id: int
    content: str
    author_name: str
    note_id: int | None
    action_item_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentPatch(BaseModel):
    content: str | None = Field(None, min_length=1, max_length=2000)
    author_name: str | None = Field(None, min_length=1, max_length=100)

    @field_validator("content", "author_name")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        return v.strip() if v else None
