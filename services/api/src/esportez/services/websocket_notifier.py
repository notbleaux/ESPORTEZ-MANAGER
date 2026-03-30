"""WebSocket notifier service for tournament events."""

import asyncio
import websockets
import json
import logging
from typing import Set, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketNotifier:
    """Notify connected clients of tournament events."""

    def __init__(self):
        self.connections: Set[websockets.WebSocketServerProtocol] = set()
        self.ws_server = None

    async def register(self, websocket: websockets.WebSocketServerProtocol) -> None:
        """Register a new connection."""
        self.connections.add(websocket)
        logger.info(f"Client registered. Total connections: {len(self.connections)}")

    async def unregister(self, websocket: websockets.WebSocketServerProtocol) -> None:
        """Unregister a connection."""
        self.connections.discard(websocket)
        logger.info(f"Client unregistered. Total connections: {len(self.connections)}")

    async def broadcast(self, message: dict) -> None:
        """Broadcast message to all connected clients."""
        if self.connections:
            message_json = json.dumps(message)
            try:
                await asyncio.gather(
                    *[ws.send(message_json) for ws in self.connections.copy()],
                    return_exceptions=True
                )
                logger.debug(f"Broadcasted message to {len(self.connections)} clients")
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")

    async def notify_tournament_update(
        self,
        tournament_id: str,
        update_type: str,
        data: dict
    ) -> None:
        """Send tournament-specific update."""
        await self.broadcast({
            "type": update_type,
            "tournament_id": tournament_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def notify_tournament_created(self, tournament_id: str, name: str) -> None:
        """Notify that a tournament was created."""
        await self.broadcast({
            "type": "tournament_created",
            "tournament_id": tournament_id,
            "name": name,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def notify_tournament_started(
        self,
        tournament_id: str,
        bracket: Optional[dict] = None
    ) -> None:
        """Notify that a tournament has started."""
        message = {
            "type": "tournament_started",
            "tournament_id": tournament_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        if bracket:
            message["bracket"] = bracket
        await self.broadcast(message)


# Global notifier instance
ws_notifier = WebSocketNotifier()
