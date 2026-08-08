import random

from config.settings import settings
from models.schemas.stats import ProxyStats

MONOLITH = "monolith"
MOVIES = "movies-service"
EVENTS = "events-service"

_requests: dict[str, int] = {MONOLITH: 0, MOVIES: 0, EVENTS: 0}


def base_url(backend: str) -> str:
    return {
        MONOLITH: settings.MONOLITH_URL,
        MOVIES: settings.MOVIES_SERVICE_URL,
        EVENTS: settings.EVENTS_SERVICE_URL,
    }[backend]


def pick_backend(path: str) -> str:
    """Choose the upstream for a request path.

    Movies is the only extracted domain, so it is the only one that can be split
    between two implementations.
    """
    if path.startswith("/api/events"):
        return EVENTS
    # Health of the extracted service must answer from that service itself
    if path == "/api/movies/health":
        return MOVIES
    if path == "/api/movies" or path.startswith("/api/movies/"):
        return _movies_backend()
    return MONOLITH


def _movies_backend() -> str:
    if not settings.GRADUAL_MIGRATION:
        return MONOLITH
    if random.randrange(100) < settings.MOVIES_MIGRATION_PERCENT:
        return MOVIES
    return MONOLITH


def count(backend: str) -> None:
    _requests[backend] += 1


def stats() -> ProxyStats:
    return ProxyStats(
        gradual_migration=settings.GRADUAL_MIGRATION,
        movies_migration_percent=settings.MOVIES_MIGRATION_PERCENT,
        requests=dict(_requests),
    )
