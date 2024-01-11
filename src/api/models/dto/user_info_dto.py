from pydantic import BaseModel, Field


class UserInfoResponseDto(BaseModel):
    sub: str = Field(max_length=50)
    email: str = Field(max_length=320)
