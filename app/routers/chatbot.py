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
