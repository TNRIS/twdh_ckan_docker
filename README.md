# A Docker image build repository for Texas Water Data Hub CKAN

## CI/CD

1. git tag v*.*.*-*-*
2. git push origin v*.*.*-*-*

## DEVOPS PIPELINE DIAGRAM
```mermaid
flowchart TD
    A[This repo] -->| commit locally | B(Local Repo Code)
    B --> | run `make build` | C(Local Image)
    C --> | run `docker compose --file docker-compose_local.yml up` | D(Local Image Running)
    D --> | run tests | E{"Tests Pass"}
    E --> PASS_L[true]
    E --> FAIL_L[false]
    FAIL_L --> | return to local dev test | B
    PASS_L --> | `git tag $TAGNAME && git push $TAGNAME` | F( GitHub Action )
    F --> | check gh action logs | G{Build Succeeded}
    G --> PASS_R[true]
    G --> FAIL_R[false]
    FAIL_R --> | return to local dev test | B
    PASS_R --> | change helmchart image tag when ready | H(Make New Helm Release)
```
