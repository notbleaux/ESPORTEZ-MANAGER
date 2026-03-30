"""Shared tournament schemas."""

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


class TournamentFormat(str, Enum):
    """Tournament format enum."""
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    ROUND_ROBIN = "round_robin"
    SWISS = "swiss"


class TournamentBase(BaseModel):
    """Base tournament schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    game: str = Field(..., min_length=1, max_length=50)
    format: TournamentFormat = TournamentFormat.SINGLE_ELIMINATION
    start_date: datetime
    end_date: datetime
    max_teams: int = Field(default=32, ge=2, le=128)
    prize_pool: Optional[float] = Field(None, ge=0)


class TournamentCreate(TournamentBase):
    """Tournament creation schema."""
    pass


class TournamentUpdate(BaseModel):
    """Tournament update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_teams: Optional[int] = Field(None, ge=2, le=128)
    prize_pool: Optional[float] = Field(None, ge=0)


class Tournament(TournamentBase):
    """Full tournament schema."""
    id: str
    status: TournamentStatus
    created_at: datetime
    updated_at: datetime
    registered_teams: int = 0
    organizer_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class Team(BaseModel):
    """Team schema."""
    id: str
    name: str
    tag: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime


class MatchStatus(str, Enum):
    """Match status enum."""
    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Match(BaseModel):
    """Match schema."""
    id: str
    tournament_id: str
    team1_id: str
    team2_id: str
    status: MatchStatus
    scheduled_at: datetime
    score1: Optional[int] = None
    score2: Optional[int] = None
    created_at: datetime
