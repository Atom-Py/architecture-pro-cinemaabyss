from robyn import Headers, Response, SubRouter

health_router = SubRouter(prefix="/health")


@health_router.get("")
def health() -> Response:
    return Response(
        status_code=200,
        headers=Headers({"Content-Type": "text/plain; charset=utf-8"}),
        body=b"Strangler Fig Proxy is healthy",
    )
