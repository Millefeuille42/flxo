from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .presence import Presence


class UserBase(SQLModel):
    username: str = Field(index=True)


class UserDTO(UserBase):
    password: str
    hashed_password: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):
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
