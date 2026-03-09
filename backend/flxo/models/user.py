from pydantic import field_validator
from sqlmodel import Column, Field, JSON, Relationship, SQLModel

from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
    from flxo.models.presence import Presence
    from flxo.models.seat import Seat


class UserBase(SQLModel):
    username: str = Field(index=True)


class UserDTO(UserBase):
    password: str
    hashed_password: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if len(password) < 8:
            msg = "password is too short"
            raise ValueError(msg)
        return password


class UserPublic(UserBase):
    id: int = Field(default=None, primary_key=True)
    disabled: bool | None = None
    properties: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    favorite_seat_id: int | None = Field(default=None, foreign_key="seat.id")


class User(UserPublic, table=True):
    hashed_password: str | None = None
    presences: list["Presence"] = Relationship(back_populates="user")
    favorite_seat: "Seat | None" = Relationship()


class UserPublicWithPresences(UserPublic):
    presences: list["Presence"] = []
