#  Novel Aggregator DB

여러 **웹소설 플랫폼의 작품 메타데이터를 수집 → 정규화 → 저장 → API 제공**까지 수행하는 파이프라인 프로젝트입니다.  
MySQL + MongoDB 기반으로 동작하며, API 트리거 및 스케줄러 실행을 지원합니다.

- **지원 플랫폼:** KakaoPage(KP), NaverSeries(NS)
- **수집 모드:** 전체 수집(Full Scan)
- **테스트 자동화:** Postman / Newman E2E + pytest 통합 테스트

---

##  Why

### 문제
플랫폼별 AI 추천, 배너 운영, 고착화된 랭킹 구조로 인해  
**정형화된 작품 노출 → 독자 선택 폭 제한** 문제가 존재합니다.

### 목표
사용자 취향에 맞는 **새로운 추천 서비스 기반 데이터 확보**를 위해  
여러 플랫폼의 소설 정보를 안정적으로 수집·정규화하는 것이 목적입니다.

---

## ✅ QA Highlights

| 항목 | 설명 |
|------|------|
| QA Guide | `docs/QA.md` |
| Test Report | `docs/test-report.md` |

### 1️⃣ E2E Job Trigger 검증 (Postman / Newman)
- `/jobs/scrape` 호출 → 실제 파이프라인 실행
- 응답에 `total / success / failed / skipped / duration_ms / errors_sample` 포함 여부 검증
- 실패 시에도 JSON 표준 에러 형식 반환 확인

### 2️⃣ KP Selenium 안정성 검증
- standalone-chrome 4개 환경에서 세션 재사용 + retry + timeout 상한 전략 검증
- 무한스크롤 및 상세 파싱 정상 동작 확인

### 3️⃣ DB Upsert / Idempotency 검증
- 동일 작품 반복 수집 시 중복 생성 방지
- 변경 필드만 갱신(MySQL novel + novel source)
- MongoDB 설명/키워드 Upsert 안정성 확인

---

## 📑 Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project-Structure](#project-structure)
- [Setup](#setup)
- [API](#api)
- [Jobs](#jobs)
- [License](#-license)

---
<a id="features"></a>
## 🚀 Features

### 🔍 Scraping
- **KakaoPage:** 동적 페이지 / 무한스크롤
- **NaverSeries:** 정적 페이지 / 페이지네이션

### 🧩 Parsing & Normalization
- 플랫폼별 다른 메타데이터를 **공통 스키마로 정규화**
- [공통] <br>
  title, author_name, genre, platform_item_id, age_rating, description, view_count, completion_status
- [미지원] <br>
  (kakao page) keywords, episode_count <br>
  (naver series) first_episode_date, keywords 

### 🗄 Storage
- **MySQL:** 정형 메타 저장 <br>
  DB Model : [schema_and_seed.sql](scripts/schema_and_seed.sql) <br>
  DB Data  : backup-data.sql(KP,NS 전체 소설 데이터 2025년 9월 기준)
- **MongoDB:** 유연 필드 저장(description, keywords 등) <br>
  DB Model : [mongo_init.js](scripts/mongo_init.js)    <br>
  DB Data : 설명은 저작권 배포에 걸릴 여지가 있으므로 생략하겠습니다.

### ⚙️ Orchestration
- 플랫폼별 병렬 처리 전략 적용
- [KP] : selenium grid와 비슷한 방식을 적용한 병렬처리
- [NS] : thread를 사용한 병렬처리

### 📈 Observability
- 로그 수집 : 중요 작업이 끝날 때마다 log 출력
- 실행 기록 저장 : job_runs 테이블(MySQL)에 작업 결과 저장 

---
<a id="architecture"></a>
## 🏗 Architecture
```text
Trigger (API / Scheduler)
   ↓
Scrape IDs  (KP: Scroll | NS: Paging)
   ↓
Fetch Detail HTML
   ↓
Parse & Normalize
   ↓
Upsert → MySQL / MongoDB
```
---
<a id="tech-stack"></a>
## 🛠 Tech Stack

- **Python** — 데이터 크롤링에 적합
- **FastAPI** — Job Scheduler & API 제공
- **MySQL** — 정형 메타데이터 저장
- **MongoDB** — 비정형 메타데이터 저장
- **Selenium** — 동적 페이지 접근 및 크롤링
- **Postman / Newman** — E2E 자동화
- **Docker** — Infra & Selenium 병렬 실행 환경

---
<a id="project-structure"></a>
## 📂 Project Structure
```text
novel-aggregator/
├─ scripts/                # DB / Docker / 초기화 스크립트
├─ src/
│  ├─ core/                # 공통 설정 / 유틸 (환경변수, 재시도 등)
│  ├─ data/
│  │  ├─ database.py
│  │  ├─ models.py         # ORM 모델
│  │  ├─ repository.py     # MySQL upsert
│  │  └─ mongo.py          # Mongo 연결 & upsert
│  ├─ scraping/
│  │  ├─ base/             # 공통 scraping 기반 (browser / session)
│  │  └─ sites/            # 플랫폼별 Scraper & Parser (KP / NS)
│  ├─ pipeline/
│  │  ├─ normalize.py      # 데이터 정규화
│  │  └─ orchestrator.py   # 파이프라인 실행 제어
│  └─ apps/
│     ├─ api/              # FastAPI (jobs API)
│     └─ scheduler/        # APScheduler (크론 작업)
├─ tests/                  # 테스트
├─ .env.example            # 환경 변수 템플릿
└─ pyproject.toml          # 의존성 관리
```

---
<a id="setup"></a>
## ⚡ Setup

### 1️⃣ Environment 설정
1) `.env.example` → `.env` 복사 후 값 설정
- MySQL DSN  
- Mongo URI  
- Selenium Remote URL X4
2) 가상 환경 설치
  ```python
python -m venv .venv     # 가상환경 설치
.venv\Scripts\activate   # Window 가상환경 활성화
pip install .            # pyproject.toml 기준으로 패키지 설치
```

### 2️⃣ Infra (Docker)
1) **Docker container 설치**
- docker-compose.yml의 DB이름 및 password 변경 권장
```bash
# docker-compose.yml이 있는 디렉토리에서 실행
docker compose up -d 
```
2) **DB initialization**
- docker 생성 시 자동으로 데이터 스키마가 생성되지만 실패 시 수동으로 생성
```bash
# MySQL : scripts/schema_and_seed.sql
docker cp scripts/schema_and_seed.sql (DB이름):/schema_and_seed.sql
docker exec -i (DB이름) sh -lc "mysql -uroot -p(비번) < /schema_and_seed.sql"

# MongoDB: scripts/mongo_init.js
docker cp scripts/mongo_init.js (DB이름):/mongo_init.js
docker exec -i novels-mongo mongosh /mongo_init.js
```

