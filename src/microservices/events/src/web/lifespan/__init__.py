from msgspec.json import Encoder
from robyn import Robyn

from integrations.kafka import consumer
from integrations.kafka.producer import producer


def register(app: Robyn) -> None:
    app.inject_global(msgspec_json_encoder=Encoder())

    @app.startup_handler
    async def startup() -> None:
        await producer.start()
        consumer.start()

    @app.shutdown_handler
    async def shutdown() -> None:
        await consumer.stop()
        await producer.stop()
