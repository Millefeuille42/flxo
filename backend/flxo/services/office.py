from collections.abc import Sequence

from sqlalchemy import func
from sqlmodel import select

from flxo.api.dependencies.database import SessionDep
from flxo.models import Office, OfficeDTO
from flxo.models.seat import Seat
from flxo.services.base import BaseService


class OfficeService(BaseService[Office]):
    Model = Office

    @staticmethod
    def get_all_with_seat_count(
        session: SessionDep, offset: int = 0, limit: int = 100
    ) -> Sequence[tuple[Office, int]]:
        results = session.exec(
            select(Office, func.count(Seat.id).label("desk_count"))  # type: ignore[arg-type]
            .outerjoin(Seat, Office.id == Seat.office_id)
            .group_by(Office.id)
            .offset(offset)
            .limit(limit)
        ).all()
        return [(office, count) for office, count in results]

    def update_office(
        self,
        session: SessionDep,
        office_dto: OfficeDTO,
        office: Office,
    ) -> Office:
        office.name = office_dto.name
        office.address = office_dto.address

        return self.update(session, office)


svc = OfficeService()
