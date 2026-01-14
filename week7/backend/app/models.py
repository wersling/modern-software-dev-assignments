from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TimestampMixin:
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Category(Base, TimestampMixin):
    """Category model for organizing notes and action items."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Relationships
    notes = relationship("Note", back_populates="category", cascade="all, delete-orphan")
    action_items = relationship(
        "ActionItem", back_populates="category", cascade="all, delete-orphan"
    )


class Note(Base, TimestampMixin):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # Relationships
    category = relationship("Category", back_populates="notes")
    comments = relationship("Comment", back_populates="note", cascade="all, delete-orphan")


class ActionItem(Base, TimestampMixin):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # Relationships
    category = relationship("Category", back_populates="action_items")
    comments = relationship("Comment", back_populates="action_item", cascade="all, delete-orphan")


class Comment(Base, TimestampMixin):
    """Comment model for notes and action items."""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_name = Column(String(100), nullable=False)

    # Foreign keys (one should be null, the other set)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=True)
    action_item_id = Column(Integer, ForeignKey("action_items.id"), nullable=True)

    # Relationships
    note = relationship("Note", back_populates="comments")
    action_item = relationship("ActionItem", back_populates="comments")
