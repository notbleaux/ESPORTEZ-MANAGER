"""Tournament endpoint tests."""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from esportez.main import app


@pytest.mark.asyncio
async def test_list_tournaments_empty():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/tournaments")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_tournament():
    tournament_data = {
        "name": "Test Tournament",
        "description": "A test tournament",
        "game": "valorant",
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "max_teams": 16,
        "prize_pool": 10000
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/tournaments", json=tournament_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == tournament_data["name"]
    assert data["game"] == tournament_data["game"]
    assert "id" in data
