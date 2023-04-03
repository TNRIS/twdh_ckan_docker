#!/bin/sh
echo "@@@@@@ INIT CHECK_LINK @@@@@@"
ckan -c /srv/app/production.ini db upgrade -p check_link