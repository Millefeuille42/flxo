from collections.abc import Sequence

from sqlmodel import select

from flxo.api.dependencies.database import SessionDep
from flxo.models.property import Property, PropertyDTO

# from flxo.models.workplace import Property, PropertyDTO
from flxo.services.base import BaseService


class PropertyService(BaseService[Property]):
    Model = Property

    def update_property_of_seat(
        self,
        session: SessionDep,
        db_property: Property,
        property_dto: PropertyDTO,
    ) -> Property:
        db_property.value = property_dto.value
        return self.update(session, db_property)

    def create_property_of_seat(
        self, session: SessionDep, property_dto: PropertyDTO, seat_id: int
    ) -> Property:
        db_property = Property(
            seat_id=seat_id, name=property_dto.name, value=property_dto.value
        )
        return self.create(session, db_property)

    @staticmethod
    def get_properties_of_seat(session: SessionDep, seat_id: int) -> Sequence[Property]:
        query = select(Property).where(Property.seat_id == seat_id)
        return session.exec(query).all()

    @staticmethod
    def get_property_of_seat(
        session: SessionDep, seat_id: int, property_name: str
    ) -> Property | None:
        query = (
            select(Property)
            .where(Property.seat_id == seat_id)
            .where(Property.name == property_name)
        )
        return session.exec(query).first()


svc = PropertyService()
