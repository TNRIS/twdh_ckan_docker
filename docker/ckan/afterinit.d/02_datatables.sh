#!/bin/sh
echo "@@@@@@ INIT SECURITY @@@@@@"
ckan -c /srv/app/production.ini datatablesview-plus migrate
