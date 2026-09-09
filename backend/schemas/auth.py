from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginData(BaseModel):
    user_id: int
    username: str
    role: str
