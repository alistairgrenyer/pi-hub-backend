"""
Core Enums

This module contains enum definitions used throughout the application.
Separated from models.py to allow importing without database dependencies.
"""
import enum


class NoteStatus(str, enum.Enum):
    """Status of a note in the processing pipeline"""
    UPLOADED = "UPLOADED"
    TRANSCRIBED = "TRANSCRIBED"
    PROCESSED = "PROCESSED"
    DONE = "DONE"
    ERROR = "ERROR"
