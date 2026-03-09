from collections.abc import Sequence
import datetime
import time

from ics import Calendar, Event
from sqlmodel import or_, select, Session

from flxo.models.presence import Presence, PresenceDTO
from flxo.services.base import BaseService
from flxo.services.settings import get_settings

from typing import Any


def _str_to_time(v: str) -> time.struct_time:
    try:
        return time.strptime(v, "%H:%M")
    except ValueError as e:
        raise ValueError("time slot must be in HH:MM format") from e


class PresenceService(BaseService[Presence]):
    Model = Presence

    def update_presence(
        self, session: Session, presence_dto: PresenceDTO, presence: Presence
    ) -> Presence:
        presence.date = presence_dto.date
        presence.slot = presence_dto.slot
        presence.state = presence_dto.state
        presence.seat_id = presence_dto.seat_id
        presence.office_id = presence_dto.office_id
        return self.update(session, presence)

    def create_presence(
        self, session: Session, presence: PresenceDTO, user_id: int
    ) -> Presence:
        db_presence = Presence(
            user_id=user_id,
            office_id=presence.office_id,
            seat_id=presence.seat_id,
            date=presence.date,
            slot=presence.slot,
            state=presence.state,
        )
        return self.create(session, db_presence)

    @staticmethod
    def get_all_presences(
        session: Session,
        date_from: datetime.date | None = None,
        date_to: datetime.date | None = None,
        offset: int = 0,
        limit: int = 100,
        query: Any = None,  # noqa: ANN401
    ) -> Sequence[Presence]:
        if not query:
            query = select(Presence)
        if date_from:
            query = query.where(Presence.date >= date_from)
        if date_to:
            query = query.where(Presence.date <= date_to)
        query = query.offset(offset).limit(limit)
        return session.exec(query).all()

    def get_all_presences_of_user(
        self,
        session: Session,
        user_id: int,
        date_from: datetime.date | None = None,
        date_to: datetime.date | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Presence]:
        return self.get_all_presences(
            session,
            date_from,
            date_to,
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
        seat_id: int,
        presence_date: datetime.date,
        slot: str,
        presence_id: int | None = None,
    ) -> bool:
        query = select(Presence).where(
            or_(Presence.user_id == user_id, Presence.seat_id == seat_id)
        )
        if presence_id:
            query = query.where(Presence.id != presence_id)
        query = query.where(Presence.date == presence_date).where(Presence.slot == slot)
        return session.exec(query).first() is not None

    @staticmethod
    def _slot_to_times(slot: str) -> tuple[datetime.time, datetime.time]:
        time_settings = get_settings().time
        morning_start = _str_to_time(time_settings.morning_start)
        morning_end = _str_to_time(time_settings.morning_end)
        afternoon_start = _str_to_time(time_settings.afternoon_start)
        afternoon_end = _str_to_time(time_settings.afternoon_end)
        return (
            (
                datetime.time(
                    morning_start.tm_hour,
                    morning_start.tm_min,
                ),
                datetime.time(morning_end.tm_hour, morning_end.tm_min),
            )
            if slot == "morning"
            else (
                datetime.time(
                    afternoon_start.tm_hour,
                    afternoon_start.tm_min,
                ),
                datetime.time(
                    afternoon_end.tm_hour,
                    afternoon_end.tm_min,
                ),
            )
        )

    @classmethod
    def presences_to_ics(
        cls, presences: Sequence[Presence], *, is_all_day: bool = False
    ) -> Calendar:
        c = Calendar()
        for presence in presences:
            e = Event()
            start_time, end_time = cls._slot_to_times(presence.slot)
            e.begin = datetime.datetime.combine(presence.date, start_time)
            e.end = datetime.datetime.combine(presence.date, end_time)
            if is_all_day:
                e.make_all_day()
            e.name = f"{presence.user.username} - {presence.office.name}"
            e.location = presence.office.address
            e.description = f"ID: {presence.id}"
            e.description += f"\nSeat: {presence.seat.name}"
            c.events.add(e)
        return c

    def get_all_presences_as_ics(
        self,
        session: Session,
        date_from: datetime.date | None = None,
        date_to: datetime.date | None = None,
        offset: int = 0,
        limit: int = 100,
        *,
        is_all_day: bool = False,
    ) -> Calendar:
        return self.presences_to_ics(
            self.get_all_presences(session, date_from, date_to, offset, limit),
            is_all_day=is_all_day,
        )

    def get_all_presences_of_user_as_ics(
        self,
        session: Session,
        user_id: int,
        date_from: datetime.date | None = None,
        date_to: datetime.date | None = None,
        offset: int = 0,
        limit: int = 100,
        *,
        is_all_day: bool = False,
    ) -> Calendar:
        return self.presences_to_ics(
            self.get_all_presences(
                session,
                date_from,
                date_to,
                offset,
                limit,
                select(Presence).where(Presence.user_id == user_id),
            ),
            is_all_day=is_all_day,
        )


svc = PresenceService()
