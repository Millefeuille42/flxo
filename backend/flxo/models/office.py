from sqlmodel import Column, Field, JSON, Relationship, SQLModel

from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
    from flxo.models.presence import Presence
    from flxo.models.seat import Seat


class OfficeBase(SQLModel):
    name: str
    address: str
    properties: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class OfficeDTO(OfficeBase):
    pass


class Office(OfficeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    seats: list["Seat"] = Relationship(back_populates="office")
    presences: list["Presence"] = Relationship(back_populates="office")


class OfficeWithSeats(OfficeDTO):
    seats: list["Seat"] = []


class OfficeWithPresences(OfficeDTO):
    presences: list["Presence"] = []


class OfficePublic(OfficeBase):
    id: int
