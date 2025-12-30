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

### 2️⃣ DB Upsert / Idempotency 검증
- 동일 작품 반복 수집 시 중복 생성 방지
- 변경 필드만 갱신(MySQL novel + novel source)
- MongoDB 설명/키워드 Upsert 안정성 확인

### 3️⃣ KP Selenium 안정성 검증
- standalone-chrome 4개 환경에서 세션 재사용 + retry + timeout 상한 전략 검증
- 무한스크롤 및 상세 파싱 정상 동작 확인

---

## 📑 Table of Contents
- [Features](#features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project-Structure](#-project-structure)
- [Setup](#-setup)
- [API](#-api)
- [Jobs](#-jobs)
- [License](#-license)

---
<a id="features"></a>
## 🚀 Features

### 🔍 Scraping
- **KakaoPage:** 동적 페이지 / 무한스크롤
- **NaverSeries:** 정적 페이지 / 페이지네이션

### 🧩 Parsing & Normalization
- 플랫폼별 다른 메타를 **공통 스키마로 정규화**
- 지원/미지원 범위 명확화

### 🗄 Storage
- **MySQL:** 정형 메타 저장
- **MongoDB:** 유연 필드 저장(설명, 키워드 등)
- 안정적인 Upsert 정책 적용

### ⚙️ Orchestration
- 플랫폼별 병렬 처리 전략 적용

### 📈 Observability
- 로그 수집
- 실행 결과 리턴(`skip`, `fail`, `error_samples`)
- Job 실행 기록 저장

---

## 🏗 Architecture

