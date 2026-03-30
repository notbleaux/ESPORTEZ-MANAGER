"""Tournament schemas."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TournamentStatus(str, Enum):
    """Tournament status enum."""
    DRAFT = "draft"
    REGISTRATION = "registration"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MatchStatus(str, Enum):
    """Match status enum."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TournamentBase(BaseModel):
    """Base tournament schema."""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    game: str = Field(..., pattern="^(valorant|cs2|lol|dota2)$")
    format: str = Field(default="single_elimination")
    start_date: datetime
    end_date: datetime
    max_teams: int = Field(default=32, ge=2, le=128)
    prize_pool: Optional[float] = Field(None, ge=0)


class TournamentCreate(TournamentBase):
    """Tournament creation schema."""
    pass


class TournamentUpdate(BaseModel):
    """Tournament update schema."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[TournamentStatus] = None
    max_teams: Optional[int] = Field(None, ge=2, le=128)
    prize_pool: Optional[float] = None


class Tournament(TournamentBase):
    """Full tournament schema."""
    id: str
    status: TournamentStatus
    created_at: datetime
    updated_at: datetime
    registered_teams: int = 0
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class Match(BaseModel):
    """Match schema for tournament bracket."""
    id: str
    round: int
    position: int
    team1_id: Optional[str] = None
    team2_id: Optional[str] = None
    winner_id: Optional[str] = None
    score1: Optional[int] = None
    score2: Optional[int] = None
    scheduled_time: Optional[datetime] = None
    status: str = "pending"  # pending, active, completed

    class Config:
        from_attributes = True


class Bracket(BaseModel):
    """Tournament bracket schema."""
    tournament_id: str
    format: str
    rounds: int
    matches: List[Match]
    current_round: int = 0

    class Config:
        from_attributes = True


# Team schemas
class TeamBase(BaseModel):
    """Base team schema."""
    name: str = Field(..., min_length=2, max_length=50)
    tag: Optional[str] = Field(None, max_length=5)
    logo_url: Optional[str] = None
    region: Optional[str] = None


class TeamCreate(TeamBase):
    """Team creation schema."""
    player_ids: List[str] = []


class Team(TeamBase):
    """Full team schema."""
    id: str
    created_at: datetime
    player_count: int = 0
    tournament_wins: int = 0

    class Config:
        from_attributes = True


class TeamRegistration(BaseModel):
    """Team registration schema."""
    team_id: str
    tournament_id: str
    registered_at: datetime

    class Config:
        from_attributes = True
