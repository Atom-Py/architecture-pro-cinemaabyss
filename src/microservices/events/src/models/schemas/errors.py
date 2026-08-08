from msgspec import Struct


class ErrorResponse(Struct):
    error: str
