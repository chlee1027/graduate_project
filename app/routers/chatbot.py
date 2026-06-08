from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from app.core.config import settings

router = APIRouter()

# Gemini API 설정 및 모델 자동 탐색
GEMINI_API_KEY = settings.GEMINI_API_KEY
model = None

def init_gemini():
    global model
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY is missing in settings")
        return
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # 사용 가능한 모델 리스트 조회
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print(f"Available models: {available_models}")
        
        # 최신/고성능 모델 순서대로 탐색 (사용자 요청 3.5 포함)
        preferred_models = [
            'models/gemini-3.5-flash',
            'models/gemini-1.5-pro-002',
            'models/gemini-1.5-pro', 
            'models/gemini-1.5-flash'
        ]
        
        target_model = None
        for pm in preferred_models:
            if pm in available_models:
                target_model = pm
                break
        
        if not target_model and available_models:
            target_model = available_models[0]
            
        if target_model:
            print(f"Connecting to REAL AI Model: {target_model}")
            model = genai.GenerativeModel(target_model)
        else:
            print("No suitable models found for this API Key.")
            
    except Exception as e:
        print(f"Critical Gemini Init Error: {e}")
        model = None

init_gemini()

class ChatRequest(BaseModel):
    message: str
    user_id: str

class ExerciseGuideRequest(BaseModel):
    exercise_name: str
    target_parts: str

@router.post("/ask")
async def ask_gemini(request: ChatRequest):
    if not model:
        # 초기화 재시도 (서버 가동 중 키가 바뀌었을 가능성 대비)
        init_gemini()
        if not model:
            raise HTTPException(status_code=500, detail="AI Model not available. Check API Key and Plan.")

    try:
        # 전문가 페르소나 부여 및 답변 생성
        prompt = f"""
        당신은 10년 경력의 대한민국 최고 전문 헬스 트레이너 'AI PT 코치'입니다. 
        사용자의 질문에 대해 전문적이고, 친절하며, 강력한 동기부여를 주는 답변을 한국어로 제공하세요.
        답변 마지막에는 항상 운동 팁 하나를 덧붙여주세요.
        
        사용자 질문: {request.message}
        """
        
        response = model.generate_content(prompt)
        return {"answer": response.text}
        
    except Exception as e:
        print(f"Chat Execution Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI 답변 생성 중 오류가 발생했습니다: {str(e)}")

@router.post("/exercise-guide")
async def get_exercise_guide(request: ExerciseGuideRequest):
    if not model:
        init_gemini()
        if not model:
            raise HTTPException(status_code=500, detail="AI Model not available.")

    try:
        prompt = f"""
        당신은 전문 PT 코치입니다. 다음 운동에 대해 상세한 가이드를 작성해주세요.
        운동 이름: {request.exercise_name}
        주요 타겟 부위: {request.target_parts}

        다음 형식을 지켜서 한국어로 답변하세요:
        1. 운동 설명: (한 문장으로 핵심 설명)
        2. 주요 효과: (어디에 효과적인지 구체적으로, 근성장/다이어트/체형교정 관점에서 설명)
        3. 주의 사항: (부상 방지를 위한 핵심 팁 한가지)
        4. 추천 유튜브 검색어: (유튜브에서 검색하기 좋은 키워드 하나)

        이모지를 적절히 사용하여 친절하게 답변해주세요.
        """
        
        response = model.generate_content(prompt)
        text = response.text
        
        # 유튜브 검색어 추출 시도 (AI 답변에서 마지막 줄이나 특정 패턴 찾기)
        import urllib.parse
        search_query = request.exercise_name + " 가이드"
        if "추천 유튜브 검색어:" in text:
            search_query = text.split("추천 유튜브 검색어:")[-1].strip()
        
        youtube_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_query)}"

        return {
            "guide_text": text,
            "youtube_url": youtube_url
        }
        
    except Exception as e:
        print(f"Guide Generation Error: {e}")
        raise HTTPException(status_code=500, detail="AI 가이드를 생성하는 중 오류가 발생했습니다.")
