from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.database import init_db, SessionLocal
from backend.seed import seed_data
from backend.middleware.auth_middleware import AuthMiddleware
from backend.routers import auth, profile, prediction, admin
from backend.config import settings
from backend.ml.ml_service import ml_service

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="GPA Prediction System", docs_url="/docs", redoc_url=None)
app.add_middleware(AuthMiddleware)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(prediction.router)
app.include_router(admin.router)

app.mount("/static", StaticFiles(directory=str(settings.BASE_DIR / "frontend" / "static")), name="static")
templates = Jinja2Templates(directory=str(settings.BASE_DIR / "frontend" / "templates"))


@app.on_event("startup")
def startup():
    settings.DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
    try:
        ml_service.load()
    except FileNotFoundError:
        logger.warning("ML model not found. Predictions will be unavailable. Run: python train_model.py")


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    from fastapi.responses import JSONResponse
    if isinstance(exc, StarletteHTTPException):
        if isinstance(exc.detail, dict):
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"success": False, "message": str(exc.detail)})
    if isinstance(exc, RequestValidationError):
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append({"field": field, "message": error["msg"]})
        return JSONResponse(status_code=422, content={"success": False, "message": "Validation error", "errors": errors})
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"success": False, "message": "Internal server error"})


@app.get("/")
def root():
    return RedirectResponse(url="/login", status_code=302)


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


@app.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {})


@app.get("/history")
def history_page(request: Request):
    return templates.TemplateResponse(request, "history.html", {})


@app.get("/admin")
def admin_dashboard_page(request: Request):
    return templates.TemplateResponse(request, "admin/dashboard.html", {})


@app.get("/admin/users")
def admin_users_page(request: Request):
    return templates.TemplateResponse(request, "admin/users.html", {})


@app.get("/admin/users/create")
def admin_create_user_page(request: Request):
    return templates.TemplateResponse(request, "admin/create_user.html", {})


@app.get("/admin/profiles")
def admin_profiles_page(request: Request):
    return templates.TemplateResponse(request, "admin/profiles.html", {})


@app.get("/admin/profiles/{profile_id}/edit")
def admin_edit_profile_page(profile_id: int, request: Request):
    return templates.TemplateResponse(request, "admin/edit_profile.html", {"profile_id": profile_id})
