from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from flxo.models.office import Office

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flxo.models.presence import Presence


class SeatBase(SQLModel):
    name: str
    properties: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class SeatDTO(SeatBase):
    office_id: int


class Seat(SeatBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    office_id: int = Field(foreign_key="office.id")

    presences: list["Presence"] = Relationship(back_populates="seat")
    office: "Office" = Relationship(back_populates="seats")


class SeatWithPresences(SeatDTO):
    presences: list["Presence"] = []


class SeatWithOffice(SeatDTO):
    office: Office


class SeatPublic(SeatWithOffice):
    pass
