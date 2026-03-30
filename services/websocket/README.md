# ESPORTEZ-MANAGER WebSocket Server

Real-time WebSocket server for tournament updates.

## Setup

```bash
# Install dependencies
poetry install

# Run server
poetry run python -m esportez_ws.server
```

## Protocol

### Connection
- Connect to `ws://localhost:8765`
- Server sends `{"type": "connected"}`

### Messages

#### Subscribe to tournament
```json
{"type": "subscribe_tournament", "tournament_id": "uuid"}
```

#### Unsubscribe
```json
{"type": "unsubscribe_tournament", "tournament_id": "uuid"}
```

#### Ping
```json
{"type": "ping"}
```
