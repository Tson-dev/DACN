from sqlalchemy.orm import Session

from backend.models.user import User


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.user_id == user_id).first()


def get_all_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.user_id).all()


def create_user(db: Session, username: str, password_hash: str, role_id: int) -> User:
    user = User(
        role_id=role_id,
        username=username,
        password_hash=password_hash,
        status="ACTIVE",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def lock_user(db: Session, user: User) -> None:
    user.status = "LOCKED"
    db.commit()


def unlock_user(db: Session, user: User) -> None:
    user.status = "ACTIVE"
    db.commit()
