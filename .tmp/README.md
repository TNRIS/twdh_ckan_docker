# This directory

Is a temporary fix to resolve template errors in ckanext-twdh_theme.
These changes fix the /dataset/, /, and add resource routes/endpoints.

Run `make patchPlugin` while running `docker compose up` from ../docker.
Then run `docker compose stop` then `docker compose up` to restart the docker server. 