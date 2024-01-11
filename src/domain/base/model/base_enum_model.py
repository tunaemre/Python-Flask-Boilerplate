from pydantic import BaseModel


class BaseEnumModel(BaseModel):
    id: int
