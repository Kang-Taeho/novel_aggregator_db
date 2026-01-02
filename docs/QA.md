## QA & Test Portfolio — Novel Aggregator

이 문서는 Novel Aggregator 프로젝트의 **테스트 전략 / 자동화 구성 / 안정화 경험 / CI 운영**을 정리한 QA 포트폴리오입니다.  
**어떤 리스크를 어떤 방식으로 줄였는지**를 증거 중심으로 보여주는 것입니다.

---

### Quick Summary
- **Test scope**: Unit / Integration / E2E(API) / Postman(Newman) / Data Quality
- **Key risks**: 무한 스크롤·동적 렌더링 타임아웃, Selenium 세션 폭주, 중복/손상 데이터
- **CI outputs**: JUnit(XML), Data Quality Markdown 리포트
- **Evidence**: 아래 링크 참고  
  - [Selenium 안정화 로그](./selenium_evidence.md)  
  - [Data Quality 개선 로그](./data_evidence.md)

--- 

## 1) Quality Goals

### 품질 목표
* 플랫폼별 동적/정적, HTML 차이를 고려해 **스크래퍼/파서의 안전성/속도를 확보**할 것
* 데이터 품질 테스트를 통해 **데이터가 중복/손상 여부를 검사**할 것
* KP(Selenium)가 장시간 실행 중에도 **세션 폭탄/렌더러 타임아웃을 최소화**할 것
* 실패가 발생해도 **원인 추적 가능**(지표/샘플 URL/에러 메시지)할 것

---

## 2) Run tests 
### 방법
- Prerequisites : README 참고
- one-shot 실행
  - `./tests/scripts/run_all.ps1`(Window) : Unit / Integration / E2E / Postman test
  - `pytest tests/data/test_data_quality.py` : Data test
- output : tests/reports/...

### 개선
[selenium_evidence.md](./selenium_evidence.md)
1. selenium 무한 스크롤 처리 속도 향상
2. selenium renderer timeout / execute_script 실패 -> 500 Server Error 개선
3. selenium SessionNotCreated / No nodes support capabilities -> 세션 폭주 개선

[data_evidence.md](./data_evidence.md)
1. 데이터 결측치 탐색
2. 데이터 중복(중복 저장) 삭제
3. 데이터 비효율적 저장량 임계치가 넘을 시 데이터 스키마 개편 고려

--- 
## 3) Test Pyramid (Unit / Integration / E2E)

### 3.1 Unit Tests
**대상**
* `normalize.py`: 플랫폼별 다른 표현의 연령,연재상태,숫자
* 각 플랫폼 `parser.py`: HTML → dict 변환 로직, 필드/타입 (단, 실제 HTML 사용)
* (NS) `scraper.py`: 각 페이지의 스레드 결과 소설ID를 합치는 로직 

**검증 포인트**
* 다양한 입력(빈 값/None/문자열 숫자/콤마 포함) 처리되는지 
* 누락 필드가 있어도 크래시 없이 “skipped” 처리되는지 
* 변환 결과가 저장 스키마와 필드/타입 일치하는지

### 3.2 Integration Tests
**대상**
* DB upsert :  novels / novel_sources
* `orchestrator.py` : parser/scraper 모듈과 DB 연결 처리 로직
* `/scheduler/main.py` : APScheduler 작동

**검증 포인트**
* **Idempotency** : 같은 입력을 여러 번 넣어도 중복 row가 생기지 않는지
* Update 정책 : episode\view_count\completion_status 등 변경 필드가 갱신되는지
* scheduler option : 동시 실행, 중복 실행 등 제대로 실행되는지

### 3.3 E2E Tests
**대상**
* FastAPI `/jobs/scrape` : 호출 → 파이프라인 실행 → 결과 지표(JSON) 반환
* 각 플랫폼 `scraper.py` : smoke 테스트로 selenium/request 작동 확인

**검증 포인트**
* API 응답 구조가 표준화되어 있는지
  * `total/success/failed/skipped/duration_ms/errors_sample`
