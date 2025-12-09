from collections.abc import Sequence

from sqlmodel import SQLModel, select

from flxo.api.dependencies.database import SessionDep

from typing import ClassVar


class BaseService[ModelType: SQLModel]:
    Model: ClassVar[type[SQLModel]]

    @classmethod
    def get_all(
        cls, session: SessionDep, offset: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        return session.exec(select(cls.Model).offset(offset).limit(limit)).all()

    @classmethod
    def get(cls, session: SessionDep, object_id: int) -> ModelType | None:
        return session.get(cls.Model, object_id)

    @classmethod
    def update(cls, session: SessionDep, instance: ModelType) -> ModelType:
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return instance

    @classmethod
    def create(cls, session: SessionDep, instance: ModelType) -> ModelType:
        return cls.create(session, instance)

    @classmethod
    def delete(cls, session: SessionDep, instance: ModelType) -> None:
        session.delete(instance)
        session.commit()
