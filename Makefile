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

build:
	@docker build ./docker/ckan -t 29_ckan:${TAG} --build-arg GH_TOKEN=${GH_TOKEN} --progress plain --no-cache 2>&1 | tee build.log

ecrLogin:
	@echo ${ECR_PW} | docker login -u AWS --password-stdin ${ECR_URL}

tag: ecrLogin
	docker tag 29_ckan:${TAG} ${ECR_URL}/29_ckan:${TAG}

ecrPush: tag
	docker push ${ECR_URL}/29_ckan:${TAG}

ecrBuildPush: build tag ecrPush