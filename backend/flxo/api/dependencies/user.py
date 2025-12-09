import jwt
from authlib.integrations.base_client import InvalidTokenError
from fastapi import Depends

from flxo.api.dependencies.auth import TokenDep
from flxo.api.dependencies.database import SessionDep
from flxo.core.exceptions import InvalidCredentialsException
from flxo.models.token import TokenData
from flxo.models.user import User, UserPublic
from flxo.services.auth import ALGORITHM, SECRET_KEY
from flxo.services.user import svc

from typing import Annotated


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise InvalidCredentialsException
        token_data = TokenData(username=username)
    except InvalidTokenError as e:
        raise InvalidCredentialsException from e
    user = svc.get_user_by_username(session, username=token_data.username)
    if user is None:
        raise InvalidCredentialsException
    return user


UserDep = Annotated[UserPublic, Depends(get_current_user)]
