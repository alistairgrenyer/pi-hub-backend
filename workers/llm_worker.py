import asyncio
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
# from llama_cpp import Llama # Commented out to avoid import error if not installed locally, but code assumes it's there in Docker

from core.config import settings
from core.models import Note, NoteStatus
from core.logging import get_logger
from workers.base import BaseWorker

logger = get_logger(__name__)

class LLMWorker(BaseWorker):
    def __init__(self):
        super().__init__("LLMWorker")
        # Mocking Llama for now if not available, or use real one
        try:
            from llama_cpp import Llama
            logger.info(f"Loading LLM model from: {settings.LLM_MODEL_PATH}")
            self.llm = Llama(
                model_path=settings.LLM_MODEL_PATH,
                n_ctx=2048,
                n_threads=4
            )
        except ImportError:
            logger.warning("llama-cpp-python not installed. LLM Worker will fail if run.")
            self.llm = None
        except Exception as e:
            logger.warning(f"Could not load LLM model: {e}. Ensure model exists at {settings.LLM_MODEL_PATH}")
            self.llm = None

    async def process_next(self, session: AsyncSession) -> bool:
        query = select(Note).where(Note.status == NoteStatus.TRANSCRIBED).order_by(Note.created_at).limit(1)
        result = await session.execute(query)
        note = result.scalar_one_or_none()

        if not note:
            return False

        logger.info(f"Processing note with LLM: {note.id}")

        if not self.llm:
             # Fallback for dev/testing without model
            logger.warning("LLM not loaded, skipping actual inference.")
            note.summary = "Summary generation skipped (LLM not loaded)."
            note.action_items = ["Check LLM configuration"]
            note.status = NoteStatus.PROCESSED
            session.add(note)
            await session.commit()
            return True

        try:
            # Improved prompt engineering for consistent JSON output
            prompt = f"""[INST] You are a helpful assistant that extracts information from meeting notes and transcripts.

Analyze this transcript and extract:
1. A concise summary (2-3 sentences)
2. Action items as a list
3. A short descriptive title

Transcript:
{note.transcript[:3000]}

Respond ONLY with valid JSON in this exact format:
{{
  "summary": "your summary here",
  "action_items": ["first action", "second action"],
  "title": "your title here"
}}

Do not include any text before or after the JSON. [/INST]"""
            
            output = await asyncio.to_thread(
                self.llm,
                prompt,
                max_tokens=512,
                stop=["</s>"],
                echo=False
            )
            
            text_response = output['choices'][0]['text'].strip()
            
            # Attempt to parse JSON
            try:
                # Find JSON substring if extra text exists
                start = text_response.find('{')
                end = text_response.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = text_response[start:end]
                    data = json.loads(json_str)
                    
                    note.summary = data.get("summary", "")
                    note.action_items = data.get("action_items", [])
                    if not note.title: # Only update title if missing
                        note.title = data.get("title", "Untitled Note")
                else:
                    note.summary = text_response
                    note.action_items = []
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM JSON response, saving raw text.")
                note.summary = text_response
            
            note.status = NoteStatus.PROCESSED
            session.add(note)
            await session.commit()
            logger.info(f"LLM processing complete for: {note.id}")
            return True

        except Exception as e:
            logger.error(f"LLM processing failed for {note.id}: {e}")
            note.status = NoteStatus.ERROR
            note.metadata_ = {"error": str(e)}
            session.add(note)
            await session.commit()
            return True

if __name__ == "__main__":
    from core.logging import setup_logging
    setup_logging()
    worker = LLMWorker()
    asyncio.run(worker.run())
