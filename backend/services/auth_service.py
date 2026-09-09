import secrets
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import bcrypt

from backend.config import settings

_sessions: dict[str, dict] = {}


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_session(user_id: int, username: str, role: str, status: str = "ACTIVE") -> str:
    session_id = secrets.token_hex(32)
    tz = ZoneInfo(settings.TIMEZONE)
    _sessions[session_id] = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "status": status,
        "created_at": datetime.now(tz),
    }
    return session_id


def get_session(session_id: str) -> dict | None:
    session = _sessions.get(session_id)
    if not session:
        return None
    tz = ZoneInfo(settings.TIMEZONE)
    expiry = session["created_at"] + timedelta(hours=settings.SESSION_EXPIRY_HOURS)
    if datetime.now(tz) > expiry:
        _sessions.pop(session_id, None)
        return None
    return session


def delete_session(session_id: str) -> bool:
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False
