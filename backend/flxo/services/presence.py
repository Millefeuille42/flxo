from collections.abc import Sequence
from datetime import datetime

from ics import Calendar, Event
from sqlmodel import Session, select

from flxo.models.presence import Presence, PresenceDTO
from flxo.services.base import BaseService

from typing import Any


class PresenceService(BaseService[Presence]):
    Model = Presence

    def update_presence(
        self, session: Session, presence_dto: PresenceDTO, presence: Presence
    ) -> Presence:
        presence.start = presence_dto.start
        presence.end = presence_dto.end
        return self.update(session, presence)

    def create_presence(
        self, session: Session, presence: PresenceDTO, user_id: int
    ) -> Presence:
        db_presence = Presence(
            user_id=user_id,
            start=presence.start,
            end=presence.end,
        )
        return self.create(session, db_presence)

    @staticmethod
    def get_all_presences(
        session: Session,
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
        self,
        session: Session,
        user_id: int,
        start: datetime | None = None,
        end: datetime | None = None,
        offset: int = 100,
        limit: int = 100,
    ) -> Sequence[Presence]:
        return self.get_all_presences(
            session,
            start,
            end,
            offset,
            limit,
            select(Presence).where(Presence.user_id == user_id),
        )

    @staticmethod
    def get_presence(
        session: Session,
        presence_id: int,
        user_id: int,
    ) -> Presence | None:
        return session.exec(
            select(Presence)
            .where(Presence.id == presence_id)
            .where(Presence.user_id == user_id)
        ).first()

    @staticmethod
    def does_presence_overlap(
        session: Session,
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

    @staticmethod
    def presences_to_ics(
        presences: Sequence[Presence], all_day: bool = False
    ) -> Calendar:
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
        self,
        session: Session,
        start: datetime | None = None,
        end: datetime | None = None,
        offset: int = 100,
        limit: int = 100,
        all_day: bool = False,
    ) -> Calendar:
        return self.presences_to_ics(
            self.get_all_presences(session, start, end, offset, limit), all_day
        )

    def get_all_presences_of_user_as_ics(
        self,
        session: Session,
        user_id: int,
        start: datetime | None = None,
        end: datetime | None = None,
        offset: int = 100,
        limit: int = 100,
        all_day: bool = False,
    ) -> Calendar:
        return self.presences_to_ics(
            self.get_all_presences(
                session,
                start,
                end,
                offset,
                limit,
                select(Presence).where(Presence.user_id == user_id),
            ),
            all_day,
        )


svc = PresenceService()
