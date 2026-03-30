"""Tournament endpoint tests."""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient, ASGITransport
from esportez.main import app


@pytest.mark.asyncio
async def test_list_tournaments():
    """Test listing tournaments."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/tournaments/")
    assert response.status_code == 200
    # Returns list (may or may not be empty depending on test order)
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_tournament():
    """Test creating a tournament."""
    tournament_data = {
        "name": "Test Tournament",
        "description": "A test tournament",
        "game": "valorant",
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "max_teams": 16,
        "prize_pool": 10000.0
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tournaments/", json=tournament_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == tournament_data["name"]
    assert data["game"] == tournament_data["game"]
    assert data["status"] == "draft"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["registered_teams"] == 0


@pytest.mark.asyncio
async def test_get_tournament():
    """Test getting a tournament by ID."""
    # First create a tournament
    tournament_data = {
        "name": "Get Test Tournament",
        "game": "cs2",
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_response = await ac.post("/tournaments/", json=tournament_data)
        tournament_id = create_response.json()["id"]

        # Now get it
        get_response = await ac.get(f"/tournaments/{tournament_id}")

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == tournament_id
    assert data["name"] == tournament_data["name"]


@pytest.mark.asyncio
async def test_get_tournament_not_found():
    """Test getting a non-existent tournament."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/tournaments/non-existent-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Tournament not found"


@pytest.mark.asyncio
async def test_update_tournament():
    """Test updating a tournament."""
    # First create a tournament
    tournament_data = {
        "name": "Update Test Tournament",
        "game": "valorant",
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_response = await ac.post("/tournaments/", json=tournament_data)
        tournament_id = create_response.json()["id"]

        # Update it
        update_data = {"name": "Updated Tournament Name"}
        update_response = await ac.put(f"/tournaments/{tournament_id}", json=update_data)

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Tournament Name"
    assert data["game"] == tournament_data["game"]  # Unchanged


@pytest.mark.asyncio
async def test_delete_tournament():
    """Test deleting a tournament."""
    # First create a tournament
    tournament_data = {
        "name": "Delete Test Tournament",
        "game": "dota2",
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_response = await ac.post("/tournaments/", json=tournament_data)
        tournament_id = create_response.json()["id"]

        # Delete it
        delete_response = await ac.delete(f"/tournaments/{tournament_id}")
        assert delete_response.status_code == 204

        # Verify it's gone
        get_response = await ac.get(f"/tournaments/{tournament_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_open_registration():
    """Test opening tournament registration."""
    tournament_data = {
        "name": "Registration Test",
        "game": "lol",
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_response = await ac.post("/tournaments/", json=tournament_data)
        tournament_id = create_response.json()["id"]

        # Open registration
        response = await ac.post(f"/tournaments/{tournament_id}/register")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "registration"


@pytest.mark.asyncio
async def test_start_tournament():
    """Test starting a tournament."""
    tournament_data = {
        "name": "Start Test Tournament",
        "game": "valorant",
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create tournament
        create_response = await ac.post("/tournaments/", json=tournament_data)
        tournament_id = create_response.json()["id"]

        # Open registration first
        await ac.post(f"/tournaments/{tournament_id}/register")

        # Start tournament
        response = await ac.post(f"/tournaments/{tournament_id}/start")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_start_tournament_wrong_status():
    """Test starting a tournament in wrong status."""
    tournament_data = {
        "name": "Wrong Status Test",
        "game": "valorant",
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_response = await ac.post("/tournaments/", json=tournament_data)
        tournament_id = create_response.json()["id"]

        # Try to start without opening registration first
        response = await ac.post(f"/tournaments/{tournament_id}/start")

    assert response.status_code == 400
    assert "Cannot start" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_bracket():
    """Test getting tournament bracket."""
    tournament_data = {
        "name": "Bracket Test",
        "game": "cs2",
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "max_teams": 8
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create tournament
        create_response = await ac.post("/tournaments/", json=tournament_data)
        tournament_id = create_response.json()["id"]

        # Open registration and start to create bracket
        await ac.post(f"/tournaments/{tournament_id}/register")
        await ac.post(f"/tournaments/{tournament_id}/start")

        # Get bracket
        response = await ac.get(f"/tournaments/{tournament_id}/bracket")

    assert response.status_code == 200
    data = response.json()
    assert data["tournament_id"] == tournament_id
    assert data["format"] == "single_elimination"
    assert "rounds" in data
    assert "matches" in data
    assert len(data["matches"]) > 0


@pytest.mark.asyncio
async def test_get_bracket_not_found():
    """Test getting bracket for tournament without one."""
    tournament_data = {
        "name": "No Bracket Test",
        "game": "valorant",
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_response = await ac.post("/tournaments/", json=tournament_data)
        tournament_id = create_response.json()["id"]

        # Try to get bracket before tournament starts
        response = await ac.get(f"/tournaments/{tournament_id}/bracket")

    assert response.status_code == 404
    assert "Bracket not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_filter_tournaments_by_status():
    """Test filtering tournaments by status."""
    tournament_data = {
        "name": "Filter Test",
        "game": "valorant",
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create tournament
        await ac.post("/tournaments/", json=tournament_data)

        # Filter by draft status
        response = await ac.get("/tournaments/?status=draft")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    for t in data:
        assert t["status"] == "draft"


@pytest.mark.asyncio
async def test_filter_tournaments_by_game():
    """Test filtering tournaments by game."""
    tournament_data = {
        "name": "Game Filter Test",
        "game": "cs2",
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create tournament
        await ac.post("/tournaments/", json=tournament_data)

        # Filter by game
        response = await ac.get("/tournaments/?game=cs2")

    assert response.status_code == 200
    data = response.json()
    for t in data:
        assert t["game"] == "cs2"


@pytest.mark.asyncio
async def test_invalid_game():
    """Test creating tournament with invalid game."""
    tournament_data = {
        "name": "Invalid Game Test",
        "game": "invalid_game",
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tournaments/", json=tournament_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_invalid_tournament_name():
    """Test creating tournament with invalid name (too short)."""
    tournament_data = {
        "name": "ab",  # Too short
        "game": "valorant",
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tournaments/", json=tournament_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_pagination():
    """Test tournament listing pagination."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Get first page
        response = await ac.get("/tournaments/?limit=5&offset=0")

    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5
