from typing import Type, TypeVar

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declared_attr

from src.domain.base.model.base_entity_model import EType
from src.infrastructure.entity.base import mapper_registry

TEntity = TypeVar('TEntity', bound='BaseEntity')


@mapper_registry.as_declarative_base()
class BaseEntity:
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.table_name()

    id = Column(String(36), primary_key=True, nullable=False)
    created_date = Column(DateTime, nullable=False)
    modified_date = Column(DateTime, nullable=True)

    @classmethod
    def table_name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def domain_model(cls: Type[TEntity]) -> Type[EType]:
        raise NotImplementedError

    @classmethod
    def from_model(cls: Type[TEntity], obj: EType) -> TEntity:
        d = obj.dict()
        return cls(**d)
