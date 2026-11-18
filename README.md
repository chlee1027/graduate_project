# Fitness AI Recommender (AI PT 코치 운동 추천 시스템)

**데모**: https://fitness-ai-coach-seven.vercel.app (웹, 휴대폰 브라우저에서도 열린다. 첫 요청은 서버가 깨어나느라 5초 안팎 걸린다)

## 프로젝트 개요

사용자의 건강 정보, 컨디션, 환경 및 과거 운동 이력을 기반으로 **개인화된 운동을 추천하는 AI 코칭 시스템**입니다.
단순한 부위별 안배를 넘어 전문 PT 코치처럼 세부 근육 단위의 균형을 맞추고, Claude API를 활용한 실시간 코칭 가이드를 제공합니다.

---

## 주요 기능

### 1. AI 스마트 가이드

*   **실시간 PT 코칭**: 추천된 운동에 대해 Claude가 상세한 설명, 타겟 근육(근성장/체형교정 등), 부상 방지 팁을 생성합니다.
*   **유튜브 연동**: 생성된 답변에서 검색 키워드를 뽑아 유튜브 검색 결과로 바로 연결합니다.

### 2. 스톱워치와 칼로리 트래킹

*   **스톱워치 모드**: 카운트다운 대신 실제 운동 시간을 재는 카운트업 방식입니다.
*   **목표 제시**: 운동 화면에 오늘의 목표(세트/회/초)를 함께 보여 줍니다.
*   **MET 기반 칼로리 계산**: `MET x 3.5 x 체중(kg) / 200 x 실제 운동 시간(분)` 으로 계산합니다. 운동마다 `met_value` 를 따로 두었습니다.

### 3. 운동 히스토리와 운동 DB

*   **최근 운동 기록**: 마이페이지에서 이번 주에 수행한 운동 종류, 소요 시간, 소모 칼로리를 확인합니다.
*   **운동 DB 73종**: 기본 41종에 헬스장 변형 운동과 저강도 변형(`가볍게 하기`)을 더해 73종입니다. 변형은 `scripts/seed_db.py` 의 `generate_variations()` 가 만듭니다.
*   **추천 쏠림 완화**: 최근 7일간 수행한 소분류 근육을 보고 덜 쓴 부위에 가산점을 주며, 점수가 같은 후보 중에서는 무작위로 고릅니다.

### 4. 추천 알고리즘 v3.0 (PT 코치 모드)

*   **세부 근육 단위 분석**: 대분류 부위뿐 아니라 소분류 근육(햄스트링, 광배근 등)의 수행 이력을 추적합니다.
*   **컨디션 반영**: 추천 화면에서 오늘 피로도(0에서 5)와 운동할 수 있는 시간을 고르면, 피로도와 숙련도에 따라 세트, 횟수, 휴식 시간, 목표 RPE를 그 자리에서 조정하고 시간 안에 끝나는 운동만 후보로 남깁니다.
*   **통증 처리 두 단계**: 직접 금기 부위는 후보에서 제외하고, 간접 영향권(예: 손목 통증일 때의 상체 중량 운동)은 감점으로 뒤로 밉니다.
*   **hybrid LinUCB 추천**: 모든 사용자가 함께 배우는 모형과 사용자마다 따로 배우는 작은 모형으로 후보마다 보상(완료 여부, RPE, 통증)을 예측하고, 덜 해 본 조합에 탐색 가산점을, 최근 덜 한 부위에 균형 가산점을 더해 고릅니다. 처음 쓰는 사용자도 다른 사용자의 기록으로 고릅니다.

### 5. 크로스 플랫폼 지원 (Web & Mobile)

*   React Native Web과 Tailwind CSS(`global.css` 컴파일 방식)를 연동하여 모바일 앱과 웹 브라우저에서 같은 화면을 씁니다.
*   웹 환경에서 발생하던 푸시 알림 및 모달 경고창 충돌을 처리했습니다.

---

## 기술 스택

### Frontend

*   **Framework**: Expo (React Native SDK 54) + React Native Web
*   **Routing**: Expo Router (File-based routing)
*   **Styling**: Tailwind CSS + NativeWind
*   **Animation**: React Native Reanimated
*   **State Management**: Zustand
*   **Networking**: Axios

