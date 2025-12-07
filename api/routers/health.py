"""
Health Check API Router

Provides system health and monitoring endpoints.
"""
import os
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import settings
from infra.db import get_db

router = APIRouter()


@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.
    
    Verifies:
    - Database connectivity
    - Inbox directory write access
    - Vault directory write access
    
    Returns the status of each component.
    """
    health_status = {
        "database": "unknown",
        "inbox_writable": os.access(settings.INBOX_DIR, os.W_OK),
        "vault_writable": os.access(settings.VAULT_DIR, os.W_OK),
    }
    
    try:
        await db.execute(select(1))
        health_status["database"] = "ok"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        
    return health_status
