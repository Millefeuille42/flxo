from fastapi import Depends
from sqlmodel import Session

from flxo.services.database import get_session

from typing import Annotated

SessionDep = Annotated[Session, Depends(get_session)]
