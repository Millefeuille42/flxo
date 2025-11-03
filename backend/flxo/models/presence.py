import datetime

from pydantic import field_validator, model_validator
from sqlmodel import Field, SQLModel

class PresenceBase(SQLModel):
    from_date: datetime.datetime = Field(default=None)
    to_date: datetime.datetime = Field(default=None)

    @field_validator("from_date")
    @classmethod
    def validate_start_date(cls, from_date):
        if from_date < datetime.datetime.now(from_date.tzinfo):
            msg = "from_date must be after current date"
            raise ValueError(msg)
        return from_date

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.to_date <= self.from_date:
            msg = "to_date must be after to from_date"
            raise ValueError(msg)
        return self


class PresenceDTO(PresenceBase):
    pass


class Presence(PresenceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
