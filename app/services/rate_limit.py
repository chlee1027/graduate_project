"""AI 코치 호출 제한. 서버리스 인스턴스끼리 메모리를 나누지 않으므로 기록은 DB 에 둔다."""

import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import ChatbotCall


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def ip_hash(ip: str) -> str:
    return hashlib.sha256(f"{settings.RATE_LIMIT_SALT}|{ip}".encode()).hexdigest()[:16]


def check_and_record(db: Session, request: Request, endpoint: str) -> None:
    """한도를 넘었으면 429, 아니면 이번 호출을 기록한다.

    시각은 DB 기본값에 맡기지 않고 여기서 UTC 로 넣는다. 넣는 값과 비교하는 값의 형식이 같아야
    SQLite(시험)처럼 시각을 글자로 비교하는 DB 에서도 한도가 맞게 센다.
    """
    now = datetime.now(timezone.utc)
    h = ip_hash(client_ip(request))
    per_ip, per_day = settings.CHATBOT_PER_IP_PER_HOUR, settings.CHATBOT_PER_DAY
    if per_ip:
        n = (db.query(ChatbotCall)
             .filter(ChatbotCall.ip_hash == h, ChatbotCall.created_at >= now - timedelta(hours=1)).count())
        if n >= per_ip:
            raise HTTPException(status_code=429,
                                detail=f"AI 가이드는 한 시간에 {per_ip}번까지 쓸 수 있어요. 잠시 뒤에 다시 시도해 주세요.")
    if per_day:
        n = db.query(ChatbotCall).filter(ChatbotCall.created_at >= now - timedelta(days=1)).count()
        if n >= per_day:
            raise HTTPException(status_code=429,
                                detail="오늘 데모의 AI 가이드 사용량이 다 찼어요. 내일 다시 시도해 주세요.")
    db.add(ChatbotCall(ip_hash=h, endpoint=endpoint, created_at=now))
    db.commit()
