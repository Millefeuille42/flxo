from sqlmodel import Session, select

from flxo.core.security import get_password_hash
from flxo.models.user import User, UserDTO


def get_user_by_username(session: Session, username: str) -> User | None:
    return session.exec(select(User).where(User.username == username)).first()


def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def create_user(session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_user_from_dto(session: Session, user: UserDTO) -> User:
    user.hashed_password = get_password_hash(user.password)
    db_user = User.model_validate(user)
    return create_user(session, db_user)


def create_user_with_username(session: Session, username: str) -> User:
    return create_user(session, User(username=username))


def get_or_create_user(session: Session, username: str) -> User:
    user = get_user_by_username(session, username)
    if not user:
        user = create_user_with_username(session, username)
    return user
