"""한국 시간(KST) 처리를 한곳에 모은다.

이 프로젝트의 created_at 은 모두 timestamptz(`DateTime(timezone=True)`)이고,
기록은 UTC 로 저장된다. 스트릭과 주간 활동은 한국 날짜 기준으로 세어야 하므로
두 가지가 필요하다.

1. SQL 쪽: timestamptz 를 한국 날짜로 바꾸는 식 -> kst_date()
2. 파이썬 쪽: 오늘 날짜와 "며칠 전" 기준 시각 -> today_kst(), now_kst()

주의: PostgreSQL 의 timezone(zone, x) 는 인자 타입에 따라 방향이 뒤집힌다.
      timezone('Asia/Seoul', timestamptz) -> 서울 벽시계 timestamp  (이게 맞다)
      timezone('Asia/Seoul', timestamp)   -> 그 값을 서울 시각으로 해석한 timestamptz
      예전 코드는 timezone('Asia/Seoul', timezone('UTC', created_at)) 처럼 두 번 걸어
      뒤쪽이 두 번째 형태로 잡혔고, 9시간을 더하는 대신 빼서 18시 이전 기록이
      전날로 밀렸다. 한 번만 거는 것이 맞다.
"""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func

# 한국은 서머타임이 없으므로 고정 오프셋으로 충분하다.
# (zoneinfo 는 윈도우에서 tzdata 패키지가 있어야 동작해서 쓰지 않는다)
KST = timezone(timedelta(hours=9))


def now_kst() -> datetime:
    """한국 시간 기준 현재 시각. tz 정보가 붙어 있어 DB 비교에 그대로 쓸 수 있다."""
    return datetime.now(KST)


def today_kst() -> date:
    """한국 시간 기준 오늘 날짜. 서버가 UTC 로 돌아도 값이 흔들리지 않는다."""
    return now_kst().date()


def kst_date(column):
    """timestamptz 컬럼을 한국 날짜로 바꾸는 SQL 식."""
    return func.date(func.timezone("Asia/Seoul", column))
