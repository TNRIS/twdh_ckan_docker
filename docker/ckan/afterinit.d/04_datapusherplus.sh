#!/bin/sh
echo "@@@@@@ INIT DATAPUSHER_PLUS @@@@@@"

UPGRADE=0

if [ "$UPGRADE" -ne 1 ]; then
    echo "Warning: CKAN DATAPUSHER_PLUS upgrade not enabled. If you want datapusher_plus upgrade to run, set UPGRADE=1 in twdh_ckan_docker/docker/ckan/entrypoint.d/01_datapusherplus.sh"
else 
  ckan -c /srv/app/production.ini db upgrade -p datapusher_plus
fi