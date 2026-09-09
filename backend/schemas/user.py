from typing import Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)
    role: str = Field(pattern=r"^(ADMIN|STUDENT)$")


class UserResponse(BaseModel):
    user_id: int
    username: str
    role: str
    status: str
    created_at: str

    class Config:
        from_attributes = True
