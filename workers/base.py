import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from infra.db import AsyncSessionLocal
from core.logging import get_logger

logger = get_logger(__name__)

class BaseWorker(ABC):
    def __init__(self, name: str, poll_interval: int = 5):
        self.name = name
        self.poll_interval = poll_interval
        self.running = True

    async def run(self):
        logger.info(f"Starting worker: {self.name}")
        while self.running:
            try:
                async with AsyncSessionLocal() as session:
                    processed = await self.process_next(session)
                    if not processed:
                        await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in worker {self.name}: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)

    @abstractmethod
    async def process_next(self, session: AsyncSession) -> bool:
        """
        Process the next available item.
        Returns True if an item was processed, False if queue was empty.
        """
        pass
