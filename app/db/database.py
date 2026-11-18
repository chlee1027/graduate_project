import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Vercel 같은 서버리스에서는 함수 인스턴스마다 연결을 붙잡아 두면 DB 연결 수가 쌓인다.
# 거기서는 요청마다 연결을 열고 닫는다(Neon 의 pooled 주소가 연결 재사용을 맡는다).
def _with_driver(url: str) -> str:
    """드라이버를 psycopg2 로 못박는다. SQLAlchemy 2.1 부터 postgresql:// 의 기본 드라이버가
    psycopg(3) 로 바뀌어, 설치된 psycopg2 를 두고 없는 psycopg 를 찾다 실패한다."""
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg2://" + url[len(prefix):]
    return url


_serverless = bool(os.environ.get("VERCEL"))
engine = create_engine(
    _with_driver(settings.DATABASE_URL),
    pool_pre_ping=True,
    **({"poolclass": NullPool} if _serverless else {}),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
