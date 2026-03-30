"""FastAPI entry point for ESPORTEZ-MANAGER API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import tournaments, teams, matches

app = FastAPI(
    title="ESPORTEZ-MANAGER API",
    description="Tournament management system for esports",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tournaments.router)
app.include_router(teams.router)
app.include_router(matches.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "esportez-manager"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ESPORTEZ-MANAGER API",
        "version": "0.1.0",
        "docs": "/docs",
    }
