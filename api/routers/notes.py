"""
Notes API Router

Handles all note-related endpoints including audio upload, listing, and retrieval.
"""
import shutil
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from core.config import settings
from core.models import Note, NoteStatus
from api.schemas import NoteRead, NoteList, NoteCreate, NoteTextCreate
from infra.db import get_db

router = APIRouter()


@router.post("/text", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
async def create_text_note(
    note_data: NoteTextCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new note from text content.
    
    This endpoint bypasses audio transcription and directly creates a note
    with the provided text content. The note will be marked as TRANSCRIBED
    and will proceed to LLM processing for summary and action item extraction.
    
    Useful for:
    - Quick testing without audio files
    - Direct text input from users
    - Importing text notes from other sources
    """
    note_id = uuid.uuid4()
    
    # Create DB record with TRANSCRIBED status since we already have the text
    new_note = Note(
        id=note_id,
        title=note_data.title,
        source_filename="text_input",
        audio_path="",  # No audio file for text notes
        transcript=note_data.content,
        status=NoteStatus.TRANSCRIBED,
        tags=note_data.tags
    )
    
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    
    return new_note


@router.post("/audio", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
async def upload_audio_note(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    tags: Optional[List[str]] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload an audio file to create a new note.
    
    The audio file will be saved to the inbox directory and a database record
    will be created with status UPLOADED. Background workers will process the
    audio for transcription and analysis.
    """
    note_id = uuid.uuid4()
    file_ext = file.filename.split(".")[-1] if file.filename else "wav"
    filename = f"{note_id}.{file_ext}"
    file_path = os.path.join(settings.INBOX_DIR, filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )

    # Create DB record
    new_note = Note(
        id=note_id,
        title=title,
        source_filename=file.filename or "unknown",
        audio_path=file_path,
        status=NoteStatus.UPLOADED,
        tags=tags
    )
    
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    
    return new_note


@router.get("/", response_model=List[NoteList])
async def list_notes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    List recent notes with pagination.
    
    Returns a simplified view of notes ordered by creation time (newest first).
    """
    query = select(Note).order_by(desc(Note.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    notes = result.scalars().all()
    return notes


@router.get("/{note_id}", response_model=NoteRead)
async def get_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get full note details by ID.
    
    Returns complete note information including transcript, summary,
    action items, and metadata if available.
    """
    query = select(Note).where(Note.id == note_id)
    result = await db.execute(query)
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
        
    return note
