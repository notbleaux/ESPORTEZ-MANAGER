"""WebSocket server tests."""

import pytest
import asyncio
import websockets
import json


@pytest.mark.asyncio
async def test_websocket_connection():
    from esportez_ws.server import TournamentWebSocket
    
    server = TournamentWebSocket(host="localhost", port=8766)
    
    # Start server in background
    server_task = asyncio.create_task(
        websockets.serve(server.handler, "localhost", 8766)
    )
    await asyncio.sleep(0.1)  # Let server start
    
    try:
        async with websockets.connect("ws://localhost:8766") as ws:
            response = await ws.recv()
            data = json.loads(response)
            assert data["type"] == "connected"
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
