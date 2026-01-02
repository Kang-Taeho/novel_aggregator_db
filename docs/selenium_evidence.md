# Selenium Evidence 
이 문서는 KP(Selenium) 구간에서 발생한 안정성 이슈를 **관측 → 원인 가설 → 개선 → 재검증(전/후)** 흐름으로 기록한 Evidence입니다.

## 측정 계획
- timeout rate = timeout 발생 건수 / 전체 처리 건수
- session creation failure = SessionNotCreatedException 발생 건수
- avg job duration = 전체 실행 시간 / job 수
- errors_sample = 상위 N개 실패 URL + 에러 메시지 요약

---

# 1차 검사 (실 서비스 기준 scraper 테스트)

## 검사 결과 (Screenshot / Text)
### 증거
- 📎 Screenshot 1차 : [1차 KP_scraper 테스트](./evidence_docs/u01_test_KP_scraper.png)
- 📎 Screenshot 2차 : [2차 KP_scraper 테스트](./evidence_docs/u02_test_KP_scraper.png)
- 📎 Screenshot 3차 : [3차 KP_scraper 테스트](./evidence_docs/u03_test_KP_scraper.png)

### 관측 요약
- (KP) scraper 무한 스크롤 장르별 실행 시간
  - 1차 | 1269.4s | 714.3s | Timeout (1800s) |
  - 2차 | 1770.7s | 973.1s | Timeout (3600s) |
  - 3차 | 1704.7s | 878s | WebDriverException |

## 1) 문제
KP 플랫폼은 **무한 스크롤 기반 동적 렌더링** 구조로, <br>
스크롤 종료 시점이 명확하지 않고 페이지 로딩 상태에 따라 <br>
실행 시간 및 안정성이 크게 흔들리는 특성이 있음. 

## 2) 조치
### 1차 조치
- **안정성 강화**
  - Selenium WebDriver의 **대기(timeout) 전략** 설정
  ```
    drv.set_page_load_timeout(60)
    drv.implicitly_wait(0)
  ```
- **timeout 상한 조정**
  - 최대 수행 시간: **30분 → 60분**으로 증가

### 2차 조치
- **스크롤 전략 변경 (안정성 증가)**
  - 일정 시간 동안 `scrollTo` 방식 사용 후
  - 이후 `PageDown` 키 기반 스크롤로 전환
- **브라우저 세션 관리 개선**
  - 장르별로 **새로운 WebDriver 세션 생성**
  - 장시간 누적 실행으로 인한 **메모리 누수/누적 상태 초기화**

### 3차 조치
- **스크롤 로직 단순화**
  - 하이브리드 방식(scrollTo + PageDown) 제거
  - `scrollTo` 기반 스크롤로 **공격적으로 변경**
  - 빠른 실패를 허용하는 방향으로 전략 전환

## 3) 결론
- 하이브리드 방식 스크롤은 안정성을 유지하려다 보면
  - 브라우저 리소스 누적
  - WebDriverException 위험 증가
- scrollTo 방식으로 **공격적으로 실패 가능성을 열어두고**
  - 빠르게 에러를 감지
  - 재시도/분할 실행으로 처리하는 방식이 더 현실적

---
# 2차 검사 (Newman)

## 1) 검사 결과 (Screenshot / Text)
### 증거
- 📄 Log: [newman 1차 테스트 결과](./evidence_docs/01_newman.txt)

### 관측 요약
- POST jobs/scrape (KP)
  - "total":57372,"success":167,"failed":57203,"skipped":2
- POST jobs/scrape (NS)
  - 실행 시간: 10701573ms (2h 58m 21.5s)
  - "total":100386,"success":73176,"failed":2, "skipped":27208
- 주요 에러 :
  - (KP)`No nodes support the capabilities ...`
  - (NS)`argument of type 'NoneType' ...`

