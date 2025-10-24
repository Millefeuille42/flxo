import os
from typing import Tuple, Type

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, TomlConfigSettingsSource, PydanticBaseSettingsSource, EnvSettingsSource, \
    YamlConfigSettingsSource

TOML_FILE_PATH = os.environ.get("TOML_FILE_PATH", "config.toml")
YAML_FILE_PATH = os.environ.get("YAML_FILE_PATH", "config.yaml")

class DBSettings(BaseModel):
    host: str = Field(default="localhost")
    database: str = Field(default="flxo")
    user: str = Field(default="flxo")
    password: str = Field(default="flxo")
    port: int = Field(default=5432)

class OAuthSettings(BaseModel):
    client_id: str = Field()
    client_secret: str = Field()
    scope: str = Field(default="openid email profile")
    authorize_url: str = Field()
    access_token_url: str = Field()
    metadata_url: str = Field()
    username_field: str = Field(default="preferred_username")

class AppSettings(BaseModel):
    secret_key: str = Field()
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    access_url: str = Field(default="http://localhost:8002")


class Settings(BaseSettings):
    db: DBSettings = Field(default=DBSettings())
    oauth: OAuthSettings = Field()
    app: AppSettings = Field()

    @classmethod
    def settings_customise_sources(
        cls, settings_cls: Type[BaseSettings], **kwargs
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        global TOML_FILE_PATH

        return (
            EnvSettingsSource(
                settings_cls,
                env_prefix="FLXO__",
                env_nested_delimiter="__",
                case_sensitive=False,
            ),
            TomlConfigSettingsSource(settings_cls, toml_file=TOML_FILE_PATH),
            YamlConfigSettingsSource(settings_cls, yaml_file=YAML_FILE_PATH),
        )
