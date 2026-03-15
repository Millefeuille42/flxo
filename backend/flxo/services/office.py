from collections.abc import Sequence

from sqlalchemy.orm import selectinload
from sqlmodel import select

from flxo.api.dependencies.database import SessionDep
from flxo.models import Office, OfficeDTO
from flxo.services.base import BaseService


class OfficeService(BaseService[Office]):
    Model = Office

    @staticmethod
    def get_all_with_seats(session: SessionDep) -> Sequence[Office]:
        return session.exec(
            select(Office).options(selectinload(Office.seats))  # type: ignore[arg-type]
        ).all()

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
