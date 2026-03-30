"""Connection pooling for ESPORTEZ API."""

import httpx
from typing import Optional
from contextlib import asynccontextmanager


class ConnectionPool:
    """HTTP connection pool manager."""
    
    def __init__(
        self,
        base_url: str,
        max_connections: int = 100,
        max_keepalive: int = 20,
        timeout: float = 30.0
    ):
        self.base_url = base_url
        self.limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive
        )
        self.timeout = httpx.Timeout(timeout)
        self._client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self) -> None:
        """Initialize the connection pool."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            limits=self.limits,
            timeout=self.timeout
        )
    
    async def close(self) -> None:
        """Close the connection pool."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    @asynccontextmanager
    async def get_client(self):
        """Get client from pool."""
        if not self._client:
            await self.initialize()
        yield self._client
    
    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make a request using the pool."""
        async with self.get_client() as client:
            return await client.request(method, url, **kwargs)
