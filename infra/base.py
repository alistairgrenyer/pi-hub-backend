from infra.db import Base
from core.models import Note

# Import all models here so Alembic can find them
__all__ = ["Base", "Note"]
