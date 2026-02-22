from collections.abc import Sequence

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from flxo.api.dependencies.database import SessionDep
from flxo.api.dependencies.settings import SettingsDep
from flxo.api.dependencies.user import UserDep
from flxo.models.user import UserDTO, UserPublic
from flxo.services.user import svc

from typing import Annotated


def require_no_sso(settings: SettingsDep) -> None:
    if settings.oauth.client_id:
        raise HTTPException(status_code=403, detail="Non disponible en mode SSO")


router = APIRouter(prefix="/user")


class UserProfileUpdate(BaseModel):
    comment: str = ""
    desk_preference_id: int | None = None


@router.get("/", response_model=Sequence[UserPublic])
async def list_users(
    _current_user: UserDep,
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=200)] = 200,
) -> Sequence[UserPublic]:
    return svc.get_all(session, offset, limit)


@router.get("/me", response_model=UserPublic)
async def get_self(current_user: UserDep) -> UserPublic:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.put("/me", response_model=UserPublic)
async def update_self(
    current_user: UserDep,
    profile: UserProfileUpdate,
    session: SessionDep,
) -> UserPublic:
    return svc.update_profile(
        session,
        current_user,  # type: ignore
        profile.comment,
        profile.desk_preference_id,
    )


@router.post("/", response_model=UserPublic, dependencies=[Depends(require_no_sso)])
async def create_user_route(user: UserDTO, session: SessionDep) -> UserPublic:
    return svc.create_user_from_dto(session, user)


@router.delete("/{user_id}", dependencies=[Depends(require_no_sso)])
async def delete_user_route(
    current_user: UserDep,
    user_id: int,
    session: SessionDep,
):
    if user_id == current_user.id:
        msg = "Vous ne pouvez pas vous supprimer vous-même"
        raise HTTPException(status_code=400, detail=msg)
    user = svc.get(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    svc.delete_user(session, user)
    return {"ok": True}
