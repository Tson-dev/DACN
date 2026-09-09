from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.role import Role
from backend.models.user import User
from backend.schemas.common import StandardResponse
from backend.schemas.user import UserCreate, UserResponse
from backend.schemas.profile import AdminProfileResponse, ProfileUpdate, ProfileResponse
from backend.services.user_service import get_user_by_username, create_user, get_all_users, lock_user, unlock_user, get_user_by_id
from backend.services.profile_service import get_all_profiles, get_profile_by_id, update_profile, create_student_profile
from backend.services.auth_service import hash_password

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _require_admin(request: Request):
    session = request.state.session
    if not session or session["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail={"success": False, "message": "Forbidden"})
    return session


@router.post("/users")
def admin_create_user(body: UserCreate, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)

    existing = get_user_by_username(db, body.username)
    if existing:
        raise HTTPException(status_code=400, detail={"success": False, "message": "Username already exists"})

    role = db.query(Role).filter(Role.name == body.role).first()
    if not role:
        raise HTTPException(status_code=400, detail={"success": False, "message": f"Invalid role: {body.role}"})

    user = create_user(db, body.username, hash_password(body.password), role.role_id)

    if body.role == "STUDENT":
        create_student_profile(db, user.user_id)

    return StandardResponse(
        success=True,
        message="User created successfully",
        data={"user_id": user.user_id, "username": user.username, "role": body.role},
    )


@router.get("/users")
def admin_list_users(request: Request, db: Session = Depends(get_db)):
    _require_admin(request)

    users = get_all_users(db)
    data = [
        {
            "user_id": u.user_id,
            "username": u.username,
            "role": u.role.name,
            "status": u.status,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]
    return StandardResponse(success=True, data={"users": data})


@router.put("/users/{user_id}/lock")
def admin_lock_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail={"success": False, "message": "User not found"})
    if user.status == "LOCKED":
        raise HTTPException(status_code=400, detail={"success": False, "message": "User is already locked"})

    lock_user(db, user)
    return StandardResponse(success=True, message="User locked successfully")


@router.put("/users/{user_id}/unlock")
def admin_unlock_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail={"success": False, "message": "User not found"})
    if user.status == "ACTIVE":
        raise HTTPException(status_code=400, detail={"success": False, "message": "User is already active"})

    unlock_user(db, user)
    return StandardResponse(success=True, message="User unlocked successfully")


@router.get("/profiles")
def admin_list_profiles(request: Request, db: Session = Depends(get_db)):
    _require_admin(request)

    profiles = get_all_profiles(db)
    data = [AdminProfileResponse.model_validate(p).model_dump() for p in profiles]
    return StandardResponse(success=True, data={"profiles": data})


@router.put("/profiles/{profile_id}")
def admin_update_profile(profile_id: int, body: ProfileUpdate, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)

    profile = get_profile_by_id(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Profile not found"})

    if body.student_code != profile.student_code:
        from backend.models.student_profile import StudentProfile
        existing = db.query(StudentProfile).filter(
            StudentProfile.student_code == body.student_code,
            StudentProfile.profile_id != profile_id,
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail={"success": False, "message": "Student code already exists"})

    update_profile(db, profile, body.model_dump())
    return StandardResponse(success=True, message="Profile updated successfully")
