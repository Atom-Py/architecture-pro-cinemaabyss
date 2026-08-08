from msgspec import Struct


class ProxyStats(Struct):
    gradual_migration: bool
    movies_migration_percent: int
    requests: dict[str, int]
