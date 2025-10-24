from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from flxo.core.settings import Settings

@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
