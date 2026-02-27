from pydantic import field_validator
from sqlmodel import Column, Field, JSON, Relationship, SQLModel

from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
    from flxo.models.presence import Presence


class UserBase(SQLModel):
    username: str = Field(index=True)
    properties: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class UserDTO(UserBase):
    password: str
    hashed_password: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str | ValueError:
        if len(password) < 8:
            return ValueError("password is too short")
        return password


class UserPublic(UserBase):
    id: int = Field(default=None, primary_key=True)
    disabled: bool | None = None


class User(UserPublic, table=True):
    hashed_password: str | None = None
    presences: list["Presence"] = Relationship(back_populates="user")


class UserPublicWithPresences(UserPublic):
    presences: list["Presence"] = []
