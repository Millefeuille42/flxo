from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED


class InvalidCredentialsException(HTTPException):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=message,
        )
