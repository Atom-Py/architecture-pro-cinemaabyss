import logging

import msgspec
from robyn import Headers, Request, Response, SubRouter

from models.schemas.errors import ErrorResponse
from models.schemas.events import MovieEvent, PaymentEvent, UserEvent
from services import events

logger = logging.getLogger(__name__)

events_router = SubRouter(prefix="/api/events")

_JSON = {"Content-Type": "application/json"}


@events_router.get("/health")
def health() -> Response:
    return Response(
        status_code=200,
        headers=Headers(_JSON),
        body=b'{"status":true}',
    )


@events_router.post("/movie")
async def create_movie_event(request: Request, global_dependencies) -> Response:
    encoder = global_dependencies["msgspec_json_encoder"]
    try:
        data = msgspec.json.decode(request.body, type=MovieEvent, strict=False)
    except (msgspec.ValidationError, msgspec.DecodeError) as error:
        return _bad_request(encoder, error)
    return await _publish(encoder, events.publish_movie_event(data))


@events_router.post("/user")
async def create_user_event(request: Request, global_dependencies) -> Response:
    encoder = global_dependencies["msgspec_json_encoder"]
    try:
        data = msgspec.json.decode(request.body, type=UserEvent, strict=False)
    except (msgspec.ValidationError, msgspec.DecodeError) as error:
        return _bad_request(encoder, error)
    return await _publish(encoder, events.publish_user_event(data))


@events_router.post("/payment")
async def create_payment_event(request: Request, global_dependencies) -> Response:
    encoder = global_dependencies["msgspec_json_encoder"]
    try:
        data = msgspec.json.decode(request.body, type=PaymentEvent, strict=False)
    except (msgspec.ValidationError, msgspec.DecodeError) as error:
        return _bad_request(encoder, error)
    return await _publish(encoder, events.publish_payment_event(data))


async def _publish(encoder, coroutine) -> Response:
    try:
        result = await coroutine
    except Exception as error:
        logger.exception("failed to publish event")
        return Response(
            status_code=500,
            headers=Headers(_JSON),
            body=encoder.encode(ErrorResponse(error=f"failed to publish event: {error}")),
        )

    return Response(
        status_code=201,
        headers=Headers(_JSON),
        body=encoder.encode(result),
    )


def _bad_request(encoder, error: Exception) -> Response:
    return Response(
        status_code=400,
        headers=Headers(_JSON),
        body=encoder.encode(ErrorResponse(error=str(error))),
    )
