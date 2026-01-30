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
# Set the common uwsgi options
UWSGI_OPTS="--socket /tmp/uwsgi.sock --pidfile=/tmp/uwsgi.pid --uid ckan --gid ckan --http :5000 --master --enable-threads --wsgi-file /srv/app/wsgi.py --module wsgi:application --lazy-apps "

if [[ -z "${UWSGI_WORKERS}" ]]; then
  #UWSGI_WORKERS not set
  UWSGI_OPTS+="--workers 2 "
else
  UWSGI_OPTS+="--workers ${UWSGI_WORKERS} "
fi

if [[ -z "${UWSGI_USE_CUSTOM_THREADS}" || "${UWSGI_USE_CUSTOM_THREADS}" != true ]]; then
  UWSGI_OPTS+="--enable-threads "
else
  UWSGI_OPTS+="--workers ${UWSGI_WORKERS} --threads ${UWSGI_THREADS} --thread-stacksize ${UWSGI_THREAD_STACKSIZE} "
fi

if [[ "${UWSGI_USE_GEVENT}" == "true" ]]; then
  UWSGI_OPTS+="--gevent 2000 --gevent-early-monkey-patch "
fi

UWSGI_OPTS+="--vacuum --harakiri 50 --callable application --single-interpreter --need-app --disable-logging --log-4xx --log-5xx --log-slow 5000 "

if [[ "$UWSGI_STATS" == "true" ]]; then
  UWSGI_OPTS+="--stats 127.0.0.1:${UWSGI_STATS_PORT} --stats-http"
fi

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

echo "Prerun complete"

# Check whether http basic auth password protection is enabled and enable basicauth routing on uwsgi respecfully
if [ $? -eq 0 ]
then
  if [ "$PASSWORD_PROTECT" = true ]
  then
    if [ "$HTPASSWD_USER" ] || [ "$HTPASSWD_PASSWORD" ]
    then
      echo "Starting with basicauth ..."
      # Generate htpasswd file for basicauth
      htpasswd -d -b -c /srv/app/.htpasswd $HTPASSWD_USER $HTPASSWD_PASSWORD
      # Start uwsgi with basicauth
      uwsgi --ini /srv/app/uwsgi.conf --pcre-jit $UWSGI_OPTS
    else
      echo "Missing HTPASSWD_USER or HTPASSWD_PASSWORD environment variables. Exiting..."
      exit 1
    fi
  else
    echo "Starting without basicauth ..."
    # Start supervisord
    echo "Starting supervisord"
    supervisord --configuration /etc/supervisor/supervisord.conf &
    # Start uwsgi
    echo "Starting uwsgi"
    uwsgi $UWSGI_OPTS

    # FOR DEBUG ONLY!
    #echo "Entering infinite loop ... "
    #/srv/app/infinite_loop.sh

  fi
else
  echo "[prerun] failed...not starting CKAN."
fi
