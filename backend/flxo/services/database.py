from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from flxo.core.settings import DBSettings
from flxo.services.settings import get_settings

from typing import Annotated

db: DBSettings = get_settings().db

DATABASE_URL = f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.database}"
if db.driver == "sqlite":
    DATABASE_URL = f"sqlite:///{db.host}"
engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
