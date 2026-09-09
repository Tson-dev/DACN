from typing import Optional
from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    profile_id: int
    student_code: str
    full_name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    major: Optional[str] = None
    attendance_percentage: Optional[float] = None
    study_hours_per_day: Optional[float] = None
    sleep_hours_per_day: Optional[float] = None
    social_hours_per_week: Optional[float] = None
    previous_cgpa: Optional[float] = None

    class Config:
        from_attributes = True


class AdminProfileResponse(BaseModel):
    profile_id: int
    user_id: int
    student_code: str
    full_name: str
    major: Optional[str] = None
    previous_cgpa: Optional[float] = None

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    student_code: str = Field(min_length=1)
    full_name: str = Field(min_length=1)
    gender: str = Field(pattern=r"^(Male|Female)$")
    age: int = Field(gt=0)
    major: str = Field(min_length=1)
    attendance_percentage: float = Field(ge=0, le=100)
    study_hours_per_day: float = Field(ge=0)
    sleep_hours_per_day: float = Field(ge=0)
    social_hours_per_week: float = Field(ge=0)
    previous_cgpa: float = Field(ge=0, le=4.0)
