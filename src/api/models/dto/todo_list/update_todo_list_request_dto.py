from pydantic import BaseModel, Field


class UpdateTodoListRequestDto(BaseModel):
    name: str = Field(max_length=50)
    status_id: int
