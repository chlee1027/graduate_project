"""AI 코치 (Claude). 운동 가이드와 자유 질문 두 가지.

모델·노력 수준은 환경 변수 CLAUDE_MODEL·CLAUDE_EFFORT 로 바꾼다(app/core/config.py).
공개 데모에서는 호출마다 rate_limit.check_and_record 가 IP·하루 한도를 먼저 본다.
"""

import re
import urllib.parse

import anthropic
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.services.rate_limit import check_and_record
from app.services.auth import ensure_self, require_user

router = APIRouter()

_client = None


def get_client():
    """첫 요청 때 만든다. 키가 없으면 None."""
    global _client
    if _client is None and settings.ANTHROPIC_API_KEY:
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY, timeout=60.0, max_retries=2)
    return _client


# 서버 쪽 거절 대체(fallbacks)를 받는 모델. Haiku 5.5 는 받지 않으므로 보내지 않는다.
FALLBACK_MODELS = {"claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5", "claude-fable-5-2", "claude-fable-5-1"}

COACH_SYSTEM = (
    "당신은 10년 경력의 대한민국 최고 전문 헬스 트레이너 'AI PT 코치'입니다. "
    "전문적이고 친절하며 동기부여가 되는 답변을 한국어로 합니다. "
    "통증이나 부상이 의심되는 질문에는 운동을 멈추고 전문가 진료를 권합니다. "
    "앱 화면에 그대로 보이므로 이모지와 마크다운(#, **, 표)을 쓰지 말고 짧은 문단과 '-' 목록으로만 씁니다."
)


def ask_claude(prompt: str, max_tokens: int = 2000) -> str:
    client = get_client()
    if client is None:
        raise HTTPException(status_code=503, detail="AI 코치가 아직 연결되지 않았어요(API 키 없음).")
    params = dict(
        model=settings.CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=COACH_SYSTEM,
        output_config={"effort": settings.CLAUDE_EFFORT},
        messages=[{"role": "user", "content": prompt}],
    )
    if settings.CLAUDE_MODEL in FALLBACK_MODELS:
        # 안전 분류기가 거절하면 서버가 알맞은 모델로 다시 돌린다
        params.update(betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    try:
        response = client.beta.messages.create(**params)
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="AI 코치가 잠시 바빠요. 조금 뒤에 다시 시도해 주세요.")
    except anthropic.APIStatusError as e:
        print(f"Claude API error {e.status_code}: {e.message}")
        raise HTTPException(status_code=502, detail="AI 답변을 만드는 중 오류가 발생했습니다.")
    except anthropic.APIConnectionError as e:
        print(f"Claude connection error: {e}")
        raise HTTPException(status_code=502, detail="AI 서버에 연결하지 못했습니다.")

    if response.stop_reason == "refusal":
        return "이 질문에는 답하기 어려워요. 운동 방법이나 루틴에 관한 질문으로 다시 물어봐 주세요."
    text = "".join(block.text for block in response.content if block.type == "text").strip()
    if not text:
        raise HTTPException(status_code=502, detail="AI 답변이 비어 있습니다.")
    return text


def extract_search_query(text: str, fallback: str) -> str:
    """AI 답변에서 유튜브 검색어 한 줄만 뽑는다.

    답변이 마크다운이라 마커 뒤에 별표와 백틱, 이모지, 괄호 설명이 줄줄이 붙어 온다.
    마커 뒤를 통째로 쓰면 유튜브가 답변 전체를 검색해 결과가 엉뚱해진다.

        **4. 추천 유튜브 검색어:**
        `맨몸 스쿼트 정석 자세` (정확한 자극점을 찾기 위해 ...)

    여기서 원하는 것은 백틱 안의 한 줄이다.
    """
    marker = "추천 유튜브 검색어"
    if marker not in text:
        return fallback

    tail = text.split(marker, 1)[1].lstrip(" :*`\n")
    first_block = tail.split("\n\n")[0]

    quoted = re.search(r"`([^`]+)`", first_block)
    candidate = quoted.group(1) if quoted else first_block.split("\n")[0]

    candidate = re.sub(r"[(（][^)）]*[)）]", " ", candidate)   # 괄호 설명을 뗀다
    # 이모지와 마크다운 기호를 턴다. 한글과 숫자는 isalnum 으로 살아남는다.
    candidate = "".join(ch for ch in candidate if ch.isalnum() or ch.isspace() or ch in "-+")
    candidate = " ".join(candidate.split())

    return candidate or fallback


class ChatRequest(BaseModel):
    message: str
    user_id: str

class ExerciseGuideRequest(BaseModel):
    exercise_name: str
    target_parts: str

@router.post("/ask")
def ask_coach(request: ChatRequest, http: Request, db: Session = Depends(get_db), _user: str = Depends(require_user)):
    if get_client() is None:
        raise HTTPException(status_code=503, detail="AI 코치가 아직 연결되지 않았어요(API 키 없음).")
    check_and_record(db, http, "ask")
    prompt = (
        "사용자의 질문에 답하고, 답변 마지막에 운동 팁 하나를 덧붙여 주세요.\n\n"
        f"사용자 질문: {request.message}"
    )
    return {"answer": ask_claude(prompt)}


@router.post("/exercise-guide")
def get_exercise_guide(request: ExerciseGuideRequest, http: Request, db: Session = Depends(get_db), _user: str = Depends(require_user)):
    if get_client() is None:
        raise HTTPException(status_code=503, detail="AI 코치가 아직 연결되지 않았어요(API 키 없음).")
    check_and_record(db, http, "exercise-guide")
    prompt = f"""다음 운동의 가이드를 작성해 주세요.
운동 이름: {request.exercise_name}
주요 타겟 부위: {request.target_parts}

다음 형식을 지켜 한국어로 답변하세요:
1. 운동 설명: (한 문장으로 핵심 설명)
2. 주요 효과: (어디에 효과적인지 구체적으로, 근성장/다이어트/체형교정 관점에서 설명)
3. 주의 사항: (부상 방지를 위한 핵심 팁 한 가지)
4. 추천 유튜브 검색어: (유튜브에서 검색하기 좋은 키워드 하나를 백틱으로 감싸서)

항목 제목은 위 번호 그대로 한 줄에 쓰고, 내용은 그 아래 줄에 씁니다. 이모지는 쓰지 않습니다."""
    text = ask_claude(prompt)
    search_query = extract_search_query(text, request.exercise_name + " 가이드")
    youtube_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_query)}"
    return {"guide_text": text, "youtube_url": youtube_url}
