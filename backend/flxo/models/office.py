from sqlmodel import Field, Relationship, SQLModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .presence import Presence
    from .seat import Seat, SeatWithProperties


class OfficeBase(SQLModel):
    name: str
    address: str


class OfficeDTO(OfficeBase):
    pass


class Office(OfficeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    seats: list["Seat"] = Relationship(back_populates="office")
    presences: list["Presence"] = Relationship(back_populates="office")


class OfficeWithSeats(OfficeDTO):
    seats: list["SeatWithProperties"] = []


class OfficeWithPresences(OfficeDTO):
    presences: list["Presence"] = []


class OfficePublic(OfficeWithSeats, OfficeWithPresences):
    pass
