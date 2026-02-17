import os
from ipaddress import IPv4Address
from typing import Callable, Any, Annotated, List

from pydantic import BaseModel, Field,BeforeValidator, HttpUrl, AfterValidator, TypeAdapter
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    TomlConfigSettingsSource,
    YamlConfigSettingsSource,
)

TOML_FILE_PATH = os.environ.get("TOML_FILE_PATH", "config.toml")
YAML_FILE_PATH = os.environ.get("YAML_FILE_PATH", "config.yaml")


def strip_whitespace(v: Any) -> Any:
    if isinstance(v, str):
        return v.strip()
    return v


def validate_and_stringify_url(v: Any) -> str:
    if not v: return ""
    adapter = TypeAdapter(HttpUrl)
    url_obj = adapter.validate_python(v)
    return str(url_obj).rstrip("/")


def split_list(sep: str = ',') -> Callable[[Any], Any]:
    def wrapped(v: Any) -> Any:
        if isinstance(v, str):
            return filter(None, [item for item in v.split(sep)])
        return v
    return wrapped


def validate_port(v: Any) -> Any:
    value = int(v)
    if not (1 <= value <= 65535):
        raise ValueError("port must be between 1 and 65535")
    return value


StrippedStr = Annotated[str, BeforeValidator(strip_whitespace)]
UrlStr = Annotated[str,
    BeforeValidator(strip_whitespace),
    AfterValidator(validate_and_stringify_url)
]
Port = Annotated[int, AfterValidator(validate_port)]
ScopeList = Annotated[List[StrippedStr], BeforeValidator(split_list(' '))]
UrlList = Annotated[List[UrlStr], BeforeValidator(split_list(','))]

class DBSettings(BaseModel):
    host: StrippedStr = Field(default="localhost")
    driver: StrippedStr = Field(default="postgresql")
    database: StrippedStr = Field(default="flxo")
    user: StrippedStr = Field(default="flxo")
    password: StrippedStr = Field(default="flxo")
    port: Port = Field(default=5432)


class OAuthSettings(BaseModel):
    client_id: StrippedStr = Field(default="")
    client_secret: StrippedStr = Field(default="")
    scope: ScopeList = Field(default="openid email profile")
    authorize_url: UrlStr = Field(default="")
    access_token_url: UrlStr = Field(default="")
    metadata_url: UrlStr = Field(default="")
    username_field: StrippedStr = Field(default="preferred_username")
    redirect_url: UrlStr = Field(default="http://localhost:5173")


class AppSettings(BaseModel):
    secret_key: StrippedStr = Field(default="unsecure-key")
    algorithm: StrippedStr = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    bind: IPv4Address = Field(default="127.0.0.1")
    port: Port = Field(default=8080)
    access_url: UrlStr = Field(default="http://127.0.0.1:8080")
    allowed_origins: UrlList = Field(default="http://localhost:5173")


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
