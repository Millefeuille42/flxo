from fastapi import APIRouter, HTTPException

from flxo.api.dependencies.database import SessionDep
from flxo.api.dependencies.user import UserDep
from flxo.models import UserDTO, UserPublic
from flxo.services.user import svc

router = APIRouter(prefix="/user")


@router.get("/me", response_model=UserPublic)
async def get_self(current_user: UserDep):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
