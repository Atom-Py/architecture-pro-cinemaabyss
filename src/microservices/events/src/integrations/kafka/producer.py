import asyncio
import logging

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError
from aiokafka.structs import RecordMetadata
from msgspec import Struct
from msgspec.json import Encoder

from config.settings import settings

logger = logging.getLogger(__name__)


class KafkaProducer:
    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None
        self._encoder = Encoder()

    async def start(self) -> None:
        # The broker and this service start together, so the first attempts fail
        last_error: Exception | None = None
        for attempt in range(1, settings.KAFKA_START_RETRIES + 1):
            producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BROKERS)
            try:
                await producer.start()
            except KafkaConnectionError as error:
                last_error = error
                logger.warning("kafka is not ready yet, attempt %d: %s", attempt, error)
                await producer.stop()
                await asyncio.sleep(settings.KAFKA_START_RETRY_DELAY_SECONDS)
                continue
            self._producer = producer
            logger.info("kafka producer connected to %s", settings.KAFKA_BROKERS)
            return

        raise RuntimeError(f"kafka is unavailable at {settings.KAFKA_BROKERS}") from last_error

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None

    async def publish(self, topic: str, event: Struct) -> RecordMetadata:
        if self._producer is None:
            raise RuntimeError("kafka producer is not started")
        return await self._producer.send_and_wait(topic, self._encoder.encode(event))


producer = KafkaProducer()
