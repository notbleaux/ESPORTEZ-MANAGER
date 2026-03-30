# ESPORTEZ-MANAGER

A comprehensive eSports platform combining **Godot Engine simulation** with **Python API services** for tournament management.

## Overview

ESPORTEZ-MANAGER is a full-stack eSports platform supporting:
- **Godot Simulation Client** - Tactical FPS simulation with NJZ UI
- **API Services** - FastAPI backend for tournament management
- **WebSocket Server** - Real-time updates and live match tracking

## Project Structure

```
ESPORTEZ-MANAGER/
├── project.godot          # Godot project file
├── scenes/                # Godot scene files (.tscn)
├── scripts/               # GDScript files
├── entities/              # Game entities and data models
├── maps/                  # Map/level data
├── Defs/                  # Definition files and constants
├── addons/                # Godot addons and plugins
├── tests/                 # Test files for Godot components
├── sim-core/              # C# Simulation Core
│   ├── SimCore/           # Core simulation engine
│   ├── ConsoleRunner/     # Console-based test runner
│   └── SimConsoleRunner/  # Simulation console interface
├── radiantx-game/         # Godot client application
│   ├── src/               # Source code
│   └── tests/             # Client tests
├── services/              # Python API services
│   ├── api/               # FastAPI application
│   └── websocket/         # WebSocket server
├── networking/            # API client and connection pooling
├── schemas/               # Shared Pydantic schemas
└── docs/                  # Documentation
```

## Components

### Godot Simulation (sim-core/)
The C# based simulation engine handling:
- Tactical FPS simulation (95% accuracy with VAL/CS2)
- Tournament logic and bracket management
- Team and player statistics
- Match simulation with deterministic RNG
- NJZ UI with 5-archetype visuals

### Godot Client (radiantx-game/)
The Godot client application:
- User interface for team management
- Tournament visualization
- Live match tracking
- 3D holographic replay viewer
- Administrative tools

### API Services (services/)
Python FastAPI backend:
- Tournament CRUD operations
- Team management
- Match scheduling
- Real-time updates via WebSocket
- Connection pooling
- Shared schemas

## Getting Started

### Godot Client

1. Open `project.godot` in Godot Engine 4.x
2. Ensure .NET build tools are installed for C# support
3. Build the solution to compile sim-core

### API Services

**Prerequisites:**
- Python 3.11+
- Poetry

**Setup:**
```bash
# Setup API service
cd services/api
poetry install
poetry run uvicorn esportez.main:app --reload --port 8000

# In another terminal, setup WebSocket service
cd services/websocket
poetry install
poetry run python -m esportez_ws.server
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## WebSocket Protocol

Connect to `ws://localhost:8765` for real-time tournament updates.

See [docs/websocket.md](docs/websocket.md) for protocol details.

## Development

### Godot
```bash
# Run tests
cd tests/
./run_tests.sh
```

### Python
```bash
# Install development dependencies
poetry install --with dev

# Run tests
pytest

# Format code
black src/
ruff check src/
```

## Services

| Service | Description | Port |
|---------|-------------|------|
| Godot Client | Game simulation UI | N/A |
| API | FastAPI REST API | 8000 |
| WebSocket | Real-time updates | 8765 |

## License

See [LICENSE](LICENSE) file.
