from collections.abc import Sequence

from fastapi import APIRouter, HTTPException, Query

from flxo.api.dependencies.database import SessionDep
from flxo.models import SeatDTO, SeatPublic
from flxo.services.seat import svc

from typing import Annotated


router = APIRouter(prefix="/seat")


@router.get("/", response_model=Sequence[SeatPublic])
def list_seats(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[SeatPublic]:
    return svc.get_all(session, offset, limit)  # type: ignore


@router.get("/{seat_id}", response_model=SeatPublic)
def get_seat(seat_id: int, session: SessionDep) -> SeatPublic:
    seat = svc.get(session, seat_id)
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    return seat  # type: ignore


@router.post("/", response_model=SeatPublic)
def create_seat(seat: SeatDTO, session: SessionDep) -> SeatPublic:
    return svc.create(session, seat)  # type: ignore


@router.put("/{seat_id}", response_model=SeatPublic)
def update_seat(seat_id: int, seat_dto: SeatDTO, session: SessionDep) -> SeatPublic:
    seat = svc.get(session, seat_id)
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    return svc.update_seat(session, seat_dto, seat)  # type: ignore


@router.delete("/{seat_id}")
def delete_seat(seat_id: int, session: SessionDep) -> dict[str, bool]:
    seat = svc.get(session, seat_id)
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    svc.delete(session, seat)
    return {"ok": True}
