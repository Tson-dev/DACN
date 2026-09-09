from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.common import StandardResponse
from backend.schemas.profile import ProfileResponse
from backend.services.profile_service import get_profile_by_user_id

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/me")
def get_my_profile(request: Request, db: Session = Depends(get_db)):
    session = request.state.session
    profile = get_profile_by_user_id(db, session["user_id"])
    if not profile:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Student profile not found"})

    return StandardResponse(
        success=True,
        data=ProfileResponse.model_validate(profile).model_dump(),
    )
