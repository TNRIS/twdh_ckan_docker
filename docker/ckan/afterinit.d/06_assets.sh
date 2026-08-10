#!/bin/sh
echo "@@@@@@ BUILT ASSETS @@@@@@"

ckan -c /srv/app/production.ini asset build
