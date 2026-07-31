from datetime import datetime
from typing import Any

from msgspec import Struct

MOVIE = "movie"
USER = "user"
PAYMENT = "payment"


class MovieEvent(Struct):
    movie_id: int
    title: str
    action: str
    user_id: int | None = None
    rating: float | None = None
    genres: list[str] | None = None
    description: str | None = None


class UserEvent(Struct):
    user_id: int
    action: str
    timestamp: datetime
    username: str | None = None
    email: str | None = None


class PaymentEvent(Struct):
    payment_id: int
    user_id: int
    amount: float
    status: str
    timestamp: datetime
    method_type: str | None = None


class Event(Struct):
    """Envelope published to Kafka. Payload keeps the original event as is."""

    id: str
    type: str
    timestamp: datetime
    payload: Any


class EventResponse(Struct):
    status: str
    partition: int
    offset: int
    event: Event
