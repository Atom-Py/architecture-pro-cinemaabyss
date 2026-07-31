import logging

import httpx
from robyn import Headers, Request, Response, SubRouter

from infra.http.client import client
from models.schemas.errors import ErrorResponse
from services import strangler

logger = logging.getLogger(__name__)

proxy_router = SubRouter(prefix="/api")

_JSON = {"Content-Type": "application/json"}

# Hop-by-hop headers describe a single connection and must not be forwarded,
# see RFC 9110. Content-Length is recalculated by httpx and by Robyn.
_SKIP_REQUEST_HEADERS = frozenset(
    {"host", "connection", "keep-alive", "transfer-encoding", "upgrade", "proxy-authorization", "content-length"},
)
_SKIP_RESPONSE_HEADERS = frozenset(
    {"connection", "keep-alive", "transfer-encoding", "upgrade", "content-length", "content-encoding"},
)


def _body(request: Request) -> bytes:
    body = request.body
    if isinstance(body, bytes):
        return body
    return body.encode() if body else b""


def _request_headers(request: Request) -> dict[str, str]:
    return {
        name: value
        for name, value in request.headers.to_dict().items()
        if name.lower() not in _SKIP_REQUEST_HEADERS
    }


def _response_headers(upstream: httpx.Response, backend: str) -> Headers:
    headers = {
        name: value
        for name, value in upstream.headers.items()
        if name.lower() not in _SKIP_RESPONSE_HEADERS
    }
    headers["X-Proxy-Target"] = backend
    return Headers(headers)


async def _forward(request: Request, encoder) -> Response:
    path = request.url.path
    backend = strangler.pick_backend(path)
    strangler.count(backend)

    logger.info("%s %s -> %s", request.method, path, backend)

    try:
        upstream = await client.request(
            method=request.method,
            url=f"{strangler.base_url(backend)}{path}",
            params=request.query_params.to_dict(),
            headers=_request_headers(request),
            content=_body(request),
        )
    except httpx.RequestError as error:
        logger.warning("%s is unavailable: %s", backend, error)
        return Response(
            status_code=502,
            headers=Headers(_JSON),
            body=encoder.encode(ErrorResponse(error=f"upstream {backend} is unavailable")),
        )

    return Response(
        status_code=upstream.status_code,
        headers=_response_headers(upstream, backend),
        body=upstream.content,
    )


@proxy_router.get("/*subpath")
async def forward_get(request: Request, global_dependencies) -> Response:
    return await _forward(request, global_dependencies["msgspec_json_encoder"])


@proxy_router.post("/*subpath")
async def forward_post(request: Request, global_dependencies) -> Response:
    return await _forward(request, global_dependencies["msgspec_json_encoder"])


@proxy_router.put("/*subpath")
async def forward_put(request: Request, global_dependencies) -> Response:
    return await _forward(request, global_dependencies["msgspec_json_encoder"])


@proxy_router.patch("/*subpath")
async def forward_patch(request: Request, global_dependencies) -> Response:
    return await _forward(request, global_dependencies["msgspec_json_encoder"])


@proxy_router.delete("/*subpath")
async def forward_delete(request: Request, global_dependencies) -> Response:
    return await _forward(request, global_dependencies["msgspec_json_encoder"])
