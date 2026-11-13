from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, skip: int = 0, limit: int = 100) -> list[ModelT]:
        return list(self.db.scalars(select(self.model).offset(skip).limit(limit)).all())

    def get(self, entity_id: int) -> ModelT | None:
        return self.db.get(self.model, entity_id)

    def add(self, entity: ModelT) -> ModelT:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: ModelT, values: dict) -> ModelT:
        for field, value in values.items():
            setattr(entity, field, value)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        self.db.delete(entity)
        self.db.commit()
