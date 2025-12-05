from collections.abc import Sequence
from datetime import datetime

from ics import Calendar, Event
from sqlmodel import select

from flxo.models.presence import Presence, PresenceDTO
from flxo.services.database import SessionDep

from typing import Any


def get_all_presences(
    session: SessionDep,
    start: datetime | None = None,
    end: datetime | None = None,
    offset: int = 100,
    limit: int = 100,
    query: Any = None,
) -> Sequence[Presence]:
    if not query:
        query = select(Presence)
    if start:
        query = query.where(Presence.start >= start)
    if end:
        query = query.where(Presence.end <= end)

    query = query.offset(offset).limit(limit)
    return session.exec(query).all()


def get_all_presences_of_user(
    session: SessionDep,
    user_id: int,
    start: datetime | None = None,
    end: datetime | None = None,
    offset: int = 100,
    limit: int = 100,
) -> Sequence[Presence]:
    return get_all_presences(
        session,
        start,
        end,
        offset,
        limit,
        select(Presence).where(Presence.user_id == user_id),
    )


def get_presence(
    session: SessionDep,
    presence_id: int,
    user_id: int,
) -> Presence | None:
    return session.exec(
        select(Presence)
        .where(Presence.id == presence_id)
        .where(Presence.user_id == user_id)
    ).first()


def does_presence_overlap(
    session: SessionDep,
    user_id: int,
    start: datetime,
    end: datetime,
    presence_id: int | None = None,
) -> bool:
    query = select(Presence).where(Presence.user_id == user_id)
    if presence_id:
        query = query.where(Presence.id != presence_id)
    query = query.where((Presence.start < end) & (Presence.end > start))
    return session.exec(query).first() is not None


def create_presence(session: SessionDep, presence: PresenceDTO, user_id: int) -> Presence:
    db_presence = Presence(
        user_id=user_id,
        start=presence.start,
        end=presence.end,
    )
    session.add(db_presence)
    session.commit()
    session.refresh(db_presence)
    return db_presence


def update_presence(
    session: SessionDep, presence_dto: PresenceDTO, presence: Presence
) -> Presence:
    presence.start = presence_dto.start
    presence.end = presence_dto.end

    session.add(presence)
    session.commit()
    session.refresh(presence)
    return presence


def delete_presence(session: SessionDep, presence: Presence):
    session.delete(presence)
    session.commit()


def presences_to_ics(presences: Sequence[Presence], all_day: bool = False) -> Calendar:
    c = Calendar()
    for presence in presences:
        e = Event()
        e.begin = presence.start
        e.end = presence.end
        if all_day:
            e.make_all_day()
        e.name = f"{presence.user.username} - Office"
        c.events.add(e)
    return c


def get_all_presences_as_ics(
    session: SessionDep,
    start: datetime | None = None,
    end: datetime | None = None,
    offset: int = 100,
    limit: int = 100,
    all_day: bool = False,
) -> Calendar:
    return presences_to_ics(
        get_all_presences(session, start, end, offset, limit), all_day
    )


def get_all_presences_of_user_as_ics(
    session: SessionDep,
    user_id: int,
    start: datetime | None = None,
    end: datetime | None = None,
    offset: int = 100,
    limit: int = 100,
    all_day: bool = False,
) -> Calendar:
    return presences_to_ics(
        get_all_presences(
            session,
            start,
            end,
            offset,
            limit,
            select(Presence).where(Presence.user_id == user_id),
        ),
        all_day,
    )
