from datetime import UTC, datetime

from pydantic import field_serializer, field_validator, model_validator
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

from flxo.models.user import User, UserPublic


class PresenceBase(SQLModel):
    start: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    end: datetime = Field(sa_column=Column(DateTime(timezone=True)))

    @field_validator("start", "end", mode="before")
    def force_utc(cls, value):
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.end <= self.start:
            msg = "end must be after start"
            raise ValueError(msg)
        return self

    @field_serializer("start", "end")
    def serialize_dt(self, value: datetime, _info):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


class PresenceDTO(PresenceBase):
    pass


class Presence(PresenceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    user: User = Relationship(back_populates="presences")


class PresenceWithUser(PresenceDTO):
    id: int
    user: UserPublic
