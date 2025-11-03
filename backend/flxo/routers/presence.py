from typing import Annotated, Any, Sequence

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import select

from flxo.models.user import UserPublic
from flxo.services.auth import get_current_user
from flxo.services.database import SessionDep
from flxo.models.presence import PresenceDTO, Presence

router = APIRouter(prefix="/presence")

@router.get("/")
def list_self_presences(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Presence]:
    return session.exec(
        select(Presence)
        .where(Presence.user_id == current_user.id)
        .offset(offset)
        .limit(limit)
    ).all()

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
            (Presence.from_date < presence.to_date)
            & (Presence.to_date > presence.from_date)
        )
    ).first()
    if overlaps:
        raise HTTPException(status_code=400, detail="Presence overlaps with an existing one")

    db_presence = Presence(
        user_id=current_user.id,
        from_date=presence.from_date,
        to_date=presence.to_date,
    )
    session.add(db_presence)
    session.commit()
    session.refresh(db_presence)
    return db_presence

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