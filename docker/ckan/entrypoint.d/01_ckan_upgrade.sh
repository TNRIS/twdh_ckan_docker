#!/bin/sh
echo "@@@@@@ UPGRADE CKAN DB @@@@@@"
ckan -c /srv/app/production.ini db upgrade 
