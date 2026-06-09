from collections.abc import Sequence

from sqlmodel import select

from flxo.api.dependencies.database import SessionDep
from flxo.models import Seat, SeatDTO
from flxo.services.base import BaseService


class SeatService(BaseService[Seat]):
    Model = Seat

    @staticmethod
    def get_by_office(
        session: SessionDep, office_id: int, offset: int = 0, limit: int = 100
    ) -> Sequence[Seat]:
        return session.exec(
            select(Seat).where(Seat.office_id == office_id).offset(offset).limit(limit)
        ).all()

    def update_seat(
        self,
        session: SessionDep,
        seat_dto: SeatDTO,
        seat: Seat,
    ) -> Seat:
        seat.name = seat_dto.name
        seat.office_id = seat_dto.office_id

        return self.update(session, seat)


svc = SeatService()
