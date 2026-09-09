from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.services.auth_service import get_session
from backend.config import settings

PUBLIC_PATHS = {"/", "/login", "/api/auth/login", "/docs", "/redoc", "/openapi.json"}
PUBLIC_PREFIXES = {"/static/"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in PUBLIC_PATHS or any(path.startswith(p) for p in PUBLIC_PREFIXES):
            return await call_next(request)

        session_id = request.cookies.get(settings.COOKIE_NAME)
        session = get_session(session_id) if session_id else None

        request.state.session = session

        is_api = path.startswith("/api/")
        is_admin = path.startswith("/admin") or path.startswith("/api/admin")

        if not session:
            if is_api:
                raise HTTPException(status_code=401, detail={"success": False, "message": "Not authenticated"})
            return RedirectResponse(url="/login", status_code=302)

        if session["status"] == "LOCKED":
            if is_api:
                raise HTTPException(status_code=403, detail={"success": False, "message": "Account is locked"})
            return RedirectResponse(url="/login", status_code=302)

        if is_admin and session["role"] != "ADMIN":
            if is_api:
                raise HTTPException(status_code=403, detail={"success": False, "message": "Forbidden"})
            return RedirectResponse(url="/dashboard", status_code=302)

        return await call_next(request)
