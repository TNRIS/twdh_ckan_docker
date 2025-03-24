#!/bin/bash
# Run any startup scripts provided by images extending this one

echo "TWDH_DEV_MODE=${TWDH_DEV_MODE}"

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

if [ "$TWDH_DEV_MODE" != nockan ];
then 
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
fi

# Start supervisord
supervisord --configuration /etc/supervisor/supervisord.conf &

if [ "$TWDH_DEV_MODE" = debug ];
then 
  # Start ckan with debugpy so that VSCode debugger will work.
  # Note that in this mode file syncing will happen more slowly than normal
  ${APP_DIR}/watch_ckan.sh ${CKAN_DIR} &
  ${APP_DIR}/watch_ckan.sh ${APP_DIR}/production.ini &

  while true; do
    echo "TWDH_DEV_MODE=debug !! VSCode debugging enabled BUT CKAN will be slow to update on code changes, so watch the logs"
    python -m debugpy --listen 0.0.0.0:5678 /srv/app/virtualenv/bin/ckan -c /srv/app/production.ini run -H 0.0.0.0 --disable-reloader
    echo Exit with status $?. Restarting.
    sleep 2
  done

elif [ "$TWDH_DEV_MODE" = nockan ];
then 
  # This mode is for debugging when CKAN is crashing inside the 
  # Docker image. You will need to `docker exec` into the image 
  # and start CKAN manually as is appropriate to your debugging 
  # scenario.
  # This mode is also useful for using Pdb to debug
  while true; do
    echo "TWDH_DEV_MODE=nockan !! RUNNING AN EMPTY LOOP FOR DEBUG; START uWSGI or CKAN MANUALLY!"
    sleep 600;
  done

elif [ "$TWDH_DEV_MODE" = dev ];
then 
  echo "TWDH_DEV_MODE=dev ## Local file sync enabled, but VSCode debugger not available"
  # Start ckan without debugpy. DEV mode will still be on, but the VSCode debugger will not be able to attach.
  uwsgi $UWSGI_OPTS

else
  echo "TWDH_DEV_MODE not valid! Set TWDH_DEV_MODE to dev, debug or nockan"
  echo "TWDH_DEV_MODE currently set to ${TWDH_DEV_MODE}"
fi
  
