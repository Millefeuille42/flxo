from datetime import datetime, UTC

from pydantic import field_serializer, field_validator, model_validator
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

from flxo.models.office import Office, OfficePublic
from flxo.models.seat import Seat, SeatPublic
from flxo.models.user import User, UserPublic

from typing import Optional


class PresenceBase(SQLModel):
    start: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    end: datetime = Field(sa_column=Column(DateTime(timezone=True)))

    @field_validator("start", "end", mode="before")
    def force_utc(cls, value: datetime | str) -> datetime:  # noqa: N805
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_date_range(self) -> "PresenceBase":
        if self.end <= self.start:
            msg = "end must be after start"
            raise ValueError(msg)
        return self

    @field_serializer("start", "end")
    def serialize_dt(self, value: datetime) -> Optional[datetime]:
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


class PresenceDTO(PresenceBase):
    seat_id: int = Field(default=0, foreign_key="seat.id")


class Presence(PresenceDTO, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    office_id: int | None = Field(default=None, foreign_key="office.id")

    user: "User" = Relationship(back_populates="presences")
    office: "Office" = Relationship(back_populates="presences")
    seat: "Seat" = Relationship(back_populates="presences")


class PresenceWithOffice(PresenceDTO):
    id: int
    office: OfficePublic


class PresenceWithSeat(PresenceDTO):
    id: int
    seat: SeatPublic


class PresenceWithUser(PresenceDTO):
    id: int
    user: UserPublic


class PresencePublic(PresenceBase):
    pass
