# 🧠 Workout Recommendation Algorithm v2.0

본 문서는 Fitness AI Recommender의 고도화된 운동 추천 알고리즘 설계 및 구현 내용을 설명합니다.

## 1. 개요
기존의 단순 무작위/선호도 기반 추천에서 벗어나, 사용자의 **운동 이력**, **근육 부위별 균형**, **신체 상태(피로도/통증)**를 종합적으로 고려한 2단계 추천 시스템을 도입했습니다.

## 2. 데이터 구조 (Granular Classification)
모든 운동 데이터는 다음과 같이 세분화되어 관리됩니다.
- **Body Part (대분류)**: `legs`, `chest`, `back`, `shoulder`, `arms`, `core`
- **Sub Target (세부 근육)**: 
    - 예: `legs` -> `quadriceps`(대퇴사두), `hamstrings`(햄스트링), `glutes`(둔근), `adductor`(내전근)
    - 예: `chest` -> `upper_chest`(상부), `middle_chest`(중부), `lower_chest`(하부)
- **Difficulty (난이도)**: `low`, `medium`, `high`

## 3. 추천 프로세스 (2-Step Logic)

### Step 1: 타겟 부위 우선순위 결정 (`get_target_parts_priority`)
1. 최근 7일간의 `ExerciseLog`를 전수 조사합니다.
2. 각 대분류 부위별 수행 횟수를 카운트합니다.
3. **수행 횟수가 적은 부위일수록 높은 우선순위 점수**를 부여합니다. 
   - 이를 통해 특정 부위에 치우치지 않는 균형 잡힌 신체 발달(분할 루틴 효과)을 유도합니다.

### Step 2: 후보군 생성 및 가중치 선정 (`generate_candidates`)
1. **필터링**: 장소(Home/Gym), 가용 시간, 보유 장비, 현재 통증 부위를 고려하여 1차 후보군을 추출합니다.
2. **숙련도 조정**: 사용자의 `experience_level`에 따라 세트 수, 반복 횟수, 운동 시간을 실시간으로 최적화합니다.
3. **가중치 부여 (`priority_score`)**: Step 1에서 결정된 부위 우선순위에 따라 각 운동 후보에 가중치 점수를 부여합니다.

### Step 3: 최종 선택 (Contextual Bandit)
1. **Exploitation (활용)**: 우선순위 점수가 높으면서, 과거 사용자가 높은 보상(수행 완료/만족도)을 주었던 운동을 우선 선택합니다.
2. **Exploration (탐색)**: 낮은 확률(`EPSILON`)로 새로운 운동을 추천하여 사용자의 운동 범위를 넓힙니다.

## 4. 기대 효과
- **자동 분할 루틴**: 사용자가 고민하지 않아도 어제 한 부위를 피해 오늘 해야 할 부위를 정확히 추천합니다.
- **개인화된 강도**: 같은 운동이라도 초보자와 숙련자에게 다른 세트/횟수를 제안합니다.
- **부상 방지**: 통증 부위 및 피로도를 실시간 반영하여 오버트레이닝을 방지합니다.

---
*Last Updated: 2026-05-18*
