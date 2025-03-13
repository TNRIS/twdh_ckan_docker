#!/bin/sh
echo "@@@@@@ INIT CKANEXT-PAGES @@@@@@"
ckan -c /srv/app/production.ini db upgrade -p pages
