"""잔디(GitHub 기여 그래프 모양) 차트용 날짜별 집계와 연속 운동일.

기록 시각은 UTC 로 저장되고 날짜는 한국 날짜로 센다. SQL 의 timezone() 대신 파이썬에서 바꾸므로
PostgreSQL 과 SQLite(시험) 에서 같은 값이 나온다.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Dict, Iterable, List, Tuple

from app.core.timezone import KST


def to_kst_date(created_at: datetime) -> date:
    """tz 가 없는 값(SQLite)은 UTC 로 본다. app 은 기록을 UTC 로 저장한다."""
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return created_at.astimezone(KST).date()


def daily_totals(rows: Iterable[Tuple[datetime, int]]) -> Dict[date, Dict[str, int]]:
    """(기록 시각, 운동 분) 목록을 한국 날짜별 {count, minutes} 로 묶는다. 완료한 기록만 넘긴다."""
    out: Dict[date, Dict[str, int]] = {}
    for created_at, minutes in rows:
        d = to_kst_date(created_at)
        day = out.setdefault(d, {"count": 0, "minutes": 0})
        day["count"] += 1
        day["minutes"] += int(minutes or 0)
    return out


def streaks(days: Iterable[date], today: date) -> Dict[str, int]:
    """현재 연속일(오늘 또는 어제부터 거꾸로, streak_service 와 같은 규칙)과 가장 긴 연속일."""
    s = set(days)
    current = 0
    check = today if today in s else today - timedelta(days=1)
    while check in s:
        current += 1
        check -= timedelta(days=1)
    longest = run = 0
    prev = None
    for d in sorted(s):
        run = run + 1 if prev is not None and d - prev == timedelta(days=1) else 1
        longest = max(longest, run)
        prev = d
    return {"current_streak": current, "longest_streak": longest}


def grid_start(today: date, weeks: int) -> date:
    """잔디의 첫 칸. 마지막 열이 이번 주(월요일 시작)가 되도록 weeks 주 전 월요일."""
    this_monday = today - timedelta(days=today.weekday())
    return this_monday - timedelta(weeks=weeks - 1)


def heatmap(totals: Dict[date, Dict[str, int]], today: date, weeks: int) -> List[Dict]:
    """grid_start 부터 오늘까지 하루 한 칸. 기록 없는 날은 0."""
    start = grid_start(today, weeks)
    out = []
    d = start
    while d <= today:
        t = totals.get(d, {"count": 0, "minutes": 0})
        out.append({"date": d.isoformat(), "count": t["count"], "minutes": t["minutes"]})
        d += timedelta(days=1)
    return out
