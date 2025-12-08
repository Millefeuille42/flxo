from fastapi import Depends

from flxo.services.settings import Settings, get_settings

from typing import Annotated

SettingsDep = Annotated[Settings, Depends(get_settings)]
