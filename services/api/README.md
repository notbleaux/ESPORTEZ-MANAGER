# ESPORTEZ-MANAGER API

FastAPI backend for tournament management.

## Setup

```bash
# Install dependencies
poetry install

# Run development server
poetry run uvicorn esportez.main:app --reload --port 8000
```

## Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `GET /docs` - Swagger UI
- `GET /tournaments` - List tournaments
- `POST /tournaments` - Create tournament
- `GET /tournaments/{id}` - Get tournament
- `PUT /tournaments/{id}` - Update tournament
- `DELETE /tournaments/{id}` - Delete tournament
