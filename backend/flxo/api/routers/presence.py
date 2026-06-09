from collections.abc import Sequence
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from flxo.api.dependencies.database import SessionDep
from flxo.api.dependencies.user import UserDep
from flxo.models.ics_response import ICSResponse
from flxo.models.presence import Presence, PresenceDTO, PresencePublic, PresenceWithUser
from flxo.services.presence import svc

from typing import Annotated


router = APIRouter(prefix="/presence")


def _raise_conflict(conflict: Presence, user_id: int) -> None:
    if conflict.user_id == user_id and conflict.seat_id:
        msg = "You already have a desk booked for this slot"
        raise HTTPException(status_code=409, detail=msg)
    if conflict.user_id == user_id:
        msg = f"Presence overlaps with an existing one (office: {conflict.office.name})"
        raise HTTPException(status_code=400, detail=msg)
    msg = "This desk is already booked for this slot"
    raise HTTPException(status_code=409, detail=msg)


@router.get("/me", response_model=Sequence[PresenceWithUser])
def list_self_presences(
    current_user: UserDep,
    session: SessionDep,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    offset: int = 0,
    limit: Annotated[int, Query(le=1000)] = 500,
) -> Sequence[PresenceWithUser]:
    return svc.get_all_presences_of_user(  # type: ignore
        session, current_user.id, date_from, date_to, offset, limit
    )


@router.get("/me/ics", response_class=ICSResponse)
def list_self_presences_as_ics(
    current_user: UserDep,
    session: SessionDep,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    offset: int = 0,
    limit: Annotated[int, Query(le=1000)] = 500,
    is_all_day: bool = False,
) -> str:
    return svc.get_all_presences_of_user_as_ics(
        session, current_user.id, date_from, date_to, offset, limit, is_all_day=is_all_day
    ).serialize()


@router.get("/", response_model=Sequence[PresenceWithUser])
def list_presences(
    _current_user: UserDep,
    session: SessionDep,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    offset: int = 0,
    limit: Annotated[int, Query(le=1000)] = 500,
) -> Sequence[PresenceWithUser]:
    return svc.get_all_presences(session, date_from, date_to, offset, limit)  # type: ignore


@router.get("/ics", response_class=ICSResponse)
def list_presences_as_ics(
    _current_user: UserDep,
    session: SessionDep,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    offset: int = 0,
    limit: Annotated[int, Query(le=1000)] = 500,
    is_all_day: bool = False,
) -> str:
    return svc.get_all_presences_as_ics(
        session, date_from, date_to, offset, limit, is_all_day=is_all_day
    ).serialize()


@router.get("/{presence_id}", response_model=PresencePublic)
def get_presence_by_id(
    current_user: UserDep,
    presence_id: int,
    session: SessionDep,
) -> Presence:
    presence = svc.get_presence(session, presence_id, current_user.id)
    if not presence:
        raise HTTPException(status_code=404, detail="presence not found")
    return presence


@router.post("/", response_model=PresencePublic)
def create_presence(
    current_user: UserDep,
    presence: PresenceDTO,
    session: SessionDep,
) -> Presence:
    conflict = svc.find_conflict(
        session, current_user.id, presence.date, presence.slot, presence.seat_id
    )
    if conflict:
        _raise_conflict(conflict, current_user.id)
    return svc.create_presence(session, presence, current_user.id)


@router.put("/{presence_id}", response_model=PresencePublic)
def update_presence(
    current_user: UserDep,
    presence_id: int,
    presence_dto: PresenceDTO,
    session: SessionDep,
) -> Presence:
    presence = svc.get_presence(session, presence_id, current_user.id)
    if not presence:
        raise HTTPException(status_code=404, detail="Presence not found")

    conflict = svc.find_conflict(
        session,
        current_user.id,
        presence_dto.date,
        presence_dto.slot,
        presence_dto.seat_id,
        presence.id,
    )
    if conflict:
        _raise_conflict(conflict, current_user.id)

    return svc.update_presence(session, presence_dto, presence)


@router.delete("/{presence_id}")
def delete_presence(
    current_user: UserDep,
    presence_id: int,
    session: SessionDep,
) -> dict[str, bool]:
    presence = svc.get_presence(session, presence_id, current_user.id)
    if not presence:
        raise HTTPException(status_code=404, detail="presence not found")
    svc.delete(session, presence)
    return {"ok": True}
