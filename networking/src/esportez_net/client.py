"""API client for ESPORTEZ-MANAGER."""

import httpx
from typing import Optional, Dict, Any
from urllib.parse import urljoin


class EsportezClient:
    """HTTP client for ESPORTEZ API."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._default_headers()
        )
    
    def _default_headers(self) -> Dict[str, str]:
        """Get default headers."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def close(self) -> None:
        """Close the client."""
        await self.client.aclose()
    
    async def get(self, path: str, **kwargs) -> httpx.Response:
        """GET request."""
        return await self.client.get(path, **kwargs)
    
    async def post(self, path: str, **kwargs) -> httpx.Response:
        """POST request."""
        return await self.client.post(path, **kwargs)
    
    async def put(self, path: str, **kwargs) -> httpx.Response:
        """PUT request."""
        return await self.client.put(path, **kwargs)
    
    async def delete(self, path: str, **kwargs) -> httpx.Response:
        """DELETE request."""
        return await self.client.delete(path, **kwargs)
    
    # Tournament endpoints
    async def list_tournaments(self) -> Dict[str, Any]:
        """List all tournaments."""
        response = await self.get("/tournaments")
        response.raise_for_status()
        return response.json()
    
    async def get_tournament(self, tournament_id: str) -> Dict[str, Any]:
        """Get tournament by ID."""
        response = await self.get(f"/tournaments/{tournament_id}")
        response.raise_for_status()
        return response.json()
    
    async def create_tournament(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tournament."""
        response = await self.post("/tournaments", json=data)
        response.raise_for_status()
        return response.json()
