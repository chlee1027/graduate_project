# 🏋️ Fitness AI Recommender (RL 기반 운동 추천 시스템)

## 📌 프로젝트 개요

사용자의 건강 정보, 컨디션, 환경을 기반으로 **개인화된 운동을 추천하는 AI 코칭 시스템**입니다. 
초기에는 **규칙 기반 + Contextual Bandit**으로 추천을 수행하며, 전문적인 운동 지표(RPE, MET, 세트당 휴식 시간)를 학습 데이터로 활용합니다.

---

## 🎯 주요 성과 및 업데이트 (2026.05.17)

### 🧬 과학적 운동 데이터베이스 (Seeded)
*   **42종의 전문 운동 플랜**: PostgreSQL DB에 총 42개의 고품질 운동 데이터를 이식했습니다.
*   **객관적 지표 적용**: 모든 운동에 **타겟 RPE(강도), 권장 휴식 시간, MET(대사량)** 지수를 부여하여 전문성을 확보했습니다.
*   **DB 가이드 생성**: 전체 운동 라이브러리를 한눈에 볼 수 있는 엑셀 가이드 파일(`docs/exercise_database_guide.csv`)을 생성했습니다.

### ⏱️ 독립형 단계별 타이머 시스템
*   **WORK/REST 분리**: 운동 페이즈와 휴식 페이즈를 명확히 구분한 독립 타이머 시스템을 구축했습니다.
*   **현실적인 시간 배분**: 전체 권장 시간을 세트 수로 나누어 각 세트당 적절한 카운트다운을 제공합니다.
*   **수행 검증 로직**: 시간 기반(70%), 횟수 기반(50%)의 세트별 최소 이수 시간을 강제하여 데이터 신뢰성을 높였습니다.

### 🔔 스마트 알림 및 리텐션
*   **푸시 알림**: `expo-notifications`를 연동하여 사용자가 설정한 운동 시간에 맞춰 매일 알림을 발송합니다.
*   **네이티브 온보딩**: 시스템 순정 시간 선택기(Time Picker)를 중앙 모달 형태로 구현하여 접근성을 높였습니다.

### 📊 대시보드 및 리포트
*   **주간 목표 달성 바**: 홈 화면에서 이번 주 운동 목표 달성도를 실시간으로 확인 가능합니다.
*   **상세 활동 리스트**: 최근 7일간 수행한 운동의 상세 로그(이름, 세트, 시간)를 조회할 수 있습니다.

---

## ⚙️ 기술 스택

### Frontend
*   **Framework**: Expo (React Native SDK 54+) + TypeScript
*   **State**: Zustand (User & Session store)
*   **Animation**: React Native Reanimated
*   **Native**: Expo Notifications, Device, Constants, DateTimePicker

### Backend
*   **Framework**: FastAPI (Python 3.10+)
*   **Database**: PostgreSQL (Docker-Compose)
*   **AI Engine**: Contextual Bandit (ε-greedy) + Experience-based Adjustment Service

---

## 📂 프로젝트 구조

```text
graduate_project/
│
├─ app/                 # Backend (FastAPI)
│  ├─ db/               # PostgreSQL Models
│  ├─ routers/          # recommend, stats, log, reward, onboarding
│  └─ services/         # candidate_generator, bandit_logic, streak_service
│
├─ frontend/            # Mobile App (Expo)
│  ├─ app/              # Expo Router (workout/, stats/weekly.tsx)
│  └─ src/              # components, api, store, services(notifications)
│
├─ scripts/             # Setup & Utility Scripts (Seeding, CSV generation)
├─ docs/                # Documentation & Excel Guides
└─ README.md
```

---

## 🚀 시작하기 (Getting Started)

### 📋 사전 준비 (Prerequisites)
*   **Docker Desktop**: 데이터베이스(PostgreSQL) 실행을 위해 필요합니다.
*   **Python 3.10+**: 백엔드 서버 실행을 위해 필요합니다.
*   **Node.js & npm**: 프런트엔드(Expo) 실행을 위해 필요합니다.

---

### 1. 백엔드 설정 (Backend Setup)

1.  **가상환경 생성 및 활성화**:
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```
2.  **의존성 설치**:
    ```powershell
    pip install -r requirements.txt
    ```
3.  **환경 변수 설정**:
    *   `.env.example` 파일을 복사하여 `.env` 파일을 생성하고, 필요에 따라 DB 접속 정보를 수정합니다.
4.  **데이터베이스 실행 (Docker)**:
    ```powershell
    docker-compose up -d
    ```
5.  **데이터베이스 초기화 (Seeding)**:
    ```powershell
    $env:PYTHONPATH = "."
    python scripts/seed_db.py
    ```
6.  **서버 실행**:
    ```powershell
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

---

### 2. 프런트엔드 설정 (Frontend Setup)

1.  **경로 이동**:
    ```powershell
    cd frontend
    ```
2.  **의존성 설치**:
    ```powershell
    npm install --legacy-peer-deps
    ```
3.  **앱 실행**:
    ```powershell
    npx expo start -c
    ```
    *   터미널에 나타나는 QR 코드를 스마트폰의 **Expo Go** 앱으로 스캔하여 확인합니다.

---

### 💡 문제 해결 (Troubleshooting)
*   **네트워크 오류**: 프런트엔드에서 백엔드로 접속이 안 될 경우, `frontend/src/api/client.ts` 파일에서 `BASE_URL`의 IP 주소가 본인 컴퓨터의 로컬 IP(IPv4)와 일치하는지 확인하세요.
*   **DB 연결 실패**: Docker Desktop이 실행 중인지, 포트 5432가 이미 사용 중이지 않은지 확인하세요.

---

## 🚧 향후 과제 (Next Priority)

1.  **인앱 가이드 영상 플레이어**: 외부 링크 이탈 없이 앱 내에서 운동 가이드를 시청하는 기능.
2.  **칼로리 소모 리포트**: MET 지수와 체중 데이터를 결합한 실시간 소모 열량 대시보드.
3.  **프로덕션 클린업**: 개발용 테스트 로직(5초 통과 등) 및 디버그 버튼 제거.

---
*Developed as a Graduate Project (Fitness AI Recommender)*
