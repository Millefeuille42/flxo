from fastapi import Depends

from flxo.services.settings import get_settings, Settings

from typing import Annotated


SettingsDep = Annotated[Settings, Depends(get_settings)]
