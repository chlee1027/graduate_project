# 🏋️ Fitness AI Recommender (RL 기반 운동 추천 시스템)

## 📌 프로젝트 개요

사용자의 건강 정보, 컨디션, 환경을 기반으로 **개인화된 운동을 추천하는 AI 코칭 시스템**입니다.
초기에는 **규칙 기반 + Contextual Bandit**으로 추천을 수행하고,
데이터가 축적되면 **Reinforcement Learning (MDP)**으로 확장 가능한 구조입니다.

---

## 🎯 최근 업데이트 (2026.05.16)

*   **연속 운동(Streak) 시스템**: 타임존(KST)을 지원하는 정교한 연속 운동일수 계산 로직 도입.
*   **액티브 레스트(Active Rest)**: 컨디션에 따라 스트레칭으로 전환 가능한 유연한 추천 시스템.
*   **브랜드 리뉴얼**: 사용자 친화적인 '코치(Coach)' 아이덴티티 적용 및 홈 대시보드 개편.
*   **UI/UX 혁신**: 온보딩 캐릭터 카드 UI 및 Reanimated 기반 리퀴드 슬라이더 적용.

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
│  ├─ db/               # Database models & migrations
│  ├─ routers/          # API (onboarding, recommend, log, user, debug)
│  ├─ services/         # Logic (recommender, streak, reward)
│  └─ main.py           # Entry point
│
├─ frontend/            # Mobile App (Expo)
│  ├─ app/              # Expo Router screens (Home, Onboarding, Recommend)
│  └─ src/
│     ├─ api/           # Axios client & endpoints
│     ├─ store/         # Zustand global state
│
├─ docker-compose.yml   # PostgreSQL setup
└─ README.md
```

---

## 📊 핵심 기능

1.  **스마트 온보딩**: 캐릭터 기반 UI로 사용자 신체 정보 및 목표 수집.
2.  **AI 맞춤 추천**: 위치, 피로도 및 **컨디션(Active Rest)**을 고려한 최적의 플랜 제공.
3.  **습관 형성(Streak)**: 연속 운동일수(🔥) 트래킹을 통한 동기 부여.
4.  **시각적 가이드**: 각 운동별 맞춤 유튜브 가이드 영상 연결.

---

## 🚧 향후 과제

*   ⏱️ **워크아웃 세션**: 실시간 타이머 및 세트별 진행률 체크 기능.
*   📈 **데이터 시각화**: 주간 운동 성과 리포트 및 성장 대시보드.
*   🧹 **최종 정리**: 개발용 디버그 도구 제거 및 프로덕션 환경 최적화.
