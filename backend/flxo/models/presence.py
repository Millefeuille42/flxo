from datetime import date

from pydantic import field_validator
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from flxo.models.office import Office, OfficePublic
from flxo.models.seat import Seat, SeatPublic
from flxo.models.user import User, UserPublic


class PresenceBase(SQLModel):
    date: date
    slot: str
    state: str = "confirmed"
    office_id: int = Field(foreign_key="office.id")
    seat_id: int = Field(foreign_key="seat.id")

    @field_validator("slot")
    @classmethod
    def validate_slot(cls, v: str) -> str:
        if v not in ("morning", "afternoon"):
            msg = "slot must be 'morning' or 'afternoon'"
            raise ValueError(msg)
        return v

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        if v not in ("confirmed", "maybe"):
            msg = "state must be 'confirmed' or 'maybe'"
            raise ValueError(msg)
        return v


class PresenceDTO(PresenceBase):
    pass


class Presence(PresenceBase, table=True):
    __table_args__ = (
        UniqueConstraint("user_id", "date", "slot", name="uq_presence_user_id_date_slot"),
        UniqueConstraint("seat_id", "date", "slot", name="uq_presence_seat_id_date_slot"),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

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


class PresencePublic(PresenceDTO):
    id: int
