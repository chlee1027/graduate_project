from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.db.models import Account
from app.schemas.request_response import LoginRequest, LoginResponse
from app.services.auth import _bearer, create_session, delete_session, normalize_username, require_user, verify_password
from app.services.rate_limit import ip_limit

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, http: Request, db: Session = Depends(get_db)):
    """다른 기기에서 이어서 쓰기. 아이디나 비밀번호 중 무엇이 틀렸는지는 알려 주지 않는다."""
    ip_limit(db, http, "login", settings.LOGINS_PER_IP_PER_HOUR, "로그인 시도가 많아요. 잠시 뒤에 다시 해 주세요.")
    account = db.query(Account).filter(Account.username == normalize_username(request.username)).first()
    if not account or not verify_password(request.password, account.password_hash):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 맞지 않아요.")
    return LoginResponse(user_id=account.user_id, username=account.username, token=create_session(db, account.user_id))


@router.post("/logout")
def logout(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    token = _bearer(authorization)
    if token:
        delete_session(db, token)
    return {"ok": True}


@router.get("/me")
def me(user_id: str = Depends(require_user), db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.user_id == user_id).first()
    return {"user_id": user_id, "username": account.username if account else None}
