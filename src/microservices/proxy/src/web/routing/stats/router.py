from robyn import Headers, Response, SubRouter

from services import strangler

stats_router = SubRouter(prefix="/proxy/stats")


@stats_router.get("")
def stats(global_dependencies) -> Response:
    """Show how the traffic was actually split between the backends."""
    return Response(
        status_code=200,
        headers=Headers({"Content-Type": "application/json"}),
        body=global_dependencies["msgspec_json_encoder"].encode(strangler.stats()),
    )
