from robyn import SubRouter

from web.routing.events import events_router

root_router = SubRouter(prefix="")
root_router.include_router(events_router)
