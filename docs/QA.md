## QA & Test Portfolio — Novel Aggregator

이 문서는 Novel Aggregator 프로젝트의 **테스트 전략 / 자동화 구성 / 안정화 경험 / CI 운영**을 정리한 QA 포트폴리오입니다.  
**어떤 리스크를 어떤 방식으로 줄였는지**를 증거 중심으로 보여주는 것입니다.

---
## 1) Quality Goals & Risks

### 품질 목표
* 플랫폼별 동적/정적, HTML 차이를 흡수해 **파서가 안정적으로 동작**할 것
* Job 실행이 반복되어도(upsert) **데이터가 중복/손상되지 않을 것**
* KP(Selenium)가 장시간 실행 중에도 **세션 폭탄/렌더러 타임아웃을 최소화**할 것
* KP,NS 전체 처리 과정에서 **안전성/속도를 가능한 확보**할 것
* 실패가 발생해도 **원인 추적 가능**(지표/샘플 URL/에러 메시지)할 것

### 주요 리스크
* KP 무한스크롤/동적 렌더링 → renderer timeout / execute_script 실패
* Selenium Remote 세션 생성 폭주 → SessionNotCreated / No nodes support capabilities
* 플랫폼 구조 변경 → selector 실패 / 필수 필드 누락
* 대량 처리시 안전성/처리속도 고려 -> docker 용량 / thread 동시 가능 수 

---
## 2) Test Pyramid (Unit / Integration / E2E)

### 2.1 Unit Tests
**대상**
* `normalize.py`: 플랫폼별 다른 표현의 연령,연재상태,숫자
* 각 플랫폼 `parser.py`: HTML → dict 변환 로직, 필드/타입 (단, 실제 HTML 사용)
* (NS) `scraper.py`: 각 페이지의 스레드 결과 소설ID를 합치는 로직 

**검증 포인트**
* 다양한 입력(빈 값/None/문자열 숫자/콤마 포함) 처리되는지 
* 누락 필드가 있어도 크래시 없이 “skipped” 처리되는지 
* 변환 결과가 저장 스키마와 필드/타입 일치하는지

### 2.2 Integration Tests
**대상**
* DB upsert :  novels / novel_sources
* 'orchestrator.py' : parser/scraper 모듈과 DB 연결 처리 로직
* '/scheduler/main.py' : APScheduler 작동

**검증 포인트**
* **Idempotency** : 같은 입력을 여러 번 넣어도 중복 row가 생기지 않는지
* Update 정책 : episode\view_count\completion_status 등 변경 필드가 갱신되는지
* scheduler option : 동시 실행, 중복 실행 등 제대로 실행되는지

### 2.3 E2E Tests
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

## 3) Postman/Newman E2E

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
1. 'uvicorn src.apps.api.main:app --reload --host 0.0.0.0 --port 8000 --log-level info' 로컬 서버 실행
2. (Window) `tests/scripts/run_all.ps1` 파일 실행
- run_all.ps1 : 파이썬 테스트(단위+통합+E2E)와 postman 실행 명령어 모음

---

## 4) Selenium 안정화 전략
### 4.1 docker container 4개
Selenium Webdriver 병렬 실행용 컨테이너 <br>
4개만 쓰는 이유 : docker cpu/memory 용량 한계
- 'shm_size:"2g"' (render timeout 완화)
- 'SE_NODE_MAX_SESSION=1' (컨테이너 당 Webdriver 세션 1개)
- 'SE_NODE_OVERRIDE_MAX_SESSIONS=true' (자동 병렬 실행 방지 및 안정성)

### 4.2 selenium grid 전략
문제 
- 작품당 Webdriver 생성으로 병렬 실행
- SessionNotCreatedException 및 세션 폭탄 발생
전략 
- 전체 작업을 청크 단위 4개로 분리 
- 4개의 webdriver(=docker container)에서 동시실행으로 순차 처리

### 4.3 Retry & timeout
- `execute_script`에 retry wrapper 적용
- 무한스크롤은 최대 수행 시간을 두어 무한 대기를 방지 
- 실패는 errors_sample로 샘플을 남겨 재현 가능하게 유지

---

## 5) Data Quality Tests (중복/정규화/인코딩)
### 5.1 중복/정규화
mysql
novels : 100483
novel_sources : 129294
mongo
novel_meta : 100601
이거 문제 해결


---

## 6) Test Evidence
실패 -> 개선 사례 
1. unit / integration 테스트 결과
2. newman 을 통해 환경변수, 전략, 변경 과정 
3. 첫번쨰 개선 : NS 개선
4. 두번째 개선 : KP 무한스크롤 selenium 안정화
5. 세번째 개선 : NS KP 병렬 파싱 처리 분리 방법
6. 네번쟤 개선 : 데이터





