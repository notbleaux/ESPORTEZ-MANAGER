"""Match router for CRUD operations."""

from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import uuid

router = APIRouter(prefix="/matches", tags=["matches"])

# In-memory storage for now
matches_db: dict = {}


@router.get("/")
async def list_matches():
    """List all matches."""
    return list(matches_db.values())


@router.post("/")
async def create_match(match: dict):
    """Create a new match."""
    match_id = str(uuid.uuid4())
    match["id"] = match_id
    match["created_at"] = datetime.utcnow().isoformat()
    matches_db[match_id] = match
    return match


@router.get("/{match_id}")
async def get_match(match_id: str):
    """Get a match by ID."""
    if match_id not in matches_db:
        raise HTTPException(status_code=404, detail="Match not found")
    return matches_db[match_id]
