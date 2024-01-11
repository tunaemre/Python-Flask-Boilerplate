from typing import Type, Dict, Any, TypeVar
import inspect

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declared_attr

from src.infrastructure.entity.base import mapper_registry


TEnum = TypeVar('TEnum', bound='BaseEnum')


@mapper_registry.as_declarative_base()
class BaseEnum:
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.table_name()

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(30), nullable=False)

    @classmethod
    def table_name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def from_dict(cls: Type[TEnum], env: Dict[str, Any]) -> TEnum:
        return cls(**env)