## 2) 문제
### 2.1 (KP) Selenium 세션 생성 대량 실행 실패
- Selenium 노드는 **1개의 세션만 수용 가능**한데,  
    -**수만 건의 작업을 다중 스레드로 동시에 실행**하면서  
    -각 작업마다 **새 WebDriver 세션을 생성하려고 시도** 

## 3) 조치
### 3.1 (KP) Selenium Docker Container 4개 구성
- Selenium WebDriver용 Docker 컨테이너를 **4개로 고정**
- 각 컨테이너는 **동시에 1개의 세션만 허용**

**활용 1. 스크롤 세션 재생성 대신 컨테이너 다중 사용**
- 기존 방식
  - 장르별 스크롤 시 **매번 새로운 WebDriver 세션 생성**
  - 장시간 실행 시 메모리 누적 및 세션 폭탄 발생
- 개선 방식
  - 장르별로 새 세션을 만들지 않음
  - **4개의 Selenium Docker 컨테이너를 재사용**
  - 컨테이너 단위로 격리되어 **메모리 누적 방지**
  - 세션 생성 오버헤드 감소 → 처리 속도 및 안정성 향상

**활용 2. Selenium Grid 실행 전략**
- 전체 작업을 **청크 단위로 4개로 분리**
- 실행 방식
  - **4개의 WebDriver(= Docker container)** 에서 동시 실행
  - 각 컨테이너 내부에서는 **순차 처리**
- 효과
  - 수만 건의 다중 스레드 대신 병렬 실행 가능
  - “No nodes support the capabilities” 재발 방지

---
# 3차 검사 - 최종 테스트 (Newman)

## 1) 검사 결과 (Screenshot / JUnit)
### 증거
- 📎 Screenshot 
  - [newman_2차_1 테스트 결과](./evidence_docs/02_1_run_all.png)
  - [newman_2차_2 테스트 결과](./evidence_docs/02_2_run_all.png)
  - [newman_2차_3 테스트 결과](./evidence_docs/02_3_run_all.png)
  - [docker 최대 사용량 스크린샷](evidence_docs/docker_최대사용량.png)
- 📄 Log: [newman 2차 결과 리포트](../tests/reports/pytest-junit.xml)


### 관측 요약
- POST jobs/scrape (KP)
  - 실행 시간: 99683055ms (1d 5h 45m 16.5s)
  - "total":57042,"success":55834,"failed":0, "skipped":1208
- POST jobs/scrape (NS)
  - **2차 검사에서 완료**

## 2) 최종 분석
### 2.1 Selenium 컨테이너 4개 적용에 따른 scroll_bottom 시간 비교

#### 테스트 조건
- 대상: KP 플랫폼 (무한 스크롤 기반 페이지)
- 작업 단위: 장르별 전체 페이지 스크롤
- 스크롤 방식: `scrollTo` 기반
- 비교 기준:
  - 단일/과도한 세션 생성 방식 vs
  - **Selenium Docker container 4개 + Grid chunking 전략**

#### 결과 요약
| 항목  | 기존 방식 | 개선 방식 (컨테이너 4개) |
|-----|---:|----------------:|
| 장르1 | 1704.7s |         1268.3s |
| 장르2 | 878s |          660.8s |
| 장르3 | WebDriverException |         4317.0s |
| 장르4 |  |          919.4s |
| 장르5 |  |           186.8 |

### 2.2 Selenium 컨테이너를 4개만 사용하는 이유
- Docker Desktop 기준으로 확인 결과:
  - Selenium Chrome 컨테이너 1개당
    - 메모리 사용량: 매우 큼
    - CPU 사용량: 스크롤 구간에서 급격히 상승
- 컨테이너 수 증가 시
  - 호스트 메모리/CPU 사용량이 선형 이상으로 증가
  - 다른 컨테이너(MySQL, API, Scheduler 등)에 영향을 주기 시작

📎 **Evidence**  
 - Docker 사용량 스크린샷: `./evidence_docs/docker_최대사용량.png`