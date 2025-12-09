from flxo.api.dependencies.database import SessionDep
from flxo.models.office import Office, OfficeDTO

# from flxo.models.workplace import Office, OfficeDTO
from flxo.services.base import BaseService


class OfficeService(BaseService[Office]):
    Model = Office

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
