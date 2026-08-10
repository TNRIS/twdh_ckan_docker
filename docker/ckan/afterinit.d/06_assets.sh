#!/bin/sh
echo "@@@@@@ BUILT ASSETS @@@@@@"

ckan -c /srv/app/production.ini asset build && chown -R ckan.ckan /srv/app/data/webassets
