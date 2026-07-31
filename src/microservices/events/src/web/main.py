import logging

from robyn import Robyn

from config.settings import settings
from web import lifespan, routing

logging.basicConfig(level=logging.INFO)

app = Robyn(__file__)

lifespan.register(app)

app.include_router(routing.root_router)

if __name__ == "__main__":
    app.start(host=settings.HOST, port=settings.PORT)
