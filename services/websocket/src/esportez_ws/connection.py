"""WebSocket connection management."""

import asyncio
from typing import Optional
import websockets
import json
from datetime import datetime


class WebSocketConnection:
    """Client WebSocket connection manager."""
    
    def __init__(self, uri: str):
        self.uri = uri
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
    
    async def connect(self) -> None:
        """Connect to WebSocket server."""
        self.websocket = await websockets.connect(self.uri)
        self.connected = True
    
    async def disconnect(self) -> None:
        """Disconnect from WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
    
    async def send(self, message: dict) -> None:
        """Send message to server."""
        if self.websocket:
            await self.websocket.send(json.dumps(message))
    
    async def receive(self) -> Optional[dict]:
        """Receive message from server."""
        if self.websocket:
            message = await self.websocket.recv()
            return json.loads(message)
        return None
    
    async def subscribe_tournament(self, tournament_id: str) -> None:
        """Subscribe to tournament updates."""
        await self.send({
            "type": "subscribe_tournament",
            "tournament_id": tournament_id
        })
    
    async def ping(self) -> None:
        """Send ping message."""
        await self.send({"type": "ping"})
