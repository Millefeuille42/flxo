from sqlmodel import Field, Relationship, SQLModel

from .office import Office

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .presence import Presence
    from .property import Property


class SeatBase(SQLModel):
    name: str


class SeatDTO(SeatBase):
    office_id: int


class Seat(SeatBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    office_id: int = Field(foreign_key="office.id")

    properties: list["Property"] = Relationship(back_populates="seat")
    presences: list["Presence"] = Relationship(back_populates="seat")
    office: "Office" = Relationship(back_populates="seats")


class SeatWithProperties(SeatDTO):
    properties: list["Property"] = []


class SeatWithPresences(SeatDTO):
    presences: list["Presence"] = []


class SeatWithOffice(SeatDTO):
    office: Office


class SeatPublic(SeatWithProperties, SeatWithOffice):
    pass
