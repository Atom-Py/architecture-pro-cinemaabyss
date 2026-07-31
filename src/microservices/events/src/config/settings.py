from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HOST: str = Field("0.0.0.0", min_length=1)
    PORT: int = Field(8082, ge=1, le=65535)

    KAFKA_BROKERS: str = Field("localhost:9092", min_length=1)
    KAFKA_CONSUMER_GROUP: str = Field("events-service", min_length=1)

    MOVIE_EVENTS_TOPIC: str = Field("movie-events", min_length=1)
    USER_EVENTS_TOPIC: str = Field("user-events", min_length=1)
    PAYMENT_EVENTS_TOPIC: str = Field("payment-events", min_length=1)

    KAFKA_START_RETRIES: int = Field(30, ge=1)
    KAFKA_START_RETRY_DELAY_SECONDS: float = Field(2.0, gt=0)


settings = Settings()
