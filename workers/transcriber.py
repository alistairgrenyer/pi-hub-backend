import asyncio
from faster_whisper import WhisperModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import Note, NoteStatus
from core.logging import get_logger
from workers.base import BaseWorker

logger = get_logger(__name__)

class TranscriberWorker(BaseWorker):
    def __init__(self):
        super().__init__("TranscriberWorker")
        # Initialize model lazily or here if memory permits
        logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL_SIZE}")
        # Run on CPU for broad compatibility, change to "cuda" if GPU available
        self.model = WhisperModel(settings.WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")

    async def process_next(self, session: AsyncSession) -> bool:
        # Find next UPLOADED note
        query = select(Note).where(Note.status == NoteStatus.UPLOADED).order_by(Note.created_at).limit(1)
        result = await session.execute(query)
        note = result.scalar_one_or_none()

        if not note:
            return False

        logger.info(f"Transcribing note: {note.id}")
        
        try:
            # Run transcription in thread pool to avoid blocking async loop
            segments, info = await asyncio.to_thread(
                self.model.transcribe, note.audio_path, beam_size=5
            )
            
            # Collect all segments
            transcript_text = "".join([segment.text for segment in segments])
            
            note.transcript = transcript_text.strip()
            note.status = NoteStatus.TRANSCRIBED
            session.add(note)
            await session.commit()
            logger.info(f"Transcription complete for: {note.id}")
            return True
            
        except Exception as e:
            logger.error(f"Transcription failed for {note.id}: {e}")
            note.status = NoteStatus.ERROR
            note.metadata_ = {"error": str(e)}
            session.add(note)
            await session.commit()
            return True

if __name__ == "__main__":
    from core.logging import setup_logging
    setup_logging()
    worker = TranscriberWorker()
    asyncio.run(worker.run())
