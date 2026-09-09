from typing import Optional
from pydantic import BaseModel, Field

from backend.config import settings


class PredictionRequest(BaseModel):
    target_gpa: float = Field(gt=settings.TARGET_GPA_MIN, le=settings.TARGET_GPA_MAX)


class PredictionData(BaseModel):
    predicted_gpa: float
    target_gpa: float
    success_probability: float
    similar_student_count: int


class PredictionHistoryData(PredictionData):
    prediction_date: str
