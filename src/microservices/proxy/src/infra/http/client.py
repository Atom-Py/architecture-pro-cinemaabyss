import httpx

from config.settings import settings


class UpstreamClient:
    """Shared httpx client for calls to the monolith and the microservices.

    One client per process keeps connections alive between requests.
    """

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                settings.UPSTREAM_TIMEOUT_SECONDS,
                connect=settings.UPSTREAM_CONNECT_TIMEOUT_SECONDS,
            ),
            limits=httpx.Limits(max_connections=200, max_keepalive_connections=50),
            follow_redirects=False,
        )

    async def stop(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def request(
        self,
        method: str,
        url: str,
        params: dict,
        headers: dict,
        content: bytes,
    ) -> httpx.Response:
        if self._client is None:
            raise RuntimeError("upstream client is not started")
        return await self._client.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            content=content,
        )


client = UpstreamClient()
