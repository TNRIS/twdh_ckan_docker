.PHONY: ecrLogin

AWS_REGION := us-east-1
AWS_ACCOUNT_ID := 746466009731

ECR_URL := ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

ECR_PW := $(shell aws ecr get-login-password --region ${AWS_REGION})

GH_TOKEN := $(shell aws secretsmanager get-secret-value \
	--secret-id ci-cd \
	--query SecretString \
	--output text | \
	jq .CKAN_GH_CTREPKA_TOKEN | \
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


TAG := default

tagTest1:
	echo ${TAG} test1

tagTest2:
	echo ${TAG} test2
	
tagTest3: tagTest1 tagTest2
	echo ${TAG} test3
	