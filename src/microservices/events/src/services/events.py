import logging
from datetime import UTC, datetime

from config.settings import settings
from integrations.kafka.producer import producer
from models.schemas.events import (
    MOVIE,
    PAYMENT,
    USER,
    Event,
    EventResponse,
    MovieEvent,
    PaymentEvent,
    UserEvent,
)

logger = logging.getLogger(__name__)


async def publish_movie_event(data: MovieEvent) -> EventResponse:
    event = Event(
        id=f"movie-{data.movie_id}-{data.action}",
        type=MOVIE,
        timestamp=datetime.now(UTC),
        payload=data,
    )
    return await _publish(settings.MOVIE_EVENTS_TOPIC, event)


async def publish_user_event(data: UserEvent) -> EventResponse:
    event = Event(
        id=f"user-{data.user_id}-{data.action}",
        type=USER,
        timestamp=datetime.now(UTC),
        payload=data,
    )
    return await _publish(settings.USER_EVENTS_TOPIC, event)


async def publish_payment_event(data: PaymentEvent) -> EventResponse:
    event = Event(
        id=f"payment-{data.payment_id}-{data.status}",
        type=PAYMENT,
        timestamp=datetime.now(UTC),
        payload=data,
    )
    return await _publish(settings.PAYMENT_EVENTS_TOPIC, event)


async def _publish(topic: str, event: Event) -> EventResponse:
    metadata = await producer.publish(topic, event)
    logger.info(
        "published event id=%s topic=%s partition=%d offset=%d",
        event.id,
        topic,
        metadata.partition,
        metadata.offset,
    )
    return EventResponse(
        status="success",
        partition=metadata.partition,
        offset=metadata.offset,
        event=event,
    )
