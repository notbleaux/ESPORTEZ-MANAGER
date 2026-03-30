# ESPORTEZ-MANAGER API Documentation

## Overview

RESTful API for tournament management.

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "esportez-manager"
}
```

### Tournaments

#### GET /tournaments
List all tournaments.

#### POST /tournaments
Create a new tournament.

**Request Body:**
```json
{
  "name": "VCT 2024",
  "description": "Valorant Championship Tournament",
  "game": "valorant",
  "start_date": "2024-06-01T00:00:00Z",
  "end_date": "2024-08-01T00:00:00Z",
  "max_teams": 16,
  "prize_pool": 1000000
}
```

#### GET /tournaments/{id}
Get tournament by ID.

#### PUT /tournaments/{id}
Update tournament.

#### DELETE /tournaments/{id}
Delete tournament.

#### PATCH /tournaments/{id}/status
Update tournament status.
