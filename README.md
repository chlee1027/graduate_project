# 🏋️ Fitness AI Recommender (RL 기반 운동 추천 시스템)

## 📌 프로젝트 개요

사용자의 건강 정보, 컨디션, 환경을 기반으로 **개인화된 운동을 추천하는 AI 코칭 시스템**입니다.
초기에는 **규칙 기반 + Contextual Bandit**으로 추천을 수행하고,
데이터가 축적되면 **Reinforcement Learning (MDP)**으로 확장 가능한 구조입니다.

---

## 🎯 최근 업데이트 (2026.05.16)

*   **인터랙티브 워크아웃 세션**: 실시간 타이머, 세트 트래커 및 자동 종료 시스템 구현.
*   **성장 엔진**: 누적 운동 기록에 따른 숙련도 자동 승급 시스템 도입.
*   **종합 대시보드**: 주간 활동 현황(타입별 컬러 코딩) 및 누적 통계 시각화.
*   **안티-어뷰징**: 데이터 무결성을 위한 최소 운동 시간(30%) 제한 로직 적용.
*   **운동 라이브러리 확장**: 고강도 3대 운동을 포함한 상급자용 데이터 대거 추가.

---

## ⚙️ 기술 스택

### Frontend
*   **Framework**: Expo (React Native) + TypeScript
*   **Animation**: React Native Reanimated (Liquid UI)
*   **Styling**: NativeWind (TailwindCSS) + Inline Styles (Dynamic UI)

### Backend
*   **Framework**: FastAPI (Python)
*   **Database**: PostgreSQL (Docker)
*   **AI Logic**: Contextual Bandit (ε-greedy) + Progression Service

---

## 📂 프로젝트 구조 (고도화됨)

```text
graduate_project/
│
├─ app/                 # Backend (FastAPI)
│  ├─ db/               # PostgreSQL Models
│  ├─ routers/          # stats, debug, onboarding, recommend, etc.
│  ├─ services/         # progression, streak, candidate_generator
│  └─ main.py           # Entry point
│
├─ frontend/            # Mobile App (Expo)
│  ├─ app/              # workout/[id].tsx (Session), index.tsx (Dashboard)
│  └─ src/
│     ├─ api/           # Axios configuration
│     └─ store/         # Zustand state management
│
└─ README.md
```

---

## 📊 핵심 기능

1.  **지능형 온보딩**: 콤팩트한 단일 화면 UI로 사용자 프로필 구축.
2.  **실시간 운동 가이드**: 타이머와 세트 트래킹을 통한 체계적인 세션 관리.
3.  **성과 시각화**: 주간 활동 차트 및 누적 성취도를 통한 동기 부여.
4.  **능동적 회복**: 컨디션에 따른 스트레칭(Active Rest) 전환 기능.

---

## 🚧 향후 과제

*   📅 **기록 로그 리스트**: 상세 운동 히스토리 확인 기능.
*   📈 **데이터 분석**: 운동 패턴 분석을 통한 장기 목표 달성도 리포트.
*   🧹 **최종 안정화**: 개발용 디버그 도구 제거 및 보안 강화.
