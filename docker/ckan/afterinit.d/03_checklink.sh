#!/bin/sh
echo "@@@@@@ INIT CKANEXT-CHECK_LINK @@@@@@"
ckan -c /srv/app/production.ini db upgrade -p check_link
