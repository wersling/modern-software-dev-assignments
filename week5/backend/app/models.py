from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Association table for Note-Tag many-to-many relationship
note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    Index("ix_note_tags_note_id", "note_id"),
    Index("ix_note_tags_tag_id", "tag_id"),
)


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    tags = relationship("Tag", secondary=note_tags, back_populates="notes", lazy="selectin")

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("ix_notes_created_at_desc", created_at.desc()),
        Index("ix_notes_title_lower", func.lower(title)),  # For case-insensitive title search
    )


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    completed = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Additional composite indexes for common query patterns
    __table_args__ = (Index("ix_action_items_created_at_desc", created_at.desc()),)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    notes = relationship("Note", secondary=note_tags, back_populates="tags", lazy="selectin")

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("ix_tags_name_lower", func.lower(name)),  # For case-insensitive name search
        Index("ix_tags_created_at_desc", created_at.desc()),
    )