### Backend

*   **Framework**: FastAPI (Python 3.12)
*   **Database**: PostgreSQL (Docker Compose)
*   **추천 엔진**: hybrid LinUCB(Li et al., WWW 2010, `LINUCB_ALPHA = 1`) + 부위 균형 가중치(`BALANCE_WEIGHT = 0.25`), `app/services/linucb.py`. 예전 ε-greedy 밴딧은 `RECOMMENDER=eps_greedy` 로 되돌릴 수 있다
*   **LLM 연동**: Claude API (`anthropic` Python SDK, 기본 `claude-opus-5-5`, 노력 수준 `low`). 모델·노력 수준은 환경 변수 `CLAUDE_MODEL`·`CLAUDE_EFFORT` 로 바꾼다. 공개 데모에서 남용을 막으려고 IP 당 한 시간 10번, 하루 전체 200번으로 호출을 제한한다(`CHATBOT_PER_IP_PER_HOUR`·`CHATBOT_PER_DAY`).

---

## 실행 방법

### 1. 데이터베이스

```bash
docker compose up -d
```

### 2. 백엔드

```bash
pip install -r requirements.txt
cp .env.example .env          # DATABASE_URL 과 ANTHROPIC_API_KEY 를 채운다
python -m scripts.seed_db     # 운동 73종 적재
uvicorn app.main:app --reload
```

`seed_db` 는 반드시 `-m` 으로 부른다. `python scripts/seed_db.py` 로 부르면 저장소 루트가 모듈 경로에 들어가지 않아 `No module named 'app'` 이 난다.

**주의: `seed_db` 는 빈 데이터베이스에 처음 세울 때만 부른다.** 이 스크립트는 맨 위에서 `exercise_plans` 테이블을 drop 하고 전체 삭제부터 한다. 운동 기록이 쌓인 뒤에 부르면 `exercise_logs.plan_id` 외래키에 걸려 실패하거나 데이터를 잃는다.

### 3. 기존 데이터가 있는 경우

`users.injuries` 와 `users.equipment` 는 쉼표로 이은 문자열이 정본이다. 예전에 온보딩이 JSON 배열로 쓴 행이 섞여 있으면 아래로 정리한다. 읽는 쪽은 두 형식을 모두 받으므로 돌리지 않아도 동작은 하지만, 저장된 값도 한 형식으로 맞춰 두는 편이 낫다.

```bash
python -m scripts.migrate_user_list_fields          # 무엇이 바뀌는지 보기만 한다
python -m scripts.migrate_user_list_fields --apply  # 실제로 바꾼다
```

추천 엔진의 모형 표 `linucb_shared`·`linucb_users` 는 서버가 뜰 때 `create_all` 이 없으면 만든다. 기존 표와 기록은 건드리지 않고, 모형은 빈 상태에서 시작해 보상이 들어올 때마다 쌓인다.

### 4. 프런트엔드

```bash
cd frontend
npm install
npx expo start --web
```

웹 화면의 스타일은 `frontend/global.css` 를 Tailwind 로 컴파일한 `frontend/output.css` 를 쓴다. 화면의 `className` 을 바꾸면 `npm run css` 로 다시 만들고 함께 커밋한다(배포 빌드는 이 파일을 다시 만들지 않는다). 공통 부품과 색은 `frontend/src/ui/index.tsx`·`frontend/tailwind.config.js` 에 모아 두었다.

웹은 `http://127.0.0.1:8000` 을 직접 부르고, 모바일 기기는 `frontend/src/api/client.ts` 의 터널 주소를 씁니다. 기기로 시연할 때는 그 주소를 현재 터널 주소로 바꿔야 합니다.

---

## 배포 (Vercel + Neon)

웹 화면과 API 를 Vercel 프로젝트 하나에 올린다. 같은 주소라 터널이나 CORS 설정이 필요 없다.

