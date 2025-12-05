from functools import lru_cache

from fastapi import Depends

from flxo.core.settings import Settings

from typing import Annotated


@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
