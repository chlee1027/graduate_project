# 🏋️ Fitness AI Recommender - 개발 가이드

## 🚀 프로젝트 개요
이 프로젝트는 강화학습 기반의 개인 맞춤형 운동 추천 시스템입니다. **Contextual Bandit (ε-greedy)** 알고리즘을 사용하여 사용자의 상태와 피드백에 따라 최적의 운동 플랜을 제안합니다.

## 🛠 기술 스택
*   **백엔드:** FastAPI (Python)
*   **프론트엔드:** React Native (Expo SDK 54)
*   **데이터베이스:** PostgreSQL (Docker 사용)
*   **스타일링:** NativeWind (Tailwind CSS)
*   **상태 관리:** Zustand

## 🏃 빠른 시작 가이드

### 1. 데이터베이스 설정 (Docker)
Docker Desktop이 실행 중인지 확인한 후 다음 명령어를 입력하세요.
```powershell
docker-compose up -d
```

### 2. 백엔드 실행 (FastAPI)
```powershell
# 가상환경 활성화
.\venv\Scripts\activate

# 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*   **주의:** 모바일 기기(Expo Go) 연결을 위해 `--host 0.0.0.0` 옵션이 반드시 필요합니다.

### 3. 프론트엔드 실행 (Expo)
```powershell
cd frontend
npx expo start -c
```
*   **IP 설정:** `frontend/src/api/client.ts` 파일의 `BASE_URL`을 본인 PC의 IPv4 주소로 수정해야 합니다. (예: `192.168.x.x`)

## 📁 주요 폴더 구조
*   `/app`: FastAPI 백엔드 로직, 라우터, DB 모델.
*   `/frontend`: React Native (Expo) 애플리케이션 코드.
*   `/docker-compose.yml`: 데이터베이스 컨테이너 설정 파일.

## 🧠 핵심 로직 흐름
1.  **온보딩(Onboarding):** 사용자의 기본 프로필과 운동 목표 수집.
2.  **추천(Recommend):** `Candidate Generator`가 운동 후보를 필터링하고, `Bandit` 알고리즘이 최적의 운동을 선택.
3.  **로그 및 보상(Log/Reward):** 사용자가 운동 결과를 기록하면, 시스템이 보상을 계산하고 `BanditStat` 통계를 업데이트하여 학습.
