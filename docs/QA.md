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
	- (mysql) job_runs의 `total`/ `failed` / `skipped` 비율
    - 단 , skipped은 19세 이상 소설의 경우가 포함
- 중복 비율
	- (mongo) `description` 중복 비율
	- (mysql) 같은 플랫폼 같은 소설 중복 비율 
- Rule 위반 목록
	- (MySQL)`novels` ↔ (Mongo)`novel_meta` 1:1 매칭 위반 목록

### Quality 임계값 및 대응 방안
#### 1) 이상치
**임계값**
- NULL 비율 > 0  
  - (MySQL) `author_name`, `genre`, `mongo_doc_id`  
  - (MongoDB) `description`
- 비정상 값 존재  
  - (MySQL) `view_count`, `episode_count` <= 0

**대응방안**
- 플랫폼 DOM/응답 포맷 변경 여부 확인 
- 이상치 발생 레코드(소설) 리스트 추출 및 케이스 분류

#### 2) 결측치
**임계값**
- `failed_count` > 0 
- `skipped_count`가 이전 실행 대비 급증  
  - 단, `skipped`에는 **19세 이상 접근 제한 케이스** 포함

**영향**
- 불필요한 크롤링 시도 증가 → 실행시간/리소스 비용 증가

**대응방안**
- **Failed**
  1. 실패 레코드 단위 주요 원인 분석 (파싱 실패/타임아웃/차단 등)
  2. 재시도 정책 적용 또는 예외 케이스 룰 보강
- **Skipped**
  1. skipped 사유 분류(19+ 제한 / 접근 불가 / 정책 제외)
  2. 19세 이상 컨텐츠는 **Pre-filtering** 적용  
     - Selenium/WebDriver 및 HTTP Request 단계에서 사전 제외

#### 3) 중복(Deduplication / Uniqueness)
**임계값**
- (MongoDB) `description` > (중복 허용 데이터 용량)
    - 단, `description`에는 **같은 소설의 시리즈/단행본 등** 포함
- (MySQL) 동일 데이터 중복 (동일 플랫폼 내 동일 소설에 관한 데이터)

**영향**
- 저장 용량 증가 및 인덱스/쿼리 성능 저하
- 검색/추천/집계에서 중복 노출로 품질 저하

**대응방안**
- **Description**
  1. 중복 패턴 분석 : 시리즈/단행본, 회차 합본 등 중복 유형 분류
  2. 중복제거 Rule: 대표 레코드 유지 + 나머지 제거/병합
- **동일 데이터**
  1. 중복 레코드 단위 주요 원인 분석 (테스트 데이터/중복 코드 실행/ DB 제약 문제 등)
  2. 예외 케이스 룰 보강

#### 4) 정합성 Rule 위반
**임계값**
- (MySQL) `novels` ↔ (MongoDB) `novel_meta` 간 1:1 매핑 불일치 발생 시 

**영향**
- 엔티티 조인 실패 → 다운스트림 테이블/서빙 데이터 품질 저하
- 데이터 누락/중복으로 인한 파이프라인 오류 가능

**대응방안**
- 주요 원인 분속 (키 매핑 오류, 적재 순서 문제, 중복 적재, 삭제 누락 등)
- 잘못된 레코드 정정/삭제 후 재적재

### 리포트 생성 위치
* Markdown : `tests/reports/data_quality_report.md`






