# backend/app/core/message_bus.py
"""
Async in-memory pub/sub message bus.

- publish(project_id, agent_name, content) -> puts message in per-project queue
- subscribe(project_id) -> returns an async generator that yields messages
  (useful for WebSocket streaming to frontend)

Note: For production across processes, replace this with Redis streams / PubSub / Kafka.
"""

import asyncio
from typing import Dict, Any, AsyncGenerator
import logging
from api.ai.core.utils import get_logger

logger = get_logger("message_bus")


class MessageBus:
    def __init__(self):
        # per-project asyncio.Queue
        self._queues: Dict[int, asyncio.Queue] = {}
        self._lock = asyncio.Lock()

    async def _get_queue(self, project_id: int) -> asyncio.Queue:
        async with self._lock:
            if project_id not in self._queues:
                self._queues[project_id] = asyncio.Queue()
            return self._queues[project_id]

    async def publish(self, project_id: int, agent_name: str, content: str) -> None:
        q = await self._get_queue(project_id)
        msg = {"agent": agent_name, "content": content}
        await q.put(msg)
        logger.debug("Published message for project=%s agent=%s", project_id, agent_name)

    async def subscribe(self, project_id: int) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Async generator that yields messages for a given project_id.
        Consumer should iterate and break when done.
        """
        q = await self._get_queue(project_id)
        while True:
            msg = await q.get()
            yield msg
            # no automatic q.task_done() to keep simple; consumers can implement own pattern
