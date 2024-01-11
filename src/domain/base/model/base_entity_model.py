from datetime import datetime
from typing import Optional, TypeVar

from pydantic import BaseModel, Field, BaseConfig

from src.domain.common.factory.datetime import datetime_factory
from src.domain.common.factory.uuid import id_factory


class BaseEntityModel(BaseModel):
    id: str = Field(default_factory=id_factory)
    created_date: datetime = Field(default_factory=datetime_factory)
    modified_date: Optional[datetime] = None

    class Config(BaseConfig):
        orm_mode = True


EType = TypeVar('EType', bound=BaseEntityModel)
