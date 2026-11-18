"""호출 제한(AI 코치, 가입, 로그인). 서버리스 인스턴스끼리 메모리를 나누지 않으므로 기록은 DB 에 둔다.

종류(endpoint)마다 따로 센다. 로그인 시도가 AI 코치 한도를 깎지 않는다.
"""

import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import ChatbotCall

AI_ENDPOINTS = ("ask", "exercise-guide")


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
             .filter(ChatbotCall.ip_hash == h, ChatbotCall.endpoint.in_(AI_ENDPOINTS),
                     ChatbotCall.created_at >= now - timedelta(hours=1)).count())
        if n >= per_ip:
            raise HTTPException(status_code=429,
                                detail=f"AI 가이드는 한 시간에 {per_ip}번까지 쓸 수 있어요. 잠시 뒤에 다시 시도해 주세요.")
    if per_day:
        n = (db.query(ChatbotCall)
             .filter(ChatbotCall.endpoint.in_(AI_ENDPOINTS), ChatbotCall.created_at >= now - timedelta(days=1)).count())
        if n >= per_day:
            raise HTTPException(status_code=429,
                                detail="오늘 데모의 AI 가이드 사용량이 다 찼어요. 내일 다시 시도해 주세요.")
    db.add(ChatbotCall(ip_hash=h, endpoint=endpoint, created_at=now))
    db.commit()


def ip_limit(db: Session, request: Request, endpoint: str, per_hour: int, message: str) -> None:
    """endpoint 하나에 대해 IP 당 한 시간 per_hour 번까지. 넘으면 429, 아니면 기록한다."""
    now = datetime.now(timezone.utc)
    h = ip_hash(client_ip(request))
    n = (db.query(ChatbotCall)
         .filter(ChatbotCall.ip_hash == h, ChatbotCall.endpoint == endpoint,
                 ChatbotCall.created_at >= now - timedelta(hours=1)).count())
    if n >= per_hour:
        raise HTTPException(status_code=429, detail=message)
    db.add(ChatbotCall(ip_hash=h, endpoint=endpoint, created_at=now))
    db.commit()
