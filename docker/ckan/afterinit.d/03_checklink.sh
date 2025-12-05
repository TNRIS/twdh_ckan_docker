#!/bin/sh
echo "@@@@@@ INIT CKANEXT-CHECK_LINK @@@@@@"

UPGRADE=0

if [ "$UPGRADE" -ne 1 ]; then
    echo "Warning: CKAN INIT CKANEXT-CHECK_LINK not enabled. If you want ckanext-checklink upgrade to run, set UPGRADE=1 in twdh_ckan_docker/docker/ckan/entrypoint.d/01_checklink.sh"
else 
  ckan -c /srv/app/production.ini db upgrade -p check_link
fi