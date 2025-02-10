#!/bin/sh
echo "@@@@@@ INIT CKANEXT-DATATABLESVIEW-PLUS @@@@@@"
ckan -c /srv/app/production.ini datatablesview-plus migrate
