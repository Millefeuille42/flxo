from collections.abc import Sequence
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select

from flxo.models.presence import Presence, PresenceDTO
from flxo.models.user import UserPublic
from flxo.services.auth import get_current_user
from flxo.services.database import SessionDep

from typing import Annotated, Optional

router = APIRouter(prefix="/presence")

# TODO Rewrite into service

@router.get("/me")
def list_self_presences(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
    session: SessionDep,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Presence]:
    return session.exec(
        select(Presence)
        .where(Presence.user_id == current_user.id)
        .offset(offset)
        .limit(limit)
    ).all()
    query = select(Presence).where(Presence.user_id == current_user.id)

    if start:
        query = query.where(Presence.start >= start)
    if end:
        query = query.where(Presence.end <= end)

    query = query.offset(offset).limit(limit)
    return session.exec(query).all()

@router.get("/")

def list_presences(
    _current_user: Annotated[UserPublic, Depends(get_current_user)],
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Presence]:
    return session.exec(
        select(Presence)
        .offset(offset)
        .limit(limit)
    ).all()
        _current_user: Annotated[UserPublic, Depends(get_current_user)],
        session: SessionDep,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    query = select(Presence)

    if start:
        query = query.where(Presence.start >= start)
    if end:
        query = query.where(Presence.end <= end)

    query = query.offset(offset).limit(limit)
    return session.exec(query).all()


@router.get("/{presence_id}", response_model=Presence)
def get_presence(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
    presence_id: int, session: SessionDep
) -> Presence:
    presence = session.exec(
        select(Presence)
        .where(Presence.id == presence_id)
        .where(Presence.user_id == current_user.id)
    ).first()
    if not presence:
        raise HTTPException(status_code=404, detail="presence not found")
    return presence


@router.post("/", response_model=Presence)
def create_presence(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
    presence: PresenceDTO, session: SessionDep
) -> Presence:
    overlaps = session.exec(
        select(Presence)
        .where(Presence.user_id == current_user.id)
        .where(
            (Presence.start < presence.end)
            & (Presence.end > presence.start)
        )
    ).first()
    if overlaps:
        raise HTTPException(
            status_code=400, detail="Presence overlaps with an existing one"
        )

    if presence.start < datetime.now(presence.start.tzinfo):
        raise HTTPException(
            status_code=400, detail="start must be after current date"
        )

    db_presence = Presence(
        user_id=current_user.id,
        start=presence.start,
        end=presence.end,
    )
    session.add(db_presence)
    session.commit()
    session.refresh(db_presence)
    return db_presence


@router.put("/{presence_id}", response_model=Presence)
def update_presence(
        current_user: Annotated[UserPublic, Depends(get_current_user)],
        presence_id: int,
        presence_update: PresenceDTO,
        session: SessionDep
) -> Presence:
    presence = session.exec(
        select(Presence)
        .where(Presence.id == presence_id)
        .where(Presence.user_id == current_user.id)
    ).first()

    if not presence:
        raise HTTPException(status_code=404, detail="Presence not found")

    overlap = session.exec(
        select(Presence)
        .where(Presence.user_id == current_user.id)
        .where(Presence.id != presence_id)
        .where(
            (Presence.start < presence_update.end)
            & (Presence.end > presence_update.start)
        )
    ).first()

    if overlap:
        raise HTTPException(status_code=400, detail="Updated presence overlaps with an existing one")

    presence.start = presence_update.start
    presence.end = presence_update.end

    session.add(presence)
    session.commit()
    session.refresh(presence)
    return presence


@router.delete("/{presence_id}")
def delete_presence(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
    presence_id: int, session: SessionDep
):
    presence = session.exec(
        select(Presence)
        .where(Presence.id == presence_id)
        .where(Presence.user_id == current_user.id)
    ).first()
    if not presence:
        raise HTTPException(status_code=404, detail="presence not found")
    session.delete(presence)
    session.commit()
    return {"ok": True}