### 3️⃣ API 실행
```bash
uvicorn src.apps.api.main:app --host 0.0.0.0 --port 8000
```
1) **scheduler 사용** <br>
CRON 환경변수 기반 CronTrigger 스케쥴 실행 
2) **테스트 환경 전용 실행** <br>
SCHED_TEST_INTERVAL 환경변수 기반 IntervalTrigger 스케쥴 실행 <br>
단, 운영 시 비활성화(0으로 초기화) 권장

---
<a id="api"></a>
## 🔌 API
####  Endpoint
```
POST /jobs/scrape
```
#### Param
```
platform_slug:
- KP = kakaopage
- NS = naverseries
```
#### Response (예시)
```
{
  "platform_slug": "KP",
  "sc_fn": "run_initial_full",
  "total": 57372,
  "success": 167,
  "failed": 57203,
  "skipped": 2,
  "duration_ms": 123456,
  "errors_sample": [
    { "url": "KP/57439031", "error": "..." }
  ]
}

```

---
<a id="jobs"></a>
## 🔧 Jobs
### NaverSeries (HTTP 기반)
- 네트워크 I/O 중심
- 권장: 8 ~ 16 workers 
스레드 동시 실행 수(max_workers)를 비교적 크게 가져갈 수 있습니다.
너무 크게 잡으면 차단/레이트리밋/네트워크 불안정으로 실패율이 증가할 수 있습니다.

### KakaoPage (Selenium 기반)
- Selenium은 세션/브라우저 리소스가 병목입니다.
- 권장: max_workers == Selenium standalone-chrome 컨테이너 수
- selenium 컨테이너 4개 쓰는 이유
  1. 컨테이너 1개당 크롬 세션 1개 (selenium webdriver 특징)
  2. 전체 작품 하나의 컨테이너로 무한스크롤시 500에러 높은 확률로 발생
  3. 스레드를 위해 여러 크롬 세션을 사용할 시 그에 맞는 컨테이너 수 필수

---
a id="license"></a>
## 📜 License
[TERMS.md](TERMS.md) 참고
- KakaoPage — 저작권 침해 없는 범위 내 허용
- NaverSeries — robots.txt 허용 범위 내 접근 허용
- Novelpia — 일반 UA 크롤링 불가
- Munpia — 일반 UA 크롤링 불가
