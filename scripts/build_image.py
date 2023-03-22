from lib.run import run
import json
import subprocess

GITHUB_SECRET_NAME = "ci-cd"

SECRETS = run(
"aws secretsmanager get-secret-value \
--secret-id {v} --query SecretString \
--output text".format(
    v=GITHUB_SECRET_NAME, 
))

TOKEN = json.loads(SECRETS)["CKAN_GH_CTREPKA_TOKEN"]

DOCKER_OUTPUT = subprocess.call(
    f"ls && cd ../ && ls",
    shell=True
)