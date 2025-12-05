#!/bin/sh
echo "@@@@@@ INIT SECURITY @@@@@@"

UPGRADE=0

if [ "$UPGRADE" -ne 1 ]; then
    echo "Warning: CKAN INIT SECURITY not enabled. If you want ckanext-security upgrade to run, set UPGRADE=1 in twdh_ckan_docker/docker/ckan/entrypoint.d/01_security.sh"
else 
  ckan -c /srv/app/production.ini security migrate
fi