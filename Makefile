.PHONY: ecrLogin

## AWS ACCOUNT VARS
AWS_REGION := us-east-1
AWS_ACCOUNT_ID := 746466009731

## ECR VARS
ECR_URL := ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
ECR_PW := $(shell aws ecr get-login-password --region ${AWS_REGION})

## GH TOKEN VARS
SECRET_ID := ci-cd
SECRET_PATH := .CKAN_GH_CTREPKA_TOKEN
GH_TOKEN := $(shell aws secretsmanager get-secret-value \
	--secret-id ${SECRET_ID} \
	--query SecretString \
	--output text | \
	jq ${SECRET_PATH} | \
	tr -d '"')

TAG := default

ecrLogin:
	@echo ${ECR_PW} | docker login -u AWS --password-stdin ${ECR_URL}

build: ecrLogin
	@/usr/bin/time --format="Build time: %E" docker build ./docker/ckan -t 29_ckan:default --build-arg GH_TOKEN=${GH_TOKEN} --progress plain --no-cache 2>&1 | tee build.log

build-dev: ecrLogin
	@/usr/bin/time --format="Build time: %E" docker build ./docker/ckan -t 29_ckan:default --build-arg GH_TOKEN=${GH_TOKEN} --build-arg ENV=dev --progress plain 2>&1 | tee build.log

build-dev-no-cache: ecrLogin
	@/usr/bin/time --format="Build time: %E" docker build ./docker/ckan -t 29_ckan:default --build-arg GH_TOKEN=${GH_TOKEN} --build-arg ENV=dev --progress plain --no-cache 2>&1 | tee build.log

tag: build
	/usr/bin/time --format="Build time: %E" docker tag 29_ckan:default ${ECR_URL}/29_ckan:${TAG}

ecrBuild: tag

ecrPush:
	docker push ${ECR_URL}/29_ckan:${TAG}

ecrBuildPush: ecrBuild ecrPush

