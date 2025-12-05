from collections.abc import Sequence
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

import flxo.services.presence as svc
from flxo.models.ics_response import ICSResponse
from flxo.models.presence import Presence, PresenceDTO, PresenceWithUser
from flxo.models.user import UserPublic
from flxo.services.auth import get_current_user
from flxo.services.database import SessionDep

from typing import Annotated

router = APIRouter(prefix="/presence")


@router.get("/me", response_model=Sequence[PresenceWithUser])
def list_self_presences(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
    session: SessionDep,
    start: datetime | None = None,
    end: datetime | None = None,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[PresenceWithUser]:
    return svc.get_all_presences_of_user(  # type: ignore
        session, current_user.id, start, end, offset, limit
    )


@router.get("/me/ics", response_class=ICSResponse)
def list_self_presences_as_ics(
        current_user: Annotated[UserPublic, Depends(get_current_user)],
        session: SessionDep,
        start: datetime | None = None,
        end: datetime | None = None,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
        all_day: bool = False
) -> str:
    return svc.get_all_presences_of_user_as_ics(
        session, current_user.id, start, end, offset, limit, all_day
    ).serialize()


@router.get("/", response_model=Sequence[PresenceWithUser])
def list_presences(
        _current_user: Annotated[UserPublic, Depends(get_current_user)],
        session: SessionDep,
        start: datetime | None = None,
        end: datetime | None = None,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[PresenceWithUser]:
    return svc.get_all_presences(session, start, end, offset, limit)  # type: ignore


@router.get("/ics", response_class=ICSResponse)
def list_presences_as_ics(
        _current_user: Annotated[UserPublic, Depends(get_current_user)],
        session: SessionDep,
        start: datetime | None = None,
        end: datetime | None = None,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
        all_day: bool = False
) -> str:
    return svc.get_all_presences_as_ics(
        session, start, end, offset, limit, all_day
    ).serialize()


@router.get("/{presence_id}", response_model=Presence)
def get_presence_by_id(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
    presence_id: int, session: SessionDep
) -> Presence:
    presence = svc.get_presence(session, presence_id, current_user.id)
    if not presence:
        raise HTTPException(status_code=404, detail="presence not found")
    return presence


@router.post("/", response_model=Presence)
def create_presence(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
    presence: PresenceDTO, session: SessionDep
) -> Presence:
    if svc.does_presence_overlap(
        session, current_user.id, presence.start, presence.end
    ):
        raise HTTPException(
            status_code=400, detail="Presence overlaps with an existing one"
        )

    if presence.start < datetime.now(presence.start.tzinfo):
        raise HTTPException(
            status_code=400, detail="start must be after current date"
        )

    return svc.create_presence(session, presence, current_user.id)


@router.put("/{presence_id}", response_model=Presence)
def update_presence(
        current_user: Annotated[UserPublic, Depends(get_current_user)],
        presence_id: int,
        presence_dto: PresenceDTO,
        session: SessionDep
) -> Presence:
    presence = svc.get_presence(session, presence_id, current_user.id)
    if not presence:
        raise HTTPException(status_code=404, detail="Presence not found")

    if svc.does_presence_overlap(
        session, current_user.id, presence_dto.start, presence_dto.end, presence.id
    ):
        raise HTTPException(
            status_code=400,
            detail="Updated presence overlaps with an existing one"
        )

    return svc.update_presence(session, presence_dto, presence)


@router.delete("/{presence_id}")
def delete_presence(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
    presence_id: int, session: SessionDep
):
    presence = svc.get_presence(session, presence_id, current_user.id)
    if not presence:
        raise HTTPException(status_code=404, detail="presence not found")
    svc.delete_presence(session, presence)
    return {"ok": True}
