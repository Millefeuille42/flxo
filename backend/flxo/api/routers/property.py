from collections.abc import Sequence

from fastapi import APIRouter, HTTPException

from flxo.api.dependencies.database import SessionDep
from flxo.models.property import PropertyDTO, PropertyPublic
from flxo.services.property import svc

router = APIRouter(prefix="/property")


@router.get("/{seat_id}", response_model=Sequence[PropertyPublic])
def get_properties_of_seat(seat_id: int, session: SessionDep):
    return svc.get_properties_of_seat(session, seat_id)


@router.get("/{seat_id}/{property_name}", response_model=PropertyPublic)
def get_property_of_seat(seat_id: int, property_name: str, session: SessionDep):
    prop = svc.get_property_of_seat(session, seat_id, property_name)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.post("/{seat_id}", response_model=PropertyPublic)
def create_property_of_seat(seat_id: int, property_dto: PropertyDTO, session: SessionDep):
    return svc.create_property_of_seat(session, property_dto, seat_id)


@router.put("/{seat_id}/{property_name}", response_model=PropertyPublic)
def update_property_of_seat(
    seat_id: int, property_name: str, property_dto: PropertyDTO, session: SessionDep
):
    prop = svc.get_property_of_seat(session, seat_id, property_name)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return svc.update_property_of_seat(session, property_dto, prop)  # type: ignore


@router.delete("/{seat_id}/{property_name}")
def delete_property_of_seat(seat_id: int, property_name: str, session: SessionDep):
    prop = svc.get_property_of_seat(session, seat_id, property_name)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    svc.delete(session, prop)
    return {"ok": True}
