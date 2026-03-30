# ESPORTEZ-MANAGER

Tournament management system for esports.

## Overview

ESPORTEZ-MANAGER is a comprehensive tournament management platform for esports events, supporting games like Valorant, Counter-Strike 2, and more.

## Architecture

```
NJZETA-ESPORTS/
├── services/
│   ├── api/              # FastAPI application
│   └── websocket/        # WebSocket server
├── networking/           # API client and connection pooling
├── schemas/              # Shared Pydantic schemas
└── docs/                 # Documentation
```

## Quick Start

### Prerequisites

- Python 3.11+
- Poetry

### Setup

```bash
# Clone repository
git clone https://github.com/notbleaux/NJZETA-ESPORTS.git
cd NJZETA-ESPORTS

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

## Project Structure

### Services

| Service | Description | Port |
|---------|-------------|------|
| API | FastAPI REST API | 8000 |
| WebSocket | Real-time updates | 8765 |

### Features

- Tournament CRUD operations
- Team management
- Match scheduling
- Real-time updates via WebSocket
- Connection pooling
- Shared schemas

## Development

```bash
# Install development dependencies
poetry install --with dev

# Run tests
pytest

# Format code
black src/
ruff check src/
```

## License

See [LICENSE](LICENSE) file.