*   **웹**: `frontend` 를 `npx expo export --platform web` 으로 정적 파일(`frontend/dist`)로 만든다. 배포 빌드에서는 API 를 같은 주소의 `/api` 로 부른다(`frontend/src/api/client.ts`).
*   **API**: `api/index.py` 가 FastAPI 앱을 Vercel Python 함수로 낸다. `vercel.json` 이 `/api/*` 를 이 함수로, 나머지 경로를 `index.html` 로 보낸다. Vercel 이 FastAPI 를 자동 인식해 모든 경로를 함수로 보내지 않도록 `"framework": null` 을 둔다.
*   **DB**: Vercel Marketplace 의 Neon(Free). 연결하면 `DATABASE_URL` 이 들어온다. 함수 리전은 DB 와 같은 미국 동부(`iad1`). 함수는 요청마다 연결을 열고 닫는다(`app/db/database.py`).
*   **환경 변수**: `DATABASE_URL`(Neon 이 넣음), `ANTHROPIC_API_KEY`, `CLAUDE_MODEL`(데모는 `claude-haiku-5-5`), `RATE_LIMIT_SALT`(임의 값).
*   **처음 한 번**: 빈 DB 에 `python -m scripts.seed_db` 를 Neon 의 비풀링 주소(`DATABASE_URL_UNPOOLED`)로 돌려 운동 73종을 넣는다. 다른 표는 함수가 처음 뜰 때 `create_all` 이 만든다.
*   GitHub `main` 에 push 하면 Vercel 이 다시 배포한다.

---

## 시간대 처리

기록(`created_at`)은 `timestamptz` 로 UTC 에 저장하고, 스트릭과 주간 활동은 한국 날짜로 셉니다. 변환은 `app/core/timezone.py` 한곳에 모여 있습니다.

PostgreSQL 의 `timezone(zone, x)` 는 인자 타입에 따라 방향이 뒤집힙니다. `timezone('Asia/Seoul', timestamptz)` 는 서울 벽시계 값을 주지만, `timezone('Asia/Seoul', timestamp)` 는 그 값을 서울 시각으로 해석해 버립니다. 두 번 겹쳐 걸면 9시간을 더하는 대신 빼게 되므로 한 번만 겁니다.

---

## 추천 방식 시뮬레이션 비교

가상 사용자 200명(seed 마다)에게 앱의 후보 생성·보상 코드를 그대로 써서 추천 방식을 비교했다. 기본 시나리오, 시험 seed 10개 평균:

| 방식 | 세션당 기대 보상 | regret |
|---|---|---|
| 무작위 | 0.977 | 0.174 |
| 예전 앱 (ε-greedy, ε=0.2) | 0.964 | 0.185 |
| LinUCB 공유 (α=1) | 1.014 | 0.133 |
| LinUCB hybrid (α=1) | 1.039 | 0.108 |
| hybrid + 부위 균형 (λ=0.25), 지금 앱 | 1.034 | 0.114 |
| 오라클 (상한) | 1.144 | 0 |

예전 방식은 이미 해 본 운동에 묶여 무작위보다 낮았고(10/10 seed), hybrid LinUCB 는 네 시나리오 모두에서 가장 높았다. 앱에는 부위 균형 가중치를 더한 판을 넣었다. 운동 부위가 앱의 손 규칙만큼 고르게 퍼지고, 기대 보상은 hybrid 보다 0.005 낮다. 가정·설계·한계는 [docs/simulation_eval.md](docs/simulation_eval.md).

```bash
pip install -r requirements-dev.txt   # 시뮬레이션·시험용 패키지까지
python -m pytest tests
python -m sim.run_experiments   # 16코어에서 약 12분
python -m sim.plot_results
```

---

## 향후 과제

1.  **인앱 가이드 영상 플레이어**: 외부 링크 이탈 없이 앱 안에서 운동 가이드를 시청하는 기능.
2.  **스트릭 시각화**: 연속 운동 일수를 잔디(GitHub-style) 차트로 표현.

> 2026-11-18 에 화면을 다시 짜면서 「UI 정밀 교정(기기 크기별 여백·정렬)」은 끝냈다. 웹은 최대 480px 폭으로 가운데 두고, 색·간격은 `frontend/src/ui/index.tsx` 한곳에서 정한다.

---
*Developed as a Graduate Project (Fitness AI Recommender)*
