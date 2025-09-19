#!/usr/bin/env bash
newman run tests/postman/collections/novel-aggregator.postman_collection.json \
-e tests/postman/environments/local.postman_environment.json \
--reporters cli,junit \
--reporter-junit-export tests/postman/newman-results.xml