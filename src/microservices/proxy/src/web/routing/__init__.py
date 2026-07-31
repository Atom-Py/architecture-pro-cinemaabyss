from robyn import SubRouter

from web.routing.health import health_router
from web.routing.proxy import proxy_router
from web.routing.stats import stats_router

root_router = SubRouter(prefix="")
root_router.include_router(health_router)
root_router.include_router(stats_router)
root_router.include_router(proxy_router)
