# 🏋️ Fitness AI Recommender (AI PT 코치 운동 추천 시스템)

## 📌 프로젝트 개요

사용자의 건강 정보, 컨디션, 환경 및 과거 운동 이력을 기반으로 **개인화된 운동을 추천하는 AI 코칭 시스템**입니다. 
단순한 부위별 안배를 넘어 전문 PT 코치처럼 세부 근육 단위의 균형을 맞추고, Gemini AI를 활용한 실시간 코칭 가이드를 제공합니다.

---

## 🎯 주요 성과 및 핵심 기능 (Latest Updates)

### 🤖 1. Gemini AI 스마트 가이드 도입 (NEW)
*   **실시간 PT 코칭**: 추천된 운동에 대해 Gemini AI가 실시간으로 분석하여 상세한 설명, 타겟 근육(근성장/체형교정 등), 부상 방지 팁을 제공합니다.
*   **유튜브 다이렉트 연동**: AI가 해당 운동에 가장 적합한 검색 키워드를 생성하여 한 번의 클릭으로 유튜브 가이드 영상으로 연결합니다.

### ⏱️ 2. 정밀 스톱워치 및 칼로리 트래킹
*   **스톱워치 모드**: 압박감을 주는 카운트다운 대신, 실제 운동 시간을 측정하는 스톱워치 인터페이스(Count-up)로 개편했습니다.
*   **동적 목표 제시**: 운동 화면에 '오늘의 목표(세트/회/초)'를 명확히 제시하여 동기를 부여합니다.
*   **MET 기반 정밀 칼로리 계산**: 국제 표준인 MET 지수와 사용자의 체중, 실제 측정된 운동 시간을 결합하여 고도로 정밀한 소모 칼로리를 계산합니다.

### 📊 3. 프로필 운동 히스토리 및 데이터 고도화
*   **최근 운동 기록 📜**: 마이페이지에서 이번 주에 수행한 운동 종류, 소요 시간, 소모 칼로리를 직관적으로 확인할 수 있습니다.
*   **대규모 운동 DB 확장 (총 73종)**: 초급자용 저강도 변형 운동(가볍게 하기 등)과 헬스장/홈트 옵션을 대폭 확장하여 추천의 다양성을 극대화했습니다. 특정 운동(예: 페이스 풀)만 반복해서 추천되는 현상을 완벽히 해결했습니다.

### 🧠 4. 추천 알고리즘 v3.0 (PT 코치 모드)
*   **세부 근육 단위 정밀 분석**: 대분류 부위뿐만 아니라 소분류 근육(햄스트링, 광배근 등)의 수행 이력을 추적하여 균형 잡힌 신체 발달을 유도합니다.
*   **가중치 밸런스 조정**: 사용자가 입력한 피드백(RPE, 완료여부 등)이 알고리즘에 더 잘 반영되도록 근육 균형 점수와 사용자 선호도 점수의 가중치를 최적화했습니다.

### 🌐 5. 크로스 플랫폼 지원 (Web & Mobile)
*   React Native Web과 Tailwind CSS(`global.css` 컴파일 방식)를 완벽히 연동하여 모바일 앱뿐만 아니라 웹 브라우저에서도 동일하게 미려한 UI/UX를 경험할 수 있습니다.
*   웹 환경에서 발생하던 푸시 알림 및 모달 경고창 충돌 이슈를 모두 해결했습니다.

---

## ⚙️ 기술 스택

### Frontend
*   **Framework**: Expo (React Native SDK 54+) + React Native Web
*   **Routing**: Expo Router (File-based routing)
*   **Styling**: Tailwind CSS + NativeWind
*   **Animation**: React Native Reanimated
*   **State Management**: Zustand
*   **Networking**: Axios

### Backend
*   **Framework**: FastAPI (Python 3.12+)
*   **Database**: PostgreSQL (Docker-Compose)
*   **AI Engine**: Contextual Bandit (ε-greedy) 알고리즘
*   **LLM Integration**: Google Gemini API (`gemini-1.5-flash` / `gemini-1.5-pro`)

---

## 🚧 향후 과제 (Next Priority)

1.  **UI 정밀 교정**: 디바이스 크기(모바일/웹)에 따른 컴포넌트 여백 및 정렬 최적화.
2.  **인앱 가이드 영상 플레이어**: 외부 링크 이탈 없이 앱 내에서 운동 가이드를 시청하는 기능.
3.  **스트릭(Streak) 시스템 시각화**: 연속 운동 일수를 시각적으로 멋지게 표현하는 잔디심기(GitHub-style) 차트 도입.

---
*Developed as a Graduate Project (Fitness AI Recommender)*
