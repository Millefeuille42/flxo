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
    def get_config_list(
        session: SessionDep, offset: int = 0, limit: int = 100
    ) -> Sequence[dict]:
        results = session.exec(
            select(  # type: ignore[arg-type]
                Office.id,
                Office.name,
                Office.address,
                Office.properties,
                func.count(Seat.id).label("desk_count"),
            )
            .outerjoin(Seat, Office.id == Seat.office_id)
            .group_by(Office.id)
            .offset(offset)
            .limit(limit)
        ).all()
        return [
            {
                "id": row.id,
                "name": row.name,
                "address": row.address,
                "logo_url": (row.properties or {}).get("logo_url", ""),
                "floor_plan_url": (row.properties or {}).get("floor_plan_url", ""),
                "desk_count": row.desk_count,
            }
            for row in results
        ]

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
