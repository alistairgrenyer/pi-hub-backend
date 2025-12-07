from datetime import datetime
from typing import Optional, List, Any, Dict
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from core.enums import NoteStatus

class NoteBase(BaseModel):
    title: Optional[str] = None
    tags: Optional[List[str]] = None

class NoteCreate(NoteBase):
    pass

class NoteTextCreate(NoteBase):
    """Schema for creating a text-based note (no audio file)."""
    content: str

class NoteUpdate(NoteBase):
    status: Optional[NoteStatus] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    action_items: Optional[List[str]] = None
    metadata_: Optional[Dict[str, Any]] = None

class NoteRead(NoteBase):
    id: UUID
    status: NoteStatus
    created_at: datetime
    updated_at: datetime
    source_filename: str
    audio_path: str
    transcript: Optional[str] = None
    summary: Optional[str] = None
    action_items: Optional[List[str]] = None
    metadata_: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class NoteList(BaseModel):
    id: UUID
    title: Optional[str]
    status: NoteStatus
    created_at: datetime
    tags: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)
