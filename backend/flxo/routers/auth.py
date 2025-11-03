from datetime import timedelta

from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request

from flxo.models.token import Token
from flxo.services.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    OAuthDep,
    authenticate_user,
    create_access_token,
)
from flxo.services.database import SessionDep
from flxo.services.settings import SettingsDep
from flxo.services.user import get_or_create_user

from typing import Annotated

router = APIRouter(prefix="/auth")


@router.get("/oauth2")
async def auth_oauth(request: Request, oauth: OAuthDep, settings: SettingsDep):
    return await oauth.keycloack.authorize_redirect(
        request,
        redirect_uri=f"{settings.app.access_url}/auth/oauth2/callback"
    )


@router.get("/oauth2/callback")
async def oauth_callback(
    request: Request, oauth: OAuthDep, settings: SettingsDep, session: SessionDep
):
    try:
        token = await oauth.keycloack.authorize_access_token(request)
    except OAuthError as e:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e.error}: {e.description}"
        )
    user = get_or_create_user(
        session,
        token.get("userinfo").get(settings.oauth.username_field)
    )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.app.access_token_expire_minutes),
        auth_method="oauth2"
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(
        access_token=access_token,
        # ruff: noqa: S106
        token_type="bearer"
    )
