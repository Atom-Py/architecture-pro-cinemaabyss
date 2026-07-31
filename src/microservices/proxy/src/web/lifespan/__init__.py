from msgspec.json import Encoder
from robyn import Robyn

from infra.http.client import client


def register(app: Robyn) -> None:
    app.inject_global(msgspec_json_encoder=Encoder())

    @app.startup_handler
    async def startup() -> None:
        await client.start()

    @app.shutdown_handler
    async def shutdown() -> None:
        await client.stop()
