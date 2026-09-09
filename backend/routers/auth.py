from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.auth import LoginRequest
from backend.schemas.common import StandardResponse
from backend.services.auth_service import verify_password, create_session, delete_session
from backend.services.user_service import get_user_by_username

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = get_user_by_username(db, body.username)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=400, detail={"success": False, "message": "Invalid username or password"})

    if user.status == "LOCKED":
        raise HTTPException(status_code=400, detail={"success": False, "message": "Account is locked"})

    session_id = create_session(
        user_id=user.user_id,
        username=user.username,
        role=user.role.name,
        status=user.status,
    )

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=86400,
        path="/",
    )

    return StandardResponse(
        success=True,
        message="Login successful",
        data={"user_id": user.user_id, "username": user.username, "role": user.role.name},
    )


@router.post("/logout")
def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id:
        delete_session(session_id)

    response.delete_cookie(key="session_id", path="/")
    return StandardResponse(success=True, message="Logged out successfully")
