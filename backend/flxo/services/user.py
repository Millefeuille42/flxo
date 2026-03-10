from sqlmodel import select, Session

from flxo.core.security import get_password_hash
from flxo.models.presence import Presence
from flxo.models.user import User, UserDTO, UserPublic
from flxo.services.base import BaseService


class UserService(BaseService[User]):
    Model = User

    def update_user(self, session: Session, user_dto: UserDTO, user: User) -> User:
        user.username = user_dto.username
        return self.update(session, user)

    def update_profile(
        self, session: Session, user: User, favorite_seat_id: int | None
    ) -> User:
        user.favorite_seat_id = favorite_seat_id
        return self.update(session, user)

    def get_user_by_id(self, session: Session, user_id: int) -> User | None:
        return self.get(session, user_id)

    @staticmethod
    def get_user_by_username(session: Session, username: str) -> User | None:
        return session.exec(select(User).where(User.username == username)).first()

    def create_user_from_dto(self, session: Session, user: UserDTO) -> User:
        user.hashed_password = get_password_hash(user.password)
        db_user = User.model_validate(user)
        return self.create(session, db_user)

    def create_user_with_username(self, session: Session, username: str) -> User:
        return self.create(session, User(username=username))

    def delete_user(self, session: Session, user: User) -> None:
        presences = session.exec(
            select(Presence).where(Presence.user_id == user.id)
        ).all()
        for presence in presences:
            session.delete(presence)
        session.flush()
        self.delete(session, user)

    def get_or_create_user(self, session: Session, username: str) -> User:
        user = self.get_user_by_username(session, username)
        if not user:
            user = self.create_user_with_username(session, username)
        return user


svc = UserService()
