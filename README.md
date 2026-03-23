# 🏋️ Fitness AI Recommender (RL 기반 운동 추천 시스템)

## 📌 프로젝트 개요

사용자의 건강 정보, 컨디션, 환경을 기반으로 **개인화된 운동을 추천하는 AI 시스템**입니다.
초기에는 **규칙 기반 + Contextual Bandit**으로 추천을 수행하고,
데이터가 축적되면 **Reinforcement Learning (MDP)**으로 확장 가능한 구조입니다.

---

## 🎯 핵심 목표

* 사용자 맞춤 운동 추천
* 지속 가능한 운동 습관 형성
* 부상 방지 및 안전한 운동 유도
* 장기적으로 RL 기반 최적화

---

## 🧠 시스템 구조

```text
User → Backend API → Candidate Generator → Bandit Recommender → Response
                           ↓
                        Logs → Reward → Bandit Update
```

---

## ⚙️ 기술 스택

* **Backend**: FastAPI (Python)
* **AI/Recommender**: Contextual Bandit (ε-greedy)
* **Data 처리**: Python (Pandas, Numpy)
* **DB (현재)**: In-Memory (향후 PostgreSQL 예정)
* **API 테스트**: Swagger (FastAPI Docs)

---

## 📂 프로젝트 구조

```text
fitness-ai-app/
│
├─ app/
│  ├─ main.py
│  ├─ routers/
│  │  ├─ onboarding.py
│  │  ├─ recommend.py
│  │  ├─ log.py
│  │  └─ reward.py
│  ├─ services/
│  │  ├─ candidate_generator.py
│  │  ├─ recommender_bandit.py
│  │  ├─ reward_service.py
│  │  └─ fake_db.py
│  ├─ schemas/
│  │  └─ request_response.py
│  └─ core/
│     └─ config.py
│
├─ requirements.txt
└─ README.md
```

---

## 🔄 전체 워크플로우

### 1️⃣ Onboarding

* 사용자 정보 입력 (나이, 목표, 경험 등)
* 초기 안전 루틴 생성

---

### 2️⃣ Daily Recommendation

#### (1) 상태 수집 (State)

* 위치 (집/헬스장)
* 운동 가능 시간
* 피로도 / 수면
* 최근 수행률 / streak

#### (2) 후보 생성 (Candidate Generator)

* 부상 부위 제외
* 장비 필터링
* 강도 제한 적용

#### (3) 추천 (Bandit)

* ε-greedy 기반 탐색/활용
* 최적 운동 선택

---

### 3️⃣ 수행 및 로그 저장

* 완료 여부
* RPE (운동 난이도)
* 통증 여부

---

### 4️⃣ 보상 계산 (Reward)

```python
reward = 0
if completed: +1
if RPE 적정: +0.5
if 통증: -1
streak 보너스 추가
```

---

### 5️⃣ 학습 업데이트

* (state, action, reward) 기반
* Bandit 평균 보상 갱신

---

## 🚀 실행 방법

### 1. 가상환경 생성

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 2. 라이브러리 설치

```bash
pip install -r requirements.txt
```

---

### 3. 서버 실행

```bash
uvicorn app.main:app --reload
```

---

### 4. Swagger 접속

```text
http://127.0.0.1:8000/docs
```

---

## 🧪 API 테스트 순서

### 1. Onboarding

`POST /api/onboarding/`

---

### 2. Recommend

`POST /api/recommend/`

---

### 3. Log

`POST /api/log/`

---

### 4. Reward

`POST /api/reward/`

---

## 📊 예시 결과

### 추천 결과

```json
{
  "selected_plan": {
    "plan_id": "home_squat_basic"
  },
  "reason": "exploration"
}
```

---

### 보상 결과

```json
{
  "reward": 1.56,
  "detail": {
    "completion": 1.0,
    "rpe_bonus": 0.5,
    "pain_penalty": 0.0,
    "streak_bonus": 0.06
  }
}
```

---

## 🔥 주요 특징

* 규칙 기반 + AI 혼합 구조 (안전성 확보)
* Contextual Bandit 기반 추천
* 사용자 행동 기반 학습 구조
* RL(MDP) 확장 가능 설계

---

## ⚠️ 현재 한계

* DB 미연동 (in-memory 사용)
* 사용자별 모델 분리 없음
* 장기 RL 미구현
* 푸시 알림 미구현

---

## 🚧 향후 개선 방향

* PostgreSQL 연동
* 사용자별 Bandit 모델
* Thompson Sampling / LinUCB 적용
* Reinforcement Learning (MDP) 확장
* 푸시 알림 및 스케줄러 추가

---

## 💡 한 줄 설명

> 사용자 상태 기반으로 운동을 추천하고, 수행 결과를 학습하여 점점 더 개인화되는 AI 운동 추천 시스템
