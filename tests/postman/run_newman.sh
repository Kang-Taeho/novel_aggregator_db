#!/usr/bin/env bash
set -e

npx newman run "tests/postman//novel-aggregator.postman_collection.json" \
  -e "tests/postman//local.postman_environment.json" \
  --reporters cli,junit \
  --reporter-junit-export "tests/postman/reports/newman-results.xml";
