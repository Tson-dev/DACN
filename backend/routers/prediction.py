from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.config import settings
from backend.models.prediction_history import PredictionHistory
from backend.schemas.common import StandardResponse
from backend.schemas.prediction import PredictionRequest, PredictionData, PredictionHistoryData
from backend.services.profile_service import get_profile_by_user_id

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


def _get_today():
    return datetime.now(ZoneInfo(settings.TIMEZONE)).date()


@router.post("")
def create_prediction(body: PredictionRequest, request: Request, db: Session = Depends(get_db)):
    session = request.state.session
    user_id = session["user_id"]

    today = _get_today()
    existing = db.query(PredictionHistory).filter(
        PredictionHistory.user_id == user_id,
        PredictionHistory.prediction_date == today,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail={"success": False, "message": "You have already made a prediction today."})

    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=400, detail={"success": False, "message": "Student profile not found."})
    if profile.student_code == "PENDING" or (profile.previous_cgpa or 0) == 0:
        raise HTTPException(status_code=400, detail={"success": False, "message": "Student profile is incomplete. Please ask admin to update your profile."})

    try:
        from backend.ml.ml_service import ml_service
        predicted_gpa, probability, similar_count = ml_service.predict(profile, body.target_gpa)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "message": "Prediction service temporarily unavailable"})

    record = PredictionHistory(
        user_id=user_id,
        target_gpa=body.target_gpa,
        predicted_gpa=round(predicted_gpa, 2),
        success_probability=round(probability, 1),
        similar_student_count=similar_count,
        prediction_date=today,
    )
    db.add(record)
    db.commit()

    return StandardResponse(
        success=True,
        data=PredictionData(
            predicted_gpa=round(predicted_gpa, 2),
            target_gpa=body.target_gpa,
            success_probability=round(probability, 1),
            similar_student_count=similar_count,
        ).model_dump(),
    )


@router.get("/today")
def get_today_prediction(request: Request, db: Session = Depends(get_db)):
    session = request.state.session
    user_id = session["user_id"]
    today = _get_today()

    record = db.query(PredictionHistory).filter(
        PredictionHistory.user_id == user_id,
        PredictionHistory.prediction_date == today,
    ).first()

    if not record:
        return StandardResponse(success=True, data=None)

    return StandardResponse(
        success=True,
        data=PredictionHistoryData(
            predicted_gpa=record.predicted_gpa,
            target_gpa=record.target_gpa,
            success_probability=record.success_probability,
            similar_student_count=record.similar_student_count,
            prediction_date=record.prediction_date.isoformat(),
        ).model_dump(),
    )


@router.get("/history")
def get_prediction_history(request: Request, db: Session = Depends(get_db)):
    session = request.state.session
    user_id = session["user_id"]

    records = db.query(PredictionHistory).filter(
        PredictionHistory.user_id == user_id,
    ).order_by(PredictionHistory.prediction_date.desc()).all()

    data = [
        PredictionHistoryData(
            predicted_gpa=r.predicted_gpa,
            target_gpa=r.target_gpa,
            success_probability=r.success_probability,
            similar_student_count=r.similar_student_count,
            prediction_date=r.prediction_date.isoformat(),
        ).model_dump()
        for r in records
    ]

    return StandardResponse(success=True, data=data)
