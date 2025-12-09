from sqlmodel import Field, Relationship, SQLModel

from .seat import Seat


class PropertyBase(SQLModel):
    name: str
    value: str


class PropertyDTO(PropertyBase):
    pass


class Property(PropertyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    seat_id: int = Field(foreign_key="seat.id")
    seat: "Seat" = Relationship(back_populates="properties")


class PropertyWithSeat(PropertyDTO):
    seat: Seat


class PropertyPublic(PropertyDTO):
    pass
