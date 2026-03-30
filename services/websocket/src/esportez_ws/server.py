"""WebSocket server for tournament real-time updates."""

import asyncio
import websockets
import json
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TournamentWebSocketServer:
    """WebSocket server for tournament real-time updates."""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.connections: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        self.global_connections: Set[websockets.WebSocketServerProtocol] = set()
        self.client_info: Dict[websockets.WebSocketServerProtocol, dict] = {}

    async def register(
        self,
        websocket: websockets.WebSocketServerProtocol,
        tournament_id: Optional[str] = None
    ) -> None:
        """Register new connection."""
        if tournament_id:
            if tournament_id not in self.connections:
                self.connections[tournament_id] = set()
            self.connections[tournament_id].add(websocket)
            self.client_info[websocket] = {"tournament_id": tournament_id}
            logger.info(f"Client subscribed to tournament {tournament_id}")
        else:
            self.global_connections.add(websocket)
            self.client_info[websocket] = {"tournament_id": None}
            logger.info("Client connected (global)")

    async def unregister(
        self,
        websocket: websockets.WebSocketServerProtocol,
        tournament_id: Optional[str] = None
    ) -> None:
        """Unregister connection."""
        if tournament_id and tournament_id in self.connections:
            self.connections[tournament_id].discard(websocket)
        self.global_connections.discard(websocket)
        if websocket in self.client_info:
            del self.client_info[websocket]
        logger.info("Client disconnected")

    async def broadcast_to_tournament(
        self,
        tournament_id: str,
        message: dict
    ) -> None:
        """Broadcast to tournament subscribers."""
        if tournament_id in self.connections:
            message_json = json.dumps(message)
            disconnected = []
            for ws in self.connections[tournament_id].copy():
                try:
                    await ws.send(message_json)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.append(ws)
            # Clean up disconnected clients
            for ws in disconnected:
                self.connections[tournament_id].discard(ws)

    async def broadcast_global(self, message: dict) -> None:
        """Broadcast to all global connections."""
        if self.global_connections:
            message_json = json.dumps(message)
            disconnected = []
            for ws in self.global_connections.copy():
                try:
                    await ws.send(message_json)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.append(ws)
            # Clean up disconnected clients
            for ws in disconnected:
                self.global_connections.discard(ws)

    async def broadcast_all(self, message: dict) -> None:
        """Broadcast to all connected clients."""
        await self.broadcast_global(message)
        for tournament_id in self.connections:
            await self.broadcast_to_tournament(tournament_id, message)

    async def handler(
        self,
        websocket: websockets.WebSocketServerProtocol,
        path: str
    ) -> None:
        """Handle WebSocket connection."""
        # Parse tournament ID from path
        tournament_id = None
        if path.startswith("/tournament/"):
            parts = path.split("/")
            if len(parts) >= 3:
                tournament_id = parts[2]

        await self.register(websocket, tournament_id)

        try:
            # Send welcome message
            await websocket.send(json.dumps({
                "type": "connected",
                "tournament_id": tournament_id,
                "timestamp": datetime.utcnow().isoformat(),
                "service": "esportez-websocket"
            }))

            # Handle incoming messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, data, tournament_id)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON"
                    }))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket, tournament_id)

    async def handle_message(
        self,
        websocket: websockets.WebSocketServerProtocol,
        data: dict,
        tournament_id: Optional[str]
    ) -> None:
        """Handle client message."""
        msg_type = data.get("type")

        if msg_type == "subscribe":
            # Subscribe to specific tournament
            new_tournament_id = data.get("tournament_id")
            if new_tournament_id:
                await self.unregister(websocket, tournament_id)
                await self.register(websocket, new_tournament_id)
                await websocket.send(json.dumps({
                    "type": "subscribed",
                    "tournament_id": new_tournament_id,
                    "timestamp": datetime.utcnow().isoformat()
                }))

        elif msg_type == "unsubscribe":
            # Unsubscribe from tournament
            await self.unregister(websocket, tournament_id)
            self.global_connections.add(websocket)
            self.client_info[websocket] = {"tournament_id": None}
            await websocket.send(json.dumps({
                "type": "unsubscribed",
                "timestamp": datetime.utcnow().isoformat()
            }))

        elif msg_type == "ping":
            await websocket.send(json.dumps({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            }))

        elif msg_type == "get_bracket":
            # Client requesting bracket data
            tid = data.get("tournament_id", tournament_id)
            await websocket.send(json.dumps({
                "type": "bracket_data",
                "tournament_id": tid,
                "bracket": {},  # Placeholder - would fetch from database
                "timestamp": datetime.utcnow().isoformat()
            }))

        elif msg_type == "get_status":
            # Client requesting tournament status
            tid = data.get("tournament_id", tournament_id)
            await websocket.send(json.dumps({
                "type": "status_data",
                "tournament_id": tid,
                "status": "unknown",  # Placeholder
                "timestamp": datetime.utcnow().isoformat()
            }))

        else:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Unknown message type: {msg_type}"
            }))

    async def start(self) -> None:
        """Start the WebSocket server."""
        logger.info(f"Starting WebSocket server on ws://{self.host}:{self.port}")
        async with websockets.serve(
            self.handler,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=10
        ):
            logger.info(f"WebSocket server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # run forever


async def main():
    """Main entry point."""
    server = TournamentWebSocketServer(host="localhost", port=8765)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
