#!/bin/sh

cd docker && \
docker compose build --build-arg GH_TOKEN=$(aws secretsmanager get-secret-value \
--secret-id ci-cd \
--query SecretString \
--output text | \
jq .CKAN_GH_CTREPKA_TOKEN | \
tr -d '"') --progress plain --no-cache 2>&1 | \
tee build.log