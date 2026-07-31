from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HOST: str = Field("0.0.0.0", min_length=1)
    PORT: int = Field(8000, ge=1, le=65535)

    MONOLITH_URL: str = Field("http://localhost:8080", min_length=1)
    MOVIES_SERVICE_URL: str = Field("http://localhost:8081", min_length=1)
    EVENTS_SERVICE_URL: str = Field("http://localhost:8082", min_length=1)

    GRADUAL_MIGRATION: bool = Field(False)
    MOVIES_MIGRATION_PERCENT: int = Field(0, ge=0, le=100)

    UPSTREAM_TIMEOUT_SECONDS: float = Field(30.0, gt=0)
    UPSTREAM_CONNECT_TIMEOUT_SECONDS: float = Field(5.0, gt=0)


settings = Settings()
