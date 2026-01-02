# 가상환경/의존성 준비는 생략(포트폴리오 Readme에 안내)

# 파이썬 테스트(단위+통합+E2E)
pytest -q --maxfail=1 --disable-warnings --junitxml=tests\reports\pytest-junit.xml tests/

# 서버 올려둔 상태에서 Postman
npx newman run tests\postman\novel-aggregator.postman_collection.json `
  -e tests\postman\local.postman_environment.json `
  --reporters cli,junit,htmlextra  `
  --reporter-junit-export tests\reports\newman-results.xml `
  --reporter-htmlextra-export tests/reports/newman-report.html;

