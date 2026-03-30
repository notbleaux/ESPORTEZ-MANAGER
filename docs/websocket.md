# ESPORTEZ-MANAGER WebSocket Documentation

## Overview

Real-time WebSocket server for tournament updates.

## Connection

```
ws://localhost:8765
```

## Message Types

### Client → Server

#### subscribe_tournament
Subscribe to tournament updates.
```json
{
  "type": "subscribe_tournament",
  "tournament_id": "uuid"
}
```

#### unsubscribe_tournament
Unsubscribe from tournament updates.
```json
{
  "type": "unsubscribe_tournament",
  "tournament_id": "uuid"
}
```

#### ping
Keepalive ping.
```json
{
  "type": "ping"
}
```

### Server → Client

#### connected
Connection established.
```json
{
  "type": "connected",
  "timestamp": "2024-01-01T00:00:00Z",
  "service": "esportez-websocket"
}
```

#### subscribed
Subscription confirmed.
```json
{
  "type": "subscribed",
  "tournament_id": "uuid"
}
```

#### pong
Ping response.
```json
{
  "type": "pong",
  "timestamp": "2024-01-01T00:00:00Z"
}
```
