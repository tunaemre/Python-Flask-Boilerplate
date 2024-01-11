from datetime import datetime
from typing import List, Optional, Type, Callable, Generic

from redis import Redis
from sqlalchemy import func
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql import operators

from src.domain.base.model.base_entity_model import EType
from src.infrastructure.entity.base.base_entity import BaseEntity
from src.infrastructure.manager.redis_manager import RedisManager


class _QueryExtension:
    def __init__(self, query: Query) -> None:
        self.query = query

    def count(self) -> int:
        q = self.query.statement.with_only_columns([func.count()])
        return self.query.session.execute(q).scalar()

    def exists(self) -> bool:
        return self.query.session.query(self.query.exists()).scalar()


class RedisRepository:
    @property
    def redis(self) -> Redis:  # type: ignore
        return RedisManager.get_redis()


class BaseRepository(Generic[EType]):
    def __init__(self, entity_type: Type[BaseEntity], session_callable: Callable[..., Session]) -> None:
        self.entity_type = entity_type
        self.session_callable = session_callable

    @property
    def session(self) -> Session:
        return self.session_callable()

    @property
    def query(self, *entity_type: Type[BaseEntity]) -> Query:
        if not entity_type:
            return self.session.query(self.entity_type)
        else:
            return self.session.query(*entity_type)

    def apply(self, query: Query) -> _QueryExtension:
        return _QueryExtension(query)

    def commit(self) -> None:
        self.session.commit()

    def insert(self, entity: EType) -> None:
        instance = self.entity_type.from_model(entity)
        self.session.add(instance)

    def insert_many(self, *entity: EType) -> None:
        if not entity:
            return
        instances = [self.entity_type.from_model(e) for e in entity]
        self.session.add_all(instances)

    def update(self, entity: EType) -> None:
        instance = self.entity_type.from_model(entity)
        instance.modified_date = datetime.utcnow()
        self.session.merge(instance)

    def update_many(self, *entity: EType) -> None:
        if not entity:
            return
        for e in entity:
            instance = self.entity_type.from_model(e)
            instance.modified_date = datetime.utcnow()
            self.session.merge(instance)

    def delete(self, entity_id: str) -> None:
        self.query.filter(self.entity_type.id == entity_id).delete(synchronize_session=False)

    def delete_many(self, *entity_id: str) -> None:
        if not entity_id:
            return
        self.query.filter(operators.in_op(self.entity_type.id, entity_id)).delete(synchronize_session=False)

    def get(self, entity_id: str) -> Optional[EType]:
        instance = self.session.get(self.entity_type, entity_id)
        if not instance:
            return None
        t: Type[EType] = self.entity_type.domain_model()
        return t.from_orm(instance)

    def get_many(self, *entity_id: str) -> Optional[List[EType]]:
        if not entity_id:
            return None
        instances = self.query.filter(operators.in_op(self.entity_type.id, entity_id)).all()
        t: Type[EType] = self.entity_type.domain_model()
        return [t.from_orm(instance) for instance in instances]

    def all(self) -> List[EType]:
        instances = self.query.all()
        t: Type[EType] = self.entity_type.domain_model()
        return [t.from_orm(instance) for instance in instances]
