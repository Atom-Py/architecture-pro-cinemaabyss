import asyncio
import logging

import msgspec
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError

from config.settings import settings
from models.schemas.events import Event

logger = logging.getLogger(__name__)

_task: asyncio.Task | None = None


def topics() -> tuple[str, ...]:
    return (
        settings.MOVIE_EVENTS_TOPIC,
        settings.USER_EVENTS_TOPIC,
        settings.PAYMENT_EVENTS_TOPIC,
    )


async def _consume() -> None:
    consumer = AIOKafkaConsumer(
        *topics(),
        bootstrap_servers=settings.KAFKA_BROKERS,
        group_id=settings.KAFKA_CONSUMER_GROUP,
        auto_offset_reset="earliest",
    )

    for attempt in range(1, settings.KAFKA_START_RETRIES + 1):
        try:
            await consumer.start()
            break
        except KafkaConnectionError as error:
            logger.warning("consumer cannot reach kafka, attempt %d: %s", attempt, error)
            await asyncio.sleep(settings.KAFKA_START_RETRY_DELAY_SECONDS)
    else:
        logger.error("consumer gave up connecting to %s", settings.KAFKA_BROKERS)
        return

    logger.info("consumer started, topics: %s", ", ".join(topics()))
    try:
        async for message in consumer:
            try:
                event = msgspec.json.decode(message.value, type=Event, strict=False)
                logger.info(
                    "handled event id=%s type=%s topic=%s partition=%d offset=%d payload=%s",
                    event.id,
                    event.type,
                    message.topic,
                    message.partition,
                    message.offset,
                    event.payload,
                )
            except Exception:
                logger.exception("failed to process message from %s", message.topic)
    finally:
        await consumer.stop()


def start() -> None:
    # Robyn runs one persistent event loop per process, so a plain background
    # task survives for the lifetime of the service
    global _task
    _task = asyncio.create_task(_consume(), name="events-consumer")


async def stop() -> None:
    global _task
    if _task is None:
        return
    _task.cancel()
    try:
        await _task
    except asyncio.CancelledError:
        pass
    _task = None
