#!/bin/sh
echo "@@@@@@ INIT HARVESTER @@@@@@"
ckan -c /srv/app/production.ini harvester initdb
