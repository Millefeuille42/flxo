from collections.abc import Sequence

from fastapi import APIRouter, HTTPException, Query

from flxo.api.dependencies.database import SessionDep
from flxo.models.seat import SeatDTO, SeatPublic
from flxo.services.seat import svc

from .property import router as property_router

from typing import Annotated

router = APIRouter(prefix="/seat")
router.include_router(property_router, tags=["property"])


@router.get("/", response_model=Sequence[SeatPublic])
def list_seats(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return svc.get_all(session, offset, limit)


@router.get("/{seat_id}", response_model=SeatPublic)
def get_seat(seat_id: int, session: SessionDep):
    seat = svc.get(session, seat_id)
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    return seat


@router.post("/", response_model=SeatPublic)
def create_seat(seat: SeatDTO, session: SessionDep):
    return svc.create(session, seat)  # type: ignore


@router.put("/{seat_id}", response_model=SeatPublic)
def update_seat(seat_id: int, seat_dto: SeatDTO, session: SessionDep):
    seat = svc.get(session, seat_id)
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    return svc.update_seat(session, seat_dto, seat)


@router.delete("/{seat_id}")
def delete_seat(seat_id: int, session: SessionDep):
    seat = svc.get(session, seat_id)
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    svc.delete(session, seat)
    return {"ok": True}
