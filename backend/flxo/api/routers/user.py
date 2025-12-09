from fastapi import APIRouter, HTTPException

from flxo.api.dependencies.database import SessionDep
from flxo.api.dependencies.user import UserDep
from flxo.models.user import UserDTO, UserPublic
from flxo.services.user import svc

router = APIRouter(prefix="/user")


@router.get("/me", response_model=UserPublic)
async def get_self(current_user: UserDep):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/", response_model=UserPublic)
async def create_user_route(user: UserDTO, session: SessionDep) -> UserPublic:
    return svc.create_user_from_dto(session, user)
