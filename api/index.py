"""Vercel Python 함수 입구. /api/* 요청을 FastAPI 앱 하나가 받는다(vercel.json 의 rewrites)."""

from app.main import app  # noqa: F401
