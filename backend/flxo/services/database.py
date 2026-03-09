from collections.abc import Generator

from sqlalchemy.pool import StaticPool
from sqlmodel import create_engine, Session, SQLModel

from flxo.core.settings import DBSettings
from flxo.services.settings import get_settings


db: DBSettings = get_settings().db


def get_engine_args(driver: str) -> dict:
    """Get database-specific engine configuration arguments.

    Args:
        driver: Database driver name ("postgresql" or "sqlite")

    Returns:
        Dictionary of engine arguments to pass to create_engine()
    """
    if driver == "sqlite":
        # SQLite-specific configuration
        return {
            "connect_args": {"check_same_thread": False},  # Required for FastAPI
            "poolclass": StaticPool,  # Use static pool for SQLite
        }
    if driver == "postgresql":
        # PostgreSQL uses default connection pooling
        # Check if psycopg2 is available
        try:
            import psycopg2  # noqa: F401
        except ImportError as e:
            msg = (
                "PostgreSQL driver (psycopg2-binary) is not installed. "
                "Install it with: uv sync --extra postgresql"
            )
            raise ImportError(msg) from e
        return {}
    msg = f"Unsupported database driver: {driver}"
    raise ValueError(msg)


def get_database_url(db_settings: DBSettings) -> str:
    """Construct database URL from settings.

    Args:
        db_settings: Database configuration settings

    Returns:
        Database connection URL string
    """
    if db_settings.driver == "sqlite":
        # Support relative paths, absolute paths, and :memory:
        return f"sqlite:///{db_settings.host}"
    if db_settings.driver == "postgresql":
        return (
            f"postgresql://{db_settings.user}:{db_settings.password}"
            f"@{db_settings.host}:{db_settings.port}/{db_settings.database}"
        )
    msg = f"Unsupported database driver: {db_settings.driver}"
    raise ValueError(msg)


DATABASE_URL = get_database_url(db)
engine = create_engine(DATABASE_URL, **get_engine_args(db.driver))


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session
