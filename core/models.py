from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, Enum, DateTime, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

from infra.db import Base
from core.enums import NoteStatus

class Note(Base):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[NoteStatus] = mapped_column(Enum(NoteStatus), default=NoteStatus.UPLOADED, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    source_filename: Mapped[str] = mapped_column(String)
    audio_path: Mapped[str] = mapped_column(String)
    
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    action_items: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    metadata_: Mapped[Optional[Any]] = mapped_column("metadata", JSON, nullable=True) # metadata is reserved in SQLAlchemy

    def __repr__(self):
        return f"<Note id={self.id} title={self.title} status={self.status}>"
