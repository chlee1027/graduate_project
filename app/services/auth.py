"""아이디·비밀번호 계정과 로그인 토큰.

- 비밀번호: scrypt(표준 라이브러리) + 사용자마다 다른 salt. 원문은 저장하지 않는다.
- 토큰: 로그인할 때 무작위 32바이트를 만들어 기기에 주고, DB 에는 SHA-256 만 둔다.
- 개인 API 는 require_user 로 토큰의 주인을 알아내고, ensure_self 로 남의 기록을 막는다.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.db.models import AuthSession

USERNAME_RE = re.compile(r"^[a-z0-9_]{3,20}$")
MIN_PASSWORD = 8
_N, _R, _P = 2 ** 14, 8, 1


def normalize_username(name: str) -> str:
    return (name or "").strip().lower()


def validate_credentials(username: str, password: str) -> None:
    if not USERNAME_RE.match(username):
        raise HTTPException(status_code=422, detail="아이디는 영문 소문자, 숫자, 밑줄로 3~20자예요.")
    if len(password or "") < MIN_PASSWORD:
        raise HTTPException(status_code=422, detail=f"비밀번호는 {MIN_PASSWORD}자 이상이에요.")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=32)
    b = lambda x: base64.b64encode(x).decode()
    return f"scrypt${_N}${_R}${_P}${b(salt)}${b(dk)}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, n, r, p, salt, dk = stored.split("$")
        got = hashlib.scrypt(password.encode(), salt=base64.b64decode(salt), n=int(n), r=int(r), p=int(p), dklen=32)
        return hmac.compare_digest(got, base64.b64decode(dk))
    except Exception:
        return False


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_session(db: Session, user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    db.add(AuthSession(token_hash=_token_hash(token), user_id=user_id, created_at=now, last_used_at=now))
    db.commit()
    return token


def delete_session(db: Session, token: str) -> None:
    db.query(AuthSession).filter(AuthSession.token_hash == _token_hash(token)).delete()
    db.commit()


def _bearer(authorization: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip() or None
    return None


def require_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> str:
    """토큰의 주인 user_id. 없거나 만료면 401."""
    token = _bearer(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="로그인이 필요해요.")
    row = db.query(AuthSession).filter(AuthSession.token_hash == _token_hash(token)).first()
    now = datetime.now(timezone.utc)
    if row:
        last = row.last_used_at if row.last_used_at.tzinfo else row.last_used_at.replace(tzinfo=timezone.utc)
        if now - last > timedelta(days=settings.SESSION_DAYS):
            db.delete(row)
            db.commit()
            row = None
    if not row:
        raise HTTPException(status_code=401, detail="로그인이 만료됐어요. 다시 로그인해 주세요.")
    if now - (row.last_used_at if row.last_used_at.tzinfo else row.last_used_at.replace(tzinfo=timezone.utc)) > timedelta(hours=1):
        row.last_used_at = now   # 쓸 때마다 갱신하면 DB 쓰기가 많아 한 시간에 한 번만
        db.commit()
    return row.user_id


def ensure_self(auth_user_id: str, user_id: str) -> None:
    if auth_user_id != user_id:
        raise HTTPException(status_code=403, detail="다른 사용자의 기록이에요.")
