#!/bin/sh
echo "@@@@@@ INIT CHECK_LINK @@@@@@"
ckan -c /srv/app/production.ini upgrade db -p check_link