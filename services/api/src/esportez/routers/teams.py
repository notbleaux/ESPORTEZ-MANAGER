"""Team router for CRUD operations."""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
import uuid

from ..schemas.tournament import Team, TeamCreate, TournamentStatus

router = APIRouter(prefix="/teams", tags=["teams"])

# In-memory storage
teams_db: dict[str, Team] = {}
registrations_db: dict[str, list] = {}  # tournament_id -> list of team_ids


@router.get("/", response_model=List[Team])
async def list_teams(
    region: Optional[str] = None,
    limit: int = 50
):
    """List teams."""
    teams = list(teams_db.values())
    if region:
        teams = [t for t in teams if t.region == region]
    return teams[:limit]


@router.post("/", response_model=Team, status_code=201)
async def create_team(team: TeamCreate):
    """Create new team."""
    new_team = Team(
        id=str(uuid.uuid4()),
        created_at=datetime.utcnow(),
        player_count=len(team.player_ids),
        **team.model_dump()
    )
    teams_db[new_team.id] = new_team
    return new_team


@router.get("/{team_id}", response_model=Team)
async def get_team(team_id: str):
    """Get team by ID."""
    if team_id not in teams_db:
        raise HTTPException(status_code=404, detail="Team not found")
    return teams_db[team_id]


@router.put("/{team_id}", response_model=Team)
async def update_team(team_id: str, team_update: TeamCreate):
    """Update a team."""
    if team_id not in teams_db:
        raise HTTPException(status_code=404, detail="Team not found")
    
    existing = teams_db[team_id]
    updated_data = team_update.model_dump()
    
    updated_team = Team(
        id=existing.id,
        created_at=existing.created_at,
        player_count=len(team_update.player_ids),
        tournament_wins=existing.tournament_wins,
        **updated_data
    )
    teams_db[team_id] = updated_team
    return updated_team


@router.delete("/{team_id}", status_code=204)
async def delete_team(team_id: str):
    """Delete a team."""
    if team_id not in teams_db:
        raise HTTPException(status_code=404, detail="Team not found")
    del teams_db[team_id]
    return None


@router.post("/{team_id}/register/{tournament_id}")
async def register_for_tournament(team_id: str, tournament_id: str):
    """Register team for tournament."""
    # Import here to avoid circular imports
    from .tournaments import tournaments_db
    
    # Check team exists
    if team_id not in teams_db:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check tournament exists and is in registration
    if tournament_id not in tournaments_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    tournament = tournaments_db[tournament_id]
    if tournament.status != TournamentStatus.REGISTRATION:
        raise HTTPException(
            status_code=400,
            detail="Tournament is not open for registration"
        )
    
    # Check if already registered
    if tournament_id in registrations_db and team_id in registrations_db[tournament_id]:
        raise HTTPException(
            status_code=400,
            detail="Team is already registered for this tournament"
        )
    
    # Check max teams limit
    if tournament.registered_teams >= tournament.max_teams:
        raise HTTPException(
            status_code=400,
            detail="Tournament has reached maximum number of teams"
        )
    
    # Register team
    if tournament_id not in registrations_db:
        registrations_db[tournament_id] = []
    registrations_db[tournament_id].append(team_id)
    
    # Increment registered teams
    tournament.registered_teams += 1
    tournament.updated_at = datetime.utcnow()
    
    return {
        "message": "Team registered successfully",
        "team_id": team_id,
        "tournament_id": tournament_id,
        "registered_at": datetime.utcnow().isoformat()
    }


@router.post("/{team_id}/unregister/{tournament_id}")
async def unregister_from_tournament(team_id: str, tournament_id: str):
    """Unregister team from tournament."""
    from .tournaments import tournaments_db
    
    # Check team exists
    if team_id not in teams_db:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check tournament exists
    if tournament_id not in tournaments_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    tournament = tournaments_db[tournament_id]
    if tournament.status != TournamentStatus.REGISTRATION:
        raise HTTPException(
            status_code=400,
            detail="Cannot unregister from tournament that is not in registration phase"
        )
    
    # Check if registered
    if tournament_id not in registrations_db or team_id not in registrations_db[tournament_id]:
        raise HTTPException(
            status_code=400,
            detail="Team is not registered for this tournament"
        )
    
    # Unregister team
    registrations_db[tournament_id].remove(team_id)
    
    # Decrement registered teams
    tournament.registered_teams = max(0, tournament.registered_teams - 1)
    tournament.updated_at = datetime.utcnow()
    
    return {
        "message": "Team unregistered successfully",
        "team_id": team_id,
        "tournament_id": tournament_id
    }
