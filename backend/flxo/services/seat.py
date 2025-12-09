from flxo.api.dependencies.database import SessionDep
from flxo.models.seat import Seat, SeatDTO

# from flxo.models.workplace import Seat, SeatDTO
from flxo.services.base import BaseService


class SeatService(BaseService[Seat]):
    Model = Seat

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
