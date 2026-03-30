"""Tournament router for CRUD operations."""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Optional
from datetime import datetime
import uuid
import math

from ..schemas.tournament import (
    Tournament, TournamentCreate, TournamentUpdate,
    TournamentStatus, Bracket, Match
)
from ..services.websocket_notifier import ws_notifier

router = APIRouter(prefix="/tournaments", tags=["tournaments"])

# In-memory storage (replace with database in production)
tournaments_db: dict[str, Tournament] = {}
brackets_db: dict[str, Bracket] = {}
matches_db: dict[str, Match] = {}


@router.get("/", response_model=List[Tournament])
async def list_tournaments(
    status: Optional[TournamentStatus] = None,
    game: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List tournaments with optional filtering."""
    tournaments = list(tournaments_db.values())
    
    if status:
        tournaments = [t for t in tournaments if t.status == status]
    if game:
        tournaments = [t for t in tournaments if t.game == game]
    
    return tournaments[offset:offset + limit]


@router.post("/", response_model=Tournament, status_code=201)
async def create_tournament(
    tournament: TournamentCreate,
    background_tasks: BackgroundTasks
):
    """Create new tournament."""
    new_tournament = Tournament(
        id=str(uuid.uuid4()),
        status=TournamentStatus.DRAFT,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        registered_teams=0,
        **tournament.model_dump()
    )
    
    tournaments_db[new_tournament.id] = new_tournament
    
    # Notify via WebSocket
    background_tasks.add_task(
        ws_notifier.notify_tournament_created,
        new_tournament.id,
        new_tournament.name
    )
    
    return new_tournament


@router.get("/{tournament_id}", response_model=Tournament)
async def get_tournament(tournament_id: str):
    """Get tournament by ID."""
    if tournament_id not in tournaments_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournaments_db[tournament_id]


@router.put("/{tournament_id}", response_model=Tournament)
async def update_tournament(
    tournament_id: str,
    update: TournamentUpdate,
    background_tasks: BackgroundTasks
):
    """Update tournament."""
    if tournament_id not in tournaments_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    tournament = tournaments_db[tournament_id]
    
    # Update fields
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(tournament, field, value)
    
    tournament.updated_at = datetime.utcnow()
    
    # Notify
    background_tasks.add_task(
        ws_notifier.notify_tournament_update,
        tournament_id,
        "tournament_updated",
        {"fields_updated": list(update.model_dump(exclude_unset=True).keys())}
    )
    
    return tournament


@router.delete("/{tournament_id}", status_code=204)
async def delete_tournament(tournament_id: str):
    """Delete tournament."""
    if tournament_id not in tournaments_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    del tournaments_db[tournament_id]
    # Clean up associated data
    if tournament_id in brackets_db:
        del brackets_db[tournament_id]
    return None


@router.post("/{tournament_id}/start", response_model=Tournament)
async def start_tournament(
    tournament_id: str,
    background_tasks: BackgroundTasks
):
    """Start tournament (change status to ACTIVE)."""
    if tournament_id not in tournaments_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    tournament = tournaments_db[tournament_id]
    
    if tournament.status != TournamentStatus.REGISTRATION:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start tournament in {tournament.status} status"
        )
    
    tournament.status = TournamentStatus.ACTIVE
    tournament.updated_at = datetime.utcnow()
    
    # Create bracket
    bracket = create_bracket(tournament)
    brackets_db[tournament_id] = bracket
    
    # Notify
    background_tasks.add_task(
        ws_notifier.notify_tournament_started,
        tournament_id,
        bracket.model_dump()
    )
    
    return tournament


@router.post("/{tournament_id}/register", response_model=Tournament)
async def open_registration(tournament_id: str):
    """Open tournament registration."""
    if tournament_id not in tournaments_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    tournament = tournaments_db[tournament_id]
    
    if tournament.status != TournamentStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot open registration from {tournament.status} status"
        )
    
    tournament.status = TournamentStatus.REGISTRATION
    tournament.updated_at = datetime.utcnow()
    
    return tournament


@router.get("/{tournament_id}/bracket", response_model=Bracket)
async def get_bracket(tournament_id: str):
    """Get tournament bracket."""
    if tournament_id not in brackets_db:
        raise HTTPException(status_code=404, detail="Bracket not found")
    return brackets_db[tournament_id]


def create_bracket(tournament: Tournament) -> Bracket:
    """Generate tournament bracket."""
    # Simple single-elimination bracket generation
    num_teams = max(tournament.registered_teams, 2)
    
    # Calculate rounds needed
    rounds = math.ceil(math.log2(num_teams))
    
    matches = []
    match_id = 0
    
    for round_num in range(rounds):
        round_matches = 2 ** (rounds - round_num - 1)
        for i in range(round_matches):
            matches.append(Match(
                id=f"m{match_id}",
                round=round_num,
                position=i,
                team1_id=None,
                team2_id=None,
                winner_id=None
            ))
            match_id += 1
    
    return Bracket(
        tournament_id=tournament.id,
        format="single_elimination",
        rounds=rounds,
        matches=matches
    )
