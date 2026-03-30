"""WebSocket server tests."""

import pytest
import asyncio
import websockets
import json


@pytest.mark.asyncio
async def test_websocket_connection():
    """Test basic WebSocket connection."""
    from esportez_ws.server import TournamentWebSocketServer

    server = TournamentWebSocketServer(host="localhost", port=8766)

    # Start server using async context manager
    async with websockets.serve(server.handler, "localhost", 8766):
        async with websockets.connect("ws://localhost:8766") as ws:
            response = await ws.recv()
            data = json.loads(response)
            assert data["type"] == "connected"
            assert "timestamp" in data
            assert data["service"] == "esportez-websocket"


@pytest.mark.asyncio
async def test_websocket_ping_pong():
    """Test ping/pong functionality."""
    from esportez_ws.server import TournamentWebSocketServer

    server = TournamentWebSocketServer(host="localhost", port=8767)

    async with websockets.serve(server.handler, "localhost", 8767):
        async with websockets.connect("ws://localhost:8767") as ws:
            # Receive connection message
            await ws.recv()

            # Send ping
            await ws.send(json.dumps({"type": "ping"}))
            response = await ws.recv()
            data = json.loads(response)
            assert data["type"] == "pong"
            assert "timestamp" in data


@pytest.mark.asyncio
async def test_websocket_tournament_subscription():
    """Test tournament subscription."""
    from esportez_ws.server import TournamentWebSocketServer

    server = TournamentWebSocketServer(host="localhost", port=8768)

    async with websockets.serve(server.handler, "localhost", 8768):
        async with websockets.connect("ws://localhost:8768") as ws:
            # Receive connection message
            await ws.recv()

            # Subscribe to tournament
            await ws.send(json.dumps({
                "type": "subscribe",
                "tournament_id": "test-tournament-123"
            }))
            response = await ws.recv()
            data = json.loads(response)
            assert data["type"] == "subscribed"
            assert data["tournament_id"] == "test-tournament-123"


@pytest.mark.asyncio
async def test_websocket_tournament_path_subscription():
    """Test tournament subscription via path."""
    from esportez_ws.server import TournamentWebSocketServer

    server = TournamentWebSocketServer(host="localhost", port=8769)

    async with websockets.serve(server.handler, "localhost", 8769):
        # Connect with tournament ID in path
        async with websockets.connect("ws://localhost:8769/tournament/tourney-456") as ws:
            response = await ws.recv()
            data = json.loads(response)
            assert data["type"] == "connected"
            assert data["tournament_id"] == "tourney-456"


@pytest.mark.asyncio
async def test_websocket_broadcast_to_tournament():
    """Test broadcasting to tournament subscribers."""
    from esportez_ws.server import TournamentWebSocketServer

    server = TournamentWebSocketServer(host="localhost", port=8770)

    async with websockets.serve(server.handler, "localhost", 8770):
        # Connect two clients to same tournament
        async with websockets.connect("ws://localhost:8770/tournament/tourney-789") as ws1:
            await ws1.recv()  # connected message

            async with websockets.connect("ws://localhost:8770/tournament/tourney-789") as ws2:
                await ws2.recv()  # connected message

                # Broadcast to tournament
                await server.broadcast_to_tournament("tourney-789", {
                    "type": "test_message",
                    "data": "Hello!"
                })

                # Both clients should receive
                response1 = await asyncio.wait_for(ws1.recv(), timeout=1.0)
                response2 = await asyncio.wait_for(ws2.recv(), timeout=1.0)

                data1 = json.loads(response1)
                data2 = json.loads(response2)

                assert data1["type"] == "test_message"
                assert data2["type"] == "test_message"
                assert data1["data"] == "Hello!"
