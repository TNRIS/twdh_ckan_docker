#!/bin/sh
echo "@@@@@@ INIT CKANEXT-DATATABLESVIEW-PLUS @@@@@@"

UPGRADE=1

if [ "$UPGRADE" -ne 1 ]; then
    echo "Warning: CKAN CKANEXT-DATATABLESVIEW-PLUS not enabled. If you want ckanext-datatablesview-plus upgrade to run, set UPGRADE=1 in twdh_ckan_docker/docker/ckan/entrypoint.d/01_datatables.sh"
else 
  ckan -c /srv/app/production.ini datatablesview-plus migrate
fi
