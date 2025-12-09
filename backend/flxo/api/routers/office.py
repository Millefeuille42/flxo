from collections.abc import Sequence

from fastapi import APIRouter, HTTPException, Query

from flxo.api.dependencies.database import SessionDep
from flxo.models.office import OfficeDTO, OfficePublic
from flxo.models.seat import SeatPublic
from flxo.services.office import svc

from typing import Annotated

router = APIRouter(prefix="/office")


@router.get("/", response_model=Sequence[OfficePublic])
def list_offices(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return svc.get_all(session, offset, limit)


@router.get("/{office_id}", response_model=OfficePublic)
def get_office(office_id: int, session: SessionDep):
    office = svc.get(session, office_id)
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")
    return office


@router.get("/{office_id}/seats", response_model=Sequence[SeatPublic])
def get_office_seats(office_id: int, session: SessionDep):
    office = svc.get(session, office_id)
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")
    return office.seats


@router.post("/", response_model=OfficePublic)
def create_office(office: OfficeDTO, session: SessionDep):
    return svc.create(session, office)  # type: ignore


@router.put("/{office_id}", response_model=OfficePublic)
def update_office(office_id: int, office_dto: OfficeDTO, session: SessionDep):
    office = svc.get(session, office_id)
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")
    return svc.update_office(session, office_dto, office)


@router.delete("/{office_id}")
def delete_office(office_id: int, session: SessionDep):
    office = svc.get(session, office_id)
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")
    svc.delete(session, office)
    return {"ok": True}
