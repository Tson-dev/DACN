import logging
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models.role import Role
from backend.models.user import User
from backend.models.student_profile import StudentProfile
from backend.services.auth_service import hash_password

logger = logging.getLogger(__name__)


def seed_data(db: Session):
    existing_roles = db.query(Role).count()
    if existing_roles == 0:
        db.add_all([
            Role(name="ADMIN", desc="System administrator"),
            Role(name="STUDENT", desc="Student user"),
        ])
        db.commit()
        logger.info("Roles seeded: ADMIN, STUDENT")

    admin_role = db.query(Role).filter(Role.name == "ADMIN").first()
    existing_admin = db.query(User).filter(User.username == settings.DEFAULT_ADMIN_USERNAME).first()
    if not existing_admin and admin_role:
        admin = User(
            role_id=admin_role.role_id,
            username=settings.DEFAULT_ADMIN_USERNAME,
            password_hash=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
            status="ACTIVE",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info(f"Admin user created: {settings.DEFAULT_ADMIN_USERNAME}")
