"""Tournament router for CRUD operations."""

from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import uuid

from ..schemas.tournament import Tournament, TournamentCreate, TournamentStatus

router = APIRouter(prefix="/tournaments", tags=["tournaments"])

# In-memory storage for now
tournaments_db: dict[str, Tournament] = {}


@router.get("/", response_model=List[Tournament])
async def list_tournaments():
    """List all tournaments."""
    return list(tournaments_db.values())


@router.post("/", response_model=Tournament)
async def create_tournament(tournament: TournamentCreate):
    """Create a new tournament."""
    new_tournament = Tournament(
        id=str(uuid.uuid4()),
        status=TournamentStatus.DRAFT,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        registered_teams=0,
        **tournament.model_dump()
    )
    tournaments_db[new_tournament.id] = new_tournament
    return new_tournament


@router.get("/{tournament_id}", response_model=Tournament)
async def get_tournament(tournament_id: str):
    """Get a tournament by ID."""
    if tournament_id not in tournaments_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournaments_db[tournament_id]


@router.put("/{tournament_id}", response_model=Tournament)
async def update_tournament(tournament_id: str, tournament_update: TournamentCreate):
    """Update a tournament."""
    if tournament_id not in tournaments_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    existing = tournaments_db[tournament_id]
    updated_data = tournament_update.model_dump()
    
    updated_tournament = Tournament(
        id=existing.id,
        status=existing.status,
        created_at=existing.created_at,
        updated_at=datetime.utcnow(),
        registered_teams=existing.registered_teams,
        **updated_data
    )
    tournaments_db[tournament_id] = updated_tournament
    return updated_tournament


@router.delete("/{tournament_id}")
async def delete_tournament(tournament_id: str):
    """Delete a tournament."""
    if tournament_id not in tournaments_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    del tournaments_db[tournament_id]
    return {"message": "Tournament deleted successfully"}


@router.patch("/{tournament_id}/status", response_model=Tournament)
async def update_tournament_status(tournament_id: str, status: TournamentStatus):
    """Update tournament status."""
    if tournament_id not in tournaments_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    tournaments_db[tournament_id].status = status
    tournaments_db[tournament_id].updated_at = datetime.utcnow()
    return tournaments_db[tournament_id]
