#!/bin/bash
# Run any startup scripts provided by images extending this one

if [[ -d "${APP_DIR}/docker-entrypoint.d" ]]
then
    for f in ${APP_DIR}/docker-entrypoint.d/*; do
        case "$f" in
            *.sh)     echo "$0: Running init file $f"; . "$f" ;;
            *.py)     echo "$0: Running init file $f"; python "$f"; echo ;;
            *)        echo "$0: Ignoring $f (not an sh or py file)" ;;
        esac
        echo
    done
fi

# Set the common uwsgi options
UWSGI_OPTS="--socket /tmp/uwsgi.sock --pidfile=/tmp/uwsgi.pid --uid ckan --gid ckan --http :5000 --master --enable-threads --wsgi-file /srv/app/wsgi.py --module wsgi:application --lazy-apps --gevent 2000 -p 2 -L --gevent-early-monkey-patch --vacuum --harakiri 50 --callable application --single-interpreter --need-app --disable-logging --log-4xx --log-5xx --log-slow 5000"

# Run the prerun script to init CKAN and create the default admin user
python prerun.py || { echo '[CKAN prerun] FAILED. Exiting...' ; exit 1; }

# Check if we are in maintenance mode and if yes serve the maintenance pages
if [ "$MAINTENANCE_MODE" = true ]; then PYTHONUNBUFFERED=1 python maintenance/serve.py; fi

# Run any after prerun/init scripts provided by images extending this one
if [[ -d "${APP_DIR}/docker-afterinit.d" ]]
then
    for f in ${APP_DIR}/docker-afterinit.d/*; do
        case "$f" in
            *.sh)     echo "$0: Running after prerun init file $f"; . "$f" ;;
            *.py)     echo "$0: Running after prerun init file $f"; python "$f"; echo ;;
            *)        echo "$0: Ignoring $f (not an sh or py file)" ;;
        esac
        echo
    done
fi

# Check whether http basic auth password protection is enabled and enable basicauth routing on uwsgi respecfully
if [ $? -eq 0 ]
then
  # Start supervisord
  supervisord --configuration /etc/supervisor/supervisord.conf &

  if [ "$TWDH_MODE" = debug ]; 
  then 
    # Start ckan with debugpy so that VSCode debugger will work.
    # Note that in this mode file syncing will not happen automaticlly
    while true; do
      python -m debugpy --listen 0.0.0.0:5678 /srv/app/virtualenv/bin/ckan -c /srv/app/production.ini run -H 0.0.0.0 --disable-reloader
      echo Exit with status $?. Restarting.
      sleep 2
    done
  else
    # Start ckan without debugpy. DEV mode will still be on, but the VSCode debugger will not be able to attach.
    uwsgi $UWSGI_OPTS
  fi
  

else
  echo "[prerun] failed...not starting CKAN."
fi
