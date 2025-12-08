from authlib.integrations.starlette_client import OAuth
from fastapi import Depends

from flxo.core.security import oauth2_scheme
from flxo.services.auth import get_oauth

from typing import Annotated

TokenDep = Annotated[str, Depends(oauth2_scheme)]
OAuthDep = Annotated[OAuth, Depends(get_oauth)]
