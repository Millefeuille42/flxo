from datetime import UTC, datetime, timedelta

import jwt
from sqlmodel import Session

from flxo.core import OAuth
from flxo.core.security import verify_password
from flxo.core.settings import Settings
from flxo.models.user import User
from flxo.services.settings import get_settings
from flxo.services.user import svc

settings: Settings = get_settings()

oauth = OAuth()
oauth.register(
    name="keycloack",
    client_id=settings.oauth.client_id,
    client_secret=settings.oauth.client_secret,
    authorize_url=settings.oauth.authorize_url,
    authorize_params={"scope": settings.oauth.scope},
    access_token_url=settings.oauth.access_token_url,
    client_kwargs={"scope": settings.oauth.scope},
    server_metadata_url=settings.oauth.metadata_url,
)


SECRET_KEY = settings.app.secret_key
ALGORITHM = settings.app.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.app.access_token_expire_minutes


def get_oauth():
    yield oauth


def create_access_token(
    data: dict, expires_delta: timedelta | None = None, auth_method: str = "oauth2"
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    to_encode.update({"auth_method": auth_method})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(session: Session, username: str, password: str) -> User | None:
    user = svc.get_user_by_username(session, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