* 실패(500) 상황에서도 **에러가 JSON으로 반환**되는지  
  (Newman에서 `Unexpected token 'I'` 같은 JSONError 방지)
* Smoke 모드로 핵심적인 기능 테스트

---

## 4) Postman/Newman E2E

### 1️⃣ 목적
API 품질을 보장하기 위해 Postman 컬렉션을 기반으로
- 기능 검증 (Functional Test)
- 회귀 테스트 (Regression Test)
를 수행하며, Newman을 통해 CI 리포트 생성

### 2️⃣ 테스트 범위
- 주요 엔드포인트에 대한 상태 코드/응답 스키마 확인
- 실 서비스 기준 selenium/request 대량 처리 기능 반복 확인
- 오류 응답 및 엣지 케이스 확인

### 3️⃣ 리포트 생성 위치
* JUnit(XML): `tests/postman/reports/newman-results.xml`
* 단위+통합+E2E HTML report: `tests/postman/reports/pytest-junit.html`

### 4️⃣ 개발자 로컬 실행 방법
```
uvicorn src.apps.api.main:app --reload --host 0.0.0.0 --port 8000 --log-level info 
./tests/scripts/run_all.ps1
```

---

## 5) Selenium 안정화 전략
### 5.1 docker container 4개
Selenium WebDriver 병렬 실행용 컨테이너를 4개로 제한해 안정성을 우선합니다(호스트 리소스 한계 고려) <br>
핵심 설정(예: docker-compose.yml)
- `shm_size:"2g"` : render timeout 완화
- `SE_NODE_MAX_SESSION=1` : 컨테이너 당 Webdriver 세션 1개로 고정
- `SE_NODE_OVERRIDE_MAX_SESSIONS=true` : 자동 병렬 실행 방지(안정성 우선)

### 5.2 selenium grid 전략
문제 
- 작품당 Webdriver 생성으로 과도한 병렬 실행
- `SessionNotCreatedException`및 세션 폭탄 발생 <br>

전략 
- 전체 작업을 청크 단위로 4개로 분리 
- 4개의 webdriver(=docker container)에서 **동시 실행 + 컨테이너 내부는 순차 처리**

### 5.3 Retry & timeout
- `execute_script`에 retry wrapper 적용
- 무한스크롤은 최대 수행 시간을 두어 무한 대기를 방지 
- 실패는 `errors_sample`로 샘플을 남겨 재현 가능하게 유지

---

## 6) Data Quality Tests
 Job 실행이 끝날 때마다 MySQL/Mongo에서 **품질 지표**를 쿼리로 뽑아 JSON/Markdown로 저장

### 품질 지표
- 이상치 통계 
	- (mysql) `author_name`, `genre`, `mongo_doc_id` : NULL 검사
	- (mysql) `view_count` , `episode_count` : 음수/0 검사
    - (mongo) `description` : NULL 검사 
- 결측치 검사
	- (mysql) `job_runs`의 total/ failed, skipped 비율
- 중복 비율
	- (mongo) `description` 중복 비율
	- (mysql) 같은 플랫폼 같은 소설 중복 비율 
- Rule 위반 목록
	- (mysql/mongo)  `novels` / `novel_meta` 1:1 매칭 위반 목록

### 대응 방안
- 이상치 통계 
	- NULL / 0 / 음수 값이 있을 경우 해당 소설 목록 검사
- 결측치 검사
	- failed : 실패 원인 분석
    - skipped : 19세 이상 소설은 개인정보로 인해 접근 불가(개인정보/정책) <br>
       단, 전 검사 대비 skipped가 급증하면 소설 목록/필터 조건을 점검
- 중복 비율
	- description 중복 : 시시리즈/단행본 등으로 발생 가능하나 저장공간을 과도하게 차지하면 삭제/정책 조정 고려
	- 같은 플랫폼 같은 소설 중복 : 해당 소설 데이터 삭제 및 원인 파악
- Rule 위반 목록
	- Rule 위반 데이터 : 해당 소설 데이터 삭제 및 원인 파악

### 리포트 생성 위치
* Markdown : `tests/reports/data_quality_report.md`






