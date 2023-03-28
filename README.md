# A Docker image build repository for Texas Water Data Hub CKAN

## Building
run `make build TAG=<your_tag_name></your_tag_name>`
## Pushing to ECR
run `make ecrPush TAG=<your_tag_name></your_tag_name>`
## Build and Push to ECR (one command)
run `make ecrBuildPush TAG=<your_tag_name></your_tag_name>`
## Managing CKAN Extensions
check ./docker/ckan/plugins/README.md
## Managing CKAN Patches
check ./docker/ckan/patches/README.md
## CI/CD
managed by Github Actions in ./github