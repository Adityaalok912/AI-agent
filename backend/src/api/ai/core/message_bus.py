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
        # per-project asyncio.Queue that will hold JSON strings
        self._queues: Dict[int, asyncio.Queue] = {}
        self._lock = asyncio.Lock()

    async def _get_queue(self, project_id: int) -> asyncio.Queue:
        async with self._lock:
            if project_id not in self._queues:
                self._queues[project_id] = asyncio.Queue()
            return self._queues[project_id]

    async def publish(self, project_id: int, agent_name: str, content: str) -> None:
        """
        Publishes a message to a project's channel.

        Args:
            project_id: The ID of the project.
            agent_name: The name of the agent, used for logging.
            content: The JSON string message to be published.
        """
        q = await self._get_queue(project_id)
        # THE FIX: Directly put the 'content' (which is already a valid JSON string from the orchestrator)
        # into the queue without wrapping it in another dictionary.
        await q.put(content)
        logger.debug("Published message for project=%s agent=%s", project_id, agent_name)

    async def subscribe(self, project_id: int) -> AsyncGenerator[str, None]:
        """
        Async generator that yields JSON string messages for a given project_id.
        """
        q = await self._get_queue(project_id)
        while True:
            # The message is now correctly expected to be a string.
            msg = await q.get()
            yield msg