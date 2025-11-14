import os

from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    TomlConfigSettingsSource,
    YamlConfigSettingsSource,
)

TOML_FILE_PATH = os.environ.get("TOML_FILE_PATH", "config.toml")
YAML_FILE_PATH = os.environ.get("YAML_FILE_PATH", "config.yaml")


class DBSettings(BaseModel):
    host: str = Field(default="localhost")
    driver: str = Field(default="postgresql")
    database: str = Field(default="flxo")
    user: str = Field(default="flxo")
    password: str = Field(default="flxo")
    port: int = Field(default=5432)


class OAuthSettings(BaseModel):
    client_id: str = Field(default="")
    client_secret: str = Field(default="")
    scope: str = Field(default="openid email profile")
    authorize_url: str = Field(default="")
    access_token_url: str = Field(default="")
    metadata_url: str = Field(default="")
    username_field: str = Field(default="preferred_username")


class AppSettings(BaseModel):
    secret_key: str = Field(default="unsecure-key")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    bind: str = Field(default="127.0.0.1")
    port: int = Field(default=8080)
    access_url: str = Field(default="http://127.0.0.1:8080")


class Settings(BaseSettings):
    db: DBSettings = Field(default=DBSettings())
    oauth: OAuthSettings = Field(default=OAuthSettings())
    app: AppSettings = Field(default=AppSettings())

    @classmethod
    def settings_customise_sources(  # type: ignore[override]
        cls, settings_cls: type[BaseSettings], **kwargs
    ) -> tuple[PydanticBaseSettingsSource, ...]:
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
