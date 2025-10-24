from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, status, Depends

from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from flxo.core.security import verify_password
from flxo.core.settings import Settings
from flxo.models.user import User
from flxo.models.token import TokenData
from flxo.services.database import SessionDep
from flxo.services.settings import get_settings
from flxo.services.user import get_user_by_username


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
    server_metadata_url=settings.oauth.metadata_url
)

SECRET_KEY = settings.app.secret_key
ALGORITHM = settings.app.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.app.access_token_expire_minutes

def get_oauth():
    yield oauth

OAuthDep = Annotated[oauth, Depends(get_oauth)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta | None = None, auth_method: str = "oauth2"):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    to_encode.update({"auth_method": auth_method})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(session: SessionDep, username: str, password: str) -> User | bool:
    user = get_user_by_username(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_by_username(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user