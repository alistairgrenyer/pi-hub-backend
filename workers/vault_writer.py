import asyncio
import os
import yaml
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import Note, NoteStatus
from core.logging import get_logger
from workers.base import BaseWorker

logger = get_logger(__name__)

class VaultWriterWorker(BaseWorker):
    def __init__(self):
        super().__init__("VaultWriterWorker")

    async def process_next(self, session: AsyncSession) -> bool:
        query = select(Note).where(Note.status == NoteStatus.PROCESSED).order_by(Note.created_at).limit(1)
        result = await session.execute(query)
        note = result.scalar_one_or_none()

        if not note:
            return False

        logger.info(f"Writing note to vault: {note.id}")
        
        try:
            # Prepare Frontmatter
            frontmatter = {
                "id": str(note.id),
                "title": note.title or "Untitled",
                "created_at": note.created_at.isoformat(),
                "tags": note.tags or [],
                "status": "done"
            }
            
            # Prepare Content
            content_parts = ["---"]
            content_parts.append(yaml.dump(frontmatter, default_flow_style=False).strip())
            content_parts.append("---\n")
            
            if note.summary:
                content_parts.append(f"# Summary\n{note.summary}\n")
            
            if note.action_items:
                content_parts.append("# Action Items")
                if isinstance(note.action_items, list):
                    for item in note.action_items:
                        content_parts.append(f"- [ ] {item}")
                else:
                    content_parts.append(str(note.action_items))
                content_parts.append("\n")
                
            if note.transcript:
                content_parts.append(f"# Transcript\n{note.transcript}\n")
                
            file_content = "\n".join(content_parts)
            
            # Determine File Path: YYYY/MM/DD-note-{id}.md
            now = datetime.now()
            year_dir = os.path.join(settings.VAULT_DIR, now.strftime("%Y"))
            month_dir = os.path.join(year_dir, now.strftime("%m"))
            os.makedirs(month_dir, exist_ok=True)
            
            filename = f"{now.strftime('%d')}-{note.title.lower().replace(' ', '-') if note.title else 'note'}-{str(note.id)[:8]}.md"
            file_path = os.path.join(month_dir, filename)
            
            # Write File
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_content)
                
            note.status = NoteStatus.DONE
            session.add(note)
            await session.commit()
            logger.info(f"Vault write complete: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Vault write failed for {note.id}: {e}")
            note.status = NoteStatus.ERROR
            note.metadata_ = {"error": str(e)}
            session.add(note)
            await session.commit()
            return True

if __name__ == "__main__":
    from core.logging import setup_logging
    setup_logging()
    worker = VaultWriterWorker()
    asyncio.run(worker.run())
