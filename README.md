# 🏋️ Fitness AI Recommender (RL 기반 운동 추천 시스템)

## 📌 프로젝트 개요

사용자의 건강 정보, 컨디션, 환경을 기반으로 **개인화된 운동을 추천하는 AI 시스템**입니다.
초기에는 **규칙 기반 + Contextual Bandit**으로 추천을 수행하고,
데이터가 축적되면 **Reinforcement Learning (MDP)**으로 확장 가능한 구조입니다.

---

## 🎯 최근 업데이트 (2026.05.16)

*   **UI/UX 혁신**: 온보딩 페이지 블루 테마 적용 및 캐릭터 기반 성별 선택 UI 도입.
*   **인터랙티브 컴포넌트**: 리액트 네이티브 Reanimated를 이용한 '리퀴드 세그먼트' 슬라이더 구현.
*   **추천 고도화**: 홈트/헬스장 장소 전환 토글 및 유튜브 가이드 영상 연동 완료.

---

## ⚙️ 기술 스택

### Frontend
*   **Framework**: Expo (React Native) + TypeScript
*   **Styling**: NativeWind (TailwindCSS)
*   **Animation**: React Native Reanimated
*   **State Management**: Zustand

### Backend
*   **Framework**: FastAPI (Python)
*   **Database**: PostgreSQL (Docker)
*   **AI Engine**: Contextual Bandit (ε-greedy)

---

## 📂 프로젝트 구조

```text
graduate_project/
│
├─ app/                 # Backend (FastAPI)
│  ├─ db/               # Database connection & models
│  ├─ routers/          # API endpoints (onboarding, recommend, log, etc.)
│  ├─ services/         # Business logic (recommender, reward calculation)
│  └─ main.py           # Entry point
│
├─ frontend/            # Mobile App (Expo)
│  ├─ app/              # Expo Router screens
│  └─ src/
│     ├─ api/           # Axios client configuration
│     ├─ components/    # Reusable UI components
│     └─ store/         # State management (Zustand)
│
├─ docker-compose.yml   # Infrastructure (DB)
└─ README.md
```

---

## 🚀 실행 방법

### 1. 인프라 실행 (Docker)
```bash
docker-compose up -d
```

### 2. 백엔드 실행
```bash
cd graduate_project
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 프론트엔드 실행
```bash
cd frontend
npx expo start -c
```

---

## 📊 핵심 기능

1.  **스마트 온보딩**: 사용자 신체 정보 및 운동 목표 수집.
2.  **AI 맞춤 추천**: 위치, 피로도, 수면 상태를 고려한 최적의 운동 플랜 제공.
3.  **보상 시스템**: 운동 완료 및 난이도 피드백을 통한 Bandit 모델 학습.
4.  **시각적 가이드**: 추천 운동별 유튜브 가이드 영상 연결.

---

## 🚧 향후 과제

*   🔥 **Streak 시스템**: 연속 운동일수 트래킹 및 보너스 보상 로직.
*   📈 **데이터 시각화**: 주간 운동 리포트 및 성장 그래프.
*   🔔 **푸시 알림**: 운동 시간 알림 및 리마인드 기능.
