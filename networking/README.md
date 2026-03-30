# ESPORTEZ-MANAGER Networking

Networking layer for API and WebSocket clients.

## Usage

```python
from esportez_net.client import EsportezClient

client = EsportezClient("http://localhost:8000")
tournaments = await client.list_tournaments()
```
