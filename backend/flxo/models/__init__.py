from flxo.models.office import (
    Office,
    OfficeDTO,
    OfficePublic,
    OfficeWithPresences,
    OfficeWithSeats,
)
from flxo.models.presence import Presence, PresenceDTO, PresencePublic, PresenceWithUser
from flxo.models.property import Property, PropertyDTO, PropertyPublic
from flxo.models.seat import Seat, SeatDTO, SeatPublic, SeatWithProperties
from flxo.models.user import User, UserDTO, UserPublic


Seat.model_rebuild()
SeatPublic.model_rebuild()
SeatDTO.model_rebuild()
SeatWithProperties.model_rebuild()
Property.model_rebuild()
PropertyDTO.model_rebuild()
PropertyPublic.model_rebuild()
Presence.model_rebuild()
PresenceDTO.model_rebuild()
PresencePublic.model_rebuild()
PresenceWithUser.model_rebuild()
Office.model_rebuild()
OfficeDTO.model_rebuild()
OfficeWithSeats.model_rebuild()
OfficeWithPresences.model_rebuild()
OfficePublic.model_rebuild()
User.model_rebuild()
UserDTO.model_rebuild()
UserPublic.model_rebuild()

__all__ = [
    "Seat",
    "SeatDTO",
    "SeatPublic",
    "Property",
    "PropertyDTO",
    "PropertyPublic",
    "Presence",
    "PresenceDTO",
    "PresencePublic",
    "PresenceWithUser",
    "Office",
    "OfficeDTO",
    "OfficePublic",
    "User",
    "UserDTO",
    "UserPublic",
]
