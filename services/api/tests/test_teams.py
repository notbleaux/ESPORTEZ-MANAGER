"""Team endpoint tests."""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient, ASGITransport
from esportez.main import app


@pytest.mark.asyncio
async def test_list_teams_empty():
    """Test listing teams when none exist."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/teams/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_team():
    """Test creating a team."""
    team_data = {
        "name": "Test Team",
        "tag": "TT",
        "region": "NA",
        "player_ids": ["player1", "player2", "player3"]
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/teams/", json=team_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == team_data["name"]
    assert data["tag"] == team_data["tag"]
    assert data["region"] == team_data["region"]
    assert data["player_count"] == 3
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_team():
    """Test getting a team by ID."""
    team_data = {
        "name": "Get Test Team",
        "tag": "GT",
        "region": "EU"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_response = await ac.post("/teams/", json=team_data)
        team_id = create_response.json()["id"]

        get_response = await ac.get(f"/teams/{team_id}")

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == team_id
    assert data["name"] == team_data["name"]


@pytest.mark.asyncio
async def test_get_team_not_found():
    """Test getting a non-existent team."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/teams/non-existent-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Team not found"


@pytest.mark.asyncio
async def test_update_team():
    """Test updating a team."""
    team_data = {
        "name": "Update Test Team",
        "tag": "UT",
        "region": "ASIA"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_response = await ac.post("/teams/", json=team_data)
        team_id = create_response.json()["id"]

        update_data = {
            "name": "Updated Team Name",
            "tag": "UTN",
            "region": "ASIA",
            "player_ids": ["player1"]
        }
        update_response = await ac.put(f"/teams/{team_id}", json=update_data)

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Team Name"
    assert data["tag"] == "UTN"
    assert data["player_count"] == 1


@pytest.mark.asyncio
async def test_delete_team():
    """Test deleting a team."""
    team_data = {
        "name": "Delete Test Team",
        "tag": "DT"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_response = await ac.post("/teams/", json=team_data)
        team_id = create_response.json()["id"]

        delete_response = await ac.delete(f"/teams/{team_id}")
        assert delete_response.status_code == 204

        get_response = await ac.get(f"/teams/{team_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_filter_teams_by_region():
    """Test filtering teams by region."""
    team_data = {
        "name": "Region Filter Test",
        "tag": "RFT",
        "region": "EU"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post("/teams/", json=team_data)

        response = await ac.get("/teams/?region=EU")

    assert response.status_code == 200
    data = response.json()
    for team in data:
        assert team["region"] == "EU"


@pytest.mark.asyncio
async def test_register_team_for_tournament():
    """Test registering a team for a tournament."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create tournament
        tournament_data = {
            "name": "Registration Tournament",
            "game": "valorant",
            "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "max_teams": 16
        }
        tournament_response = await ac.post("/tournaments/", json=tournament_data)
        tournament_id = tournament_response.json()["id"]

        # Open registration
        await ac.post(f"/tournaments/{tournament_id}/register")

        # Create team
        team_data = {
            "name": "Tournament Team",
            "tag": "TT"
        }
        team_response = await ac.post("/teams/", json=team_data)
        team_id = team_response.json()["id"]

        # Register team
        response = await ac.post(f"/teams/{team_id}/register/{tournament_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Team registered successfully"
    assert data["team_id"] == team_id
    assert data["tournament_id"] == tournament_id


@pytest.mark.asyncio
async def test_register_team_tournament_not_found():
    """Test registering for non-existent tournament."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create team
        team_data = {"name": "Lonely Team", "tag": "LT"}
        team_response = await ac.post("/teams/", json=team_data)
        team_id = team_response.json()["id"]

        # Try to register for non-existent tournament
        response = await ac.post(f"/teams/{team_id}/register/non-existent-tournament")

    assert response.status_code == 404
    assert "Tournament not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_team_not_in_registration():
    """Test registering when tournament is not in registration."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create tournament (in draft status)
        tournament_data = {
            "name": "Draft Tournament",
            "game": "valorant",
            "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        }
        tournament_response = await ac.post("/tournaments/", json=tournament_data)
        tournament_id = tournament_response.json()["id"]

        # Create team
        team_data = {"name": "Eager Team", "tag": "ET"}
        team_response = await ac.post("/teams/", json=team_data)
        team_id = team_response.json()["id"]

        # Try to register (should fail - tournament in draft)
        response = await ac.post(f"/teams/{team_id}/register/{tournament_id}")

    assert response.status_code == 400
    assert "not open for registration" in response.json()["detail"]


@pytest.mark.asyncio
async def test_unregister_team_from_tournament():
    """Test unregistering a team from a tournament."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create tournament
        tournament_data = {
            "name": "Unregister Tournament",
            "game": "cs2",
            "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        }
        tournament_response = await ac.post("/tournaments/", json=tournament_data)
        tournament_id = tournament_response.json()["id"]

        # Open registration
        await ac.post(f"/tournaments/{tournament_id}/register")

        # Create team
        team_data = {"name": "Leaving Team", "tag": "LT"}
        team_response = await ac.post("/teams/", json=team_data)
        team_id = team_response.json()["id"]

        # Register team
        await ac.post(f"/teams/{team_id}/register/{tournament_id}")

        # Unregister team
        response = await ac.post(f"/teams/{team_id}/unregister/{tournament_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Team unregistered successfully"
