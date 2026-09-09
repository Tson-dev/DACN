from sqlalchemy.orm import Session

from backend.models.student_profile import StudentProfile


def get_profile_by_user_id(db: Session, user_id: int) -> StudentProfile | None:
    return db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()


def get_profile_by_id(db: Session, profile_id: int) -> StudentProfile | None:
    return db.query(StudentProfile).filter(StudentProfile.profile_id == profile_id).first()


def get_all_profiles(db: Session) -> list[StudentProfile]:
    return db.query(StudentProfile).order_by(StudentProfile.profile_id).all()


def create_student_profile(db: Session, user_id: int) -> StudentProfile:
    profile = StudentProfile(
        user_id=user_id,
        student_code="PENDING",
        full_name="Not Set",
        gender=None,
        age=0,
        major=None,
        attendance_percentage=0.0,
        study_hours_per_day=0.0,
        sleep_hours_per_day=0.0,
        social_hours_per_week=0.0,
        previous_cgpa=0.0,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(db: Session, profile: StudentProfile, data: dict) -> StudentProfile:
    for key, value in data.items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile
