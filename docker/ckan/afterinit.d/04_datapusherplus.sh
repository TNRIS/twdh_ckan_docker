#!/bin/sh
echo "@@@@@@ INIT DATAPUSHER_PLUS @@@@@@"
ckan -c /srv/app/production.ini db upgrade -p datapusher_plus
