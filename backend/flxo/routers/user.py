from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from flxo.models.user import UserPublic, UserDTO
from flxo.services.auth import get_current_user
from flxo.services.database import SessionDep
from flxo.services.user import create_user_from_dto

router = APIRouter(prefix="/user")

@router.get("/me", response_model=UserPublic)
async def get_self(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/", response_model=UserPublic)
async def create_user_route(user: UserDTO, session: SessionDep) -> UserPublic:
    return create_user_from_dto(session, user)
