"""WebSocket server for tournament real-time updates."""

import asyncio
import websockets
import json
import logging
from typing import Set, Dict, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TournamentWebSocket:
    """WebSocket server for tournament real-time updates."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.connections: Set[websockets.WebSocketServerProtocol] = set()
        self.tournament_subscriptions: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
    
    async def register(self, websocket: websockets.WebSocketServerProtocol) -> None:
        """Register a new WebSocket connection."""
        self.connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.connections)}")
    
    async def unregister(self, websocket: websockets.WebSocketServerProtocol) -> None:
        """Unregister a WebSocket connection."""
        self.connections.discard(websocket)
        # Remove from all tournament subscriptions
        for subs in self.tournament_subscriptions.values():
            subs.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.connections)}")
    
    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected clients."""
        if self.connections:
            message_json = json.dumps(message)
            await asyncio.gather(
                *[ws.send(message_json) for ws in self.connections.copy()],
                return_exceptions=True
            )
    
    async def broadcast_to_tournament(
        self, 
        tournament_id: str, 
        message: Dict[str, Any]
    ) -> None:
        """Broadcast message to clients subscribed to a specific tournament."""
        if tournament_id in self.tournament_subscriptions:
            subscribers = self.tournament_subscriptions[tournament_id].copy()
            if subscribers:
                message_json = json.dumps(message)
                await asyncio.gather(
                    *[ws.send(message_json) for ws in subscribers],
                    return_exceptions=True
                )
    
    async def handle_message(
        self, 
        websocket: websockets.WebSocketServerProtocol, 
        data: Dict[str, Any]
    ) -> None:
        """Handle incoming WebSocket message."""
        msg_type = data.get("type")
        
        if msg_type == "subscribe_tournament":
            tournament_id = data.get("tournament_id")
            if tournament_id:
                if tournament_id not in self.tournament_subscriptions:
                    self.tournament_subscriptions[tournament_id] = set()
                self.tournament_subscriptions[tournament_id].add(websocket)
                await websocket.send(json.dumps({
                    "type": "subscribed",
                    "tournament_id": tournament_id
                }))
        
        elif msg_type == "unsubscribe_tournament":
            tournament_id = data.get("tournament_id")
            if tournament_id and tournament_id in self.tournament_subscriptions:
                self.tournament_subscriptions[tournament_id].discard(websocket)
                await websocket.send(json.dumps({
                    "type": "unsubscribed",
                    "tournament_id": tournament_id
                }))
        
        elif msg_type == "ping":
            await websocket.send(json.dumps({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            }))
    
    async def handler(
        self, 
        websocket: websockets.WebSocketServerProtocol, 
        path: str
    ) -> None:
        """Handle WebSocket connection."""
        await self.register(websocket)
        try:
            # Send connection confirmation
            await websocket.send(json.dumps({
                "type": "connected",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "esportez-websocket"
            }))
            
            # Handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON"
                    }))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)
    
    async def start(self) -> None:
        """Start the WebSocket server."""
        logger.info(f"Starting WebSocket server on ws://{self.host}:{self.port}")
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()  # run forever


async def main():
    """Main entry point."""
    server = TournamentWebSocket(host="localhost", port=8765)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
