from typing import Any, List, Optional
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    field: str
    message: str


class StandardResponse(BaseModel):
    success: bool
    message: str = ""
    data: Any = None
    errors: Optional[List[ErrorDetail]] = None
