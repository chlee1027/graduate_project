# 🏋️ Fitness AI Recommender (RL 기반 운동 추천 시스템)

## 📌 프로젝트 개요

사용자의 건강 정보, 컨디션, 환경을 기반으로 **개인화된 운동을 추천하는 AI 코칭 시스템**입니다. 
초기에는 **규칙 기반 + Contextual Bandit**으로 추천을 수행하며, 전문적인 운동 지표(RPE, MET, 세트당 휴식 시간)를 학습 데이터로 활용합니다.

---

## 🎯 주요 성과 및 업데이트 (2026.05.17)

### 🧬 과학적 운동 데이터베이스 및 칼로리 계산
*   **42종의 전문 운동 플랜**: PostgreSQL DB에 42개의 고품질 운동 데이터를 이식하고 AI 엔진과 연동했습니다.
*   **칼로리 소모량 계산기**: DB의 **MET 지수**와 사용자 **체중**을 결합한 과학적 계산 공식을 적용했습니다.

### 👤 마이페이지 및 사용자 프로필 관리
*   **정보 수정 기능**: 키, 몸무게, 운동 목표 등을 언제든 수정할 수 있는 마이페이지를 새롭게 구축했습니다.
*   **UI 클린업**: 홈 화면의 복잡한 통계 수치들을 마이페이지로 이동시켜 사용자 경험을 최적화했습니다.

### ⏱️ 독립형 단계별 타이머 시스템
*   **WORK/REST 분리**: 운동 페이즈와 휴식 페이즈를 명확히 구분한 독립 타이머 시스템을 구축했습니다.
*   **수행 검증 로직**: 시간 기반(70%), 횟수 기반(50%)의 세트별 최소 이수 시간을 강제하여 데이터 신뢰성을 확보했습니다.

### 🌐 원격 접속 환경 (Tunneling)
*   **외부 환경 테스트 지원**: `localtunnel`과 `Expo Tunnel`을 활용하여 장소에 구애받지 않고 앱을 테스트할 수 있는 네트워크 환경을 구축했습니다.

---

## ⚙️ 기술 스택

### Frontend
*   **Framework**: Expo (React Native SDK 54+) + TypeScript
*   **State**: Zustand (User & Session store)
*   **Native**: Expo Notifications, Device, Constants, DateTimePicker, localtunnel

### Backend
*   **Framework**: FastAPI (Python 3.10+)
*   **Database**: PostgreSQL (Docker-Compose)
*   **AI Engine**: Contextual Bandit (ε-greedy)

---

## 🚧 향후 과제 (Next Priority)

1.  **UI 정밀 교정**: 헤더 버튼 및 아이콘들의 정중앙 정렬(Vertical/Horizontal) 미세 조정.
2.  **인앱 가이드 영상 플레이어**: 외부 링크 이탈 없이 앱 내에서 운동 가이드를 시청하는 기능.
3.  **프로덕션 클린업**: 개발용 테스트 로직(5초 통과 등) 및 디버그 버튼 제거.

---
*Developed as a Graduate Project (Fitness AI Recommender)*
