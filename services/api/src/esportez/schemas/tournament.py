"""Tournament schemas."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class TournamentStatus(str, Enum):
    """Tournament status enum."""
    DRAFT = "draft"
    REGISTRATION = "registration"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TournamentBase(BaseModel):
    """Base tournament schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    game: str = Field(..., min_length=1, max_length=50)  # "valorant", "cs2", etc.
    start_date: datetime
    end_date: datetime
    max_teams: int = Field(default=32, ge=2, le=128)
    prize_pool: Optional[float] = Field(None, ge=0)


class TournamentCreate(TournamentBase):
    """Tournament creation schema."""
    pass


class Tournament(TournamentBase):
    """Full tournament schema."""
    id: str
    status: TournamentStatus
    created_at: datetime
    updated_at: datetime
    registered_teams: int = 0
    
    class Config:
        from_attributes = True
