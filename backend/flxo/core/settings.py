from collections.abc import Callable
from ipaddress import IPv4Address
import os

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    Field,
    HttpUrl,
    TypeAdapter,
)
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    TomlConfigSettingsSource,
    YamlConfigSettingsSource,
)

from typing import Annotated


TOML_FILE_PATH = os.environ.get("TOML_FILE_PATH", "config.toml")
YAML_FILE_PATH = os.environ.get("YAML_FILE_PATH", "config.yaml")


def strip_whitespace(v: str) -> str:
    if isinstance(v, str):
        return v.strip()
    return v


def validate_and_stringify_url(v: str) -> str:
    if not v:
        return ""
    adapter = TypeAdapter(HttpUrl)
    url_obj = adapter.validate_python(v)
    return str(url_obj).rstrip("/")


def split_list(sep: str = ",") -> Callable[[str], list[str]]:
    def wrapped(v: str) -> list[str]:
        return list(filter(None, v.split(sep)))

    return wrapped


def validate_port(v: int) -> int:
    value = int(v)
    if not (1 <= value <= 65535):
        raise ValueError("port must be between 1 and 65535")
    return value


StrippedStr = Annotated[str, BeforeValidator(strip_whitespace)]
UrlStr = Annotated[
    str, BeforeValidator(strip_whitespace), AfterValidator(validate_and_stringify_url)
]
Port = Annotated[int, AfterValidator(validate_port)]
ScopeList = Annotated[list[StrippedStr], BeforeValidator(split_list(" "))]
UrlList = Annotated[list[UrlStr], BeforeValidator(split_list(","))]


class DBSettings(BaseModel):
    host: StrippedStr = Field(default="flxo.db")
    driver: StrippedStr = Field(default="sqlite")
    database: StrippedStr = Field(default="flxo")
    user: StrippedStr = Field(default="flxo")
    password: StrippedStr = Field(default="flxo")
    port: Port = Field(default=5432)


class OAuthSettings(BaseModel):
    client_id: StrippedStr = Field(default="")
    client_secret: StrippedStr = Field(default="")
    scope: ScopeList = Field(default="openid email profile")  # type: ignore
    authorize_url: UrlStr = Field(default="")
    access_token_url: UrlStr = Field(default="")
    metadata_url: UrlStr = Field(default="")
    username_field: StrippedStr = Field(default="preferred_username")
    redirect_url: UrlStr = Field(default="http://localhost:5173")


class AppSettings(BaseModel):
    secret_key: StrippedStr = Field(default="unsecure-key")
    algorithm: StrippedStr = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    bind: IPv4Address = Field(default="127.0.0.1")  # type: ignore
    port: Port = Field(default=8080)
    access_url: UrlStr = Field(default="http://127.0.0.1:8080")
    allowed_origins: UrlList = Field(default="http://localhost:5173")  # type: ignore


class TimeSettings(BaseModel):
    morning_start: str = Field(default="08:00")
    morning_end: str = Field(default="12:00")
    afternoon_start: str = Field(default="13:00")
    afternoon_end: str = Field(default="17:00")


class Settings(BaseSettings):
    db: DBSettings = Field(default=DBSettings())
    oauth: OAuthSettings = Field(default=OAuthSettings())
    app: AppSettings = Field(default=AppSettings())
    time: TimeSettings = Field(default=TimeSettings())

    @classmethod
    def settings_customise_sources(  # type: ignore[override]
        cls, settings_cls: type[BaseSettings], **_kwargs: object
    ) -> tuple[PydanticBaseSettingsSource, ...]:
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
