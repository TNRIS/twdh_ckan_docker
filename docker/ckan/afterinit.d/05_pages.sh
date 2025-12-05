#!/bin/sh
echo "@@@@@@ INIT CKANEXT-PAGES @@@@@@"

UPGRADE=0

if [ "$UPGRADE" -ne 1 ]; then
    echo "Warning: CKAN INIT CKANEXT-PAGES not enabled. If you want ckanext-pages upgrade to run, set UPGRADE=1 in twdh_ckan_docker/docker/ckan/entrypoint.d/01_pages.sh"
else 
  ckan -c /srv/app/production.ini db upgrade -p pages
fi