from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey
from datetime import datetime, timezone

from backend.database import Base


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    history_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    target_gpa = Column(Float, nullable=False)
    predicted_gpa = Column(Float, nullable=False)
    success_probability = Column(Float, nullable=False)
    similar_student_count = Column(Integer, nullable=False)
    prediction_date = Column(Date, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
