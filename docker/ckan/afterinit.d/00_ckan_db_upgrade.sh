#!/bin/sh
echo "@@@@@@ UPGRADE CKAN DB @@@@@@"

UPGRADE=0

if [ "$UPGRADE" -ne 1 ]; then
    echo "Warning: CKAN DB UPGRADE not enabled. If you want db upgrade to run, set UPGRADE=1 in twdh_ckan_docker/docker/ckan/entrypoint.d/01_ckan_db_upgrade.sh"
else 
  ckan -c /srv/app/production.ini db upgrade 
  ckan -c /srv/app/production.ini db pending-migrations --apply 
fi

