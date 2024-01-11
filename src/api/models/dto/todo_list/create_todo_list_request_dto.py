from pydantic import BaseModel, Field


class CreateTodoListRequestDto(BaseModel):
    name: str = Field(max_length=50)

