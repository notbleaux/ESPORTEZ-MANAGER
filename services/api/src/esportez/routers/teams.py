"""Team router for CRUD operations."""

from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import uuid

router = APIRouter(prefix="/teams", tags=["teams"])

# In-memory storage for now
teams_db: dict = {}


@router.get("/")
async def list_teams():
    """List all teams."""
    return list(teams_db.values())


@router.post("/")
async def create_team(team: dict):
    """Create a new team."""
    team_id = str(uuid.uuid4())
    team["id"] = team_id
    team["created_at"] = datetime.utcnow().isoformat()
    teams_db[team_id] = team
    return team


@router.get("/{team_id}")
async def get_team(team_id: str):
    """Get a team by ID."""
    if team_id not in teams_db:
        raise HTTPException(status_code=404, detail="Team not found")
    return teams_db[team_id]
