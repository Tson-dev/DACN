from sqlalchemy import Column, Integer, String, Float, ForeignKey

from backend.database import Base


class StudentProfile(Base):
    __tablename__ = "student_profile"

    profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), unique=True, nullable=False)
    student_code = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    gender = Column(String(20))
    age = Column(Integer)
    major = Column(String(100))
    attendance_percentage = Column(Float)
    study_hours_per_day = Column(Float)
    sleep_hours_per_day = Column(Float)
    social_hours_per_week = Column(Float)
    previous_cgpa = Column(Float)
