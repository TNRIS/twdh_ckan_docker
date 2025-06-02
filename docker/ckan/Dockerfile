##################
### Build CKAN ###
##################

ARG ENV=base

FROM ubuntu:jammy-20250126 AS ckanbuild

# Set CKAN version to build

ENV GIT_URL=https://github.com/TNRIS/ckan.git
#ENV GIT_BRANCH=twdh-patches-2.10.5
ENV GIT_BRANCH=twdh-patches-2.10.5-iformredirect

# Set timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set Locale
ENV LC_ALL=en_US.UTF-8

# Set src dirs
ENV SRC_DIR=/srv/app/src
ENV PIP_SRC=${SRC_DIR}

WORKDIR ${SRC_DIR}

# Set the locale          
RUN apt-get update
RUN apt-get install --no-install-recommends -y locales
RUN sed -i "/$LC_ALL/s/^# //g" /etc/locale.gen
RUN dpkg-reconfigure --frontend=noninteractive locales 
RUN update-locale LANG=${LC_ALL}

# Instal apt-utils
RUN apt-get install --no-install-recommends -y \
        apt-utils

# Packages to build CKAN requirements and plugins
RUN apt-get install --no-install-recommends -y \
        git \
        curl \
        ca-certificates \
        python3 \
        python3.10-venv \
        libpq-dev \
        linux-headers-generic \
        wget \
        make \
        autoconf \
        automake \
        libtool \
        patch \
        libpcre3-dev \
        libpcre3 \
        python3-dev \
        libffi-dev \
        libxml2-dev \
        libxslt-dev \
        build-essential

# Create the src directory
RUN mkdir -p ${SRC_DIR}

# SETUP VIRTUAL ENVIRONMENT
# NOTE: needs to be initialized in each build phase
ENV VIRTUAL_ENV=/srv/app/virtualenv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="$PATH:$VIRTUAL_ENV/bin:PATH"
ENV WHEEL_DIR=${VIRTUAL_ENV}/src 

RUN pip install "setuptools-scm<8" "setuptools>=44.1.0" wheel
#RUN pip install --upgrade pip "setuptools-scm<8" "setuptools>=44.1.0" wheel

# Fetch and build CKAN and requirements
RUN pip install -e git+${GIT_URL}@${GIT_BRANCH}#egg=ckan


RUN python -V
RUN pip -V
RUN pip list

RUN pip wheel --wheel-dir=${VIRTUAL_ENV}/src -r ckan/requirements.txt

# ┌─────────────────────────────────────────────────────────────┐
# │                                                             │
# │ Base image (Production env)                                 │
# │ ---------------------------                                 │
# │ This is always built                                        │
# │                                                             │
# └─────────────────────────────────────────────────────────────┘


FROM ubuntu:jammy-20250126 AS base

ARG GH_TOKEN=default

LABEL maintainer="Texas Geographic Information Office"
LABEL org.opencontainers.image.source https://github.com/tnris/twdh_ckan_docker

# Set timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set Locale
ENV LC_ALL=en_US.UTF-8

# Set the locale          
RUN apt-get update && \
    apt-get install --no-install-recommends -y locales && \
    sed -i "/$LC_ALL/s/^# //g" /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=${LC_ALL} && \
    rm -rf /var/lib/apt/lists/*

ENV APP_DIR=/srv/app
ENV SRC_DIR=/srv/app/src
ENV CKAN_DIR=${SRC_DIR}/ckan
ENV DATA_DIR=/srv/app/data
ENV PIP_SRC=${SRC_DIR}
ENV CKAN_SITE_URL=http://0.0.0.0:5000
ENV CKAN__MAX_RESOURCE_SIZE 512

ENV CKAN__DEFAULT_VIEWS image_view \
    openapi_viewer \
    text_view \
    geo_view \
    geojson_view \
    datatablesview_plus \ 
    ags_fs_view 

ENV CKAN__PLUGINS \
    stats \
    twdh_reports \
    twdh_theme \
    collection \
    activity \
    security \
    report \
    check_link \
    text_view \
    webpage_view \
    image_view \
    video_view \
    datastore \
    spatial_metadata \
    spatial_query \
    twdh_schema \
    scheming_datasets \
    scheming_organizations \
    contact \
    pages \
    resource_proxy \
    geo_view \
    geojson_view \
    wmts_view \
    shp_view \
    datatablesview_plus \
    datapusher_plus \
    openapi_viewer \
    s3filestore \
    googleanalytics \
    ags_fs_view \ 
    envvars 
    # ^ envvars always needs to be last in the CKAN__PLUGINS list
    # s3filestore MUST PRECEDE googlealanalytics in the CKAN_PLUGINS list

# s3filestore env variables
ENV CKANEXT__S3FILESTORE__AWS_BUCKET_NAME twdh-s3filestore
ENV CKANEXT__S3FILESTORE__SIGNATURE_VERSION s3v4
ENV CKANEXT__S3FILESTORE__REGION_NAME us-east-1
ENV CKANEXT__S3FILESTORE__AWS_STORAGE_PATH docker-twdh-local
ENV CKANEXT__S3FILESTORE__FILESYSTEM_DOWNLOAD_FALLBACK true

# Install necessary packages to run CKAN
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    gettext \
    build-essential \
	curl \
    patch \
    ca-certificates \
    libpq5 \
    git \
    g++-10 \
	postgresql-client \
    python3 \
    python3.10-venv \
	python3-distutils \
	libpython3.10 \
    libmagic1 \
    libpcre3 \
    libxslt1.1 \
    libxml2 \
    tzdata \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libgeos-c1v5 \
    postgis \
    libjpeg8 \
    libjpeg-dev \
    libfreetype6 \
    libfreetype6-dev \
    zlib1g-dev \
    supervisor \
    file \
    # Is proj-bin necessary here, in build phase, or both?
    proj-bin \
    uchardet \
    vim \
    apache2-utils && \
    rm -rf /var/lib/apt/lists/* && \
    # Create SRC_DIR
    mkdir -p ${SRC_DIR}

# SETUP VIRTUAL ENVIRONMENT
# NOTE: needs to be initialized in each build phase
ENV VIRTUAL_ENV=/srv/app/virtualenv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="$PATH:$VIRTUAL_ENV/bin:PATH"
ENV WHEEL_DIR=${VIRTUAL_ENV}/src 
RUN pip install "setuptools-scm<8" "setuptools>=44.1.0" wheel
#RUN pip install --upgrade pip "setuptools-scm<8" "setuptools>=44.1.0" wheel

# Get artifacts from build stages
COPY --from=ckanbuild ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=ckanbuild ${WHEEL_DIR} /srv/app/wheels
COPY --from=ckanbuild ${CKAN_DIR} ${CKAN_DIR}
COPY ./plugins ${SRC_DIR}/plugins

# Copy pre-built binaries into place
COPY bin/qsvdp /usr/local/bin/qsvdp

# Build PROJ generic coordinate transformation software required by ckanext-spatial

# RUN apt-get update && \
#    apt-get install --no-install-recommends -y \
#    cmake \
#    sqlite3 \
#    libsqlite3-dev \
#    libtiff5-dev \
#    libcurl4-openssl-dev && \
#    curl https://download.osgeo.org/proj/proj-9.5.1.tar.gz --output proj-9.5.1.tar.gz && \
#    tar xzvf proj-9.5.1.tar.gz && \
#    cd proj-9.5.1 && \
#    mkdir build && \
#    cd build && \
#    cmake .. && \
#    cmake --build . && \
#    cmake --build . --target install &&  \
#    projsync --system-directory --all

RUN ls ${SRC_DIR}/plugins

# Fix ckanext-spatial dependency issue
# RUN pip install geojson shapely

# Fix ckanext-googleanalytics dependency issue
RUN pip install google-api-python-client==1.6.7

# Additional install steps for build stages artifacts
RUN pip install uWSGI gevent==22.10.2

# Create a local user and group to run the app
RUN groupadd -g 92 ckan && \
    useradd -rm -d /srv/app -s /bin/bash -g ckan -u 92 ckan

WORKDIR ${CKAN_DIR}

# Install CKAN
RUN pip install -e /srv/app/src/ckan

# comment out below if using ckanext-security and use own who.ini
# COPY overwrite.who.ini into app dir for ckanext-security required configurations
COPY ./overwrite.who.ini ${APP_DIR}/who.ini
COPY ./overwrite.who.dev.ini ${APP_DIR}/devwho.ini

RUN pip install --no-index --find-links=/srv/app/wheels -r requirements.txt
RUN pip install future

# Generate CKAN config
RUN ckan generate config ${APP_DIR}/production.ini

RUN python -V
RUN pip -V
RUN pip list

# Install plugins
RUN python ${SRC_DIR}/plugins/plugins.py


# Configure plugins
RUN ckan config-tool ${APP_DIR}/production.ini "ckan.plugins = ${CKAN__PLUGINS}" && \
    # Create the data directory
    mkdir ${DATA_DIR} && \
    # Webassets can't be loaded from env variables at runtime, it needs to be in the config so that it is created
    ckan config-tool ${APP_DIR}/production.ini "ckan.webassets.path = ${DATA_DIR}/webassets" && \
    # Set the default level for extensions to INFO
    ckan config-tool ${APP_DIR}/production.ini -s logger_ckanext -e level=INFO && \
    # Set the default views
    ckan config-tool ${APP_DIR}/production.ini "ckan.views.default_views = ${CKAN__DEFAULT_VIEWS}" && \
    # upgrade ckan_max_resource_size
    ckan config-tool ${APP_DIR}/production.ini "ckan.max_resource_size = ${CKAN__MAX_RESOURCE_SIZE}" && \
    # add scheming config
    ckan config-tool ${APP_DIR}/production.ini "scheming.dataset_schemas = ckanext.twdh_schema:schemas/dataset-druf.yaml ckanext.twdh_schema:schemas/application.yaml" && \
    ckan config-tool ${APP_DIR}/production.ini "scheming.organization_schemas = ckanext.twdh_schema:schemas/organization.yaml" && \
    ckan config-tool ${APP_DIR}/production.ini "scheming.presets = ckanext.scheming:presets.json ckanext.twdh_schema:schemas/presets.yaml" && \
    # add ckan.spatial.search_backend to enable solr spatial search
    ckan config-tool ${APP_DIR}/production.ini "ckanext.spatial.search_backend = solr-spatial-field" && \
    # change default logo to tx water logo from cdn.tnris.org
    ckan config-tool ${APP_DIR}/production.ini "ckan.site_logo = https://cdn.tnris.org/images/Hub_NavIcon_dark.png" && \
    # add config option for google analytics download view
    ckan config-tool ${APP_DIR}/production.ini "googleanalytics.id = G-SJK5R9G5F5" && \
    ckan config-tool ${APP_DIR}/production.ini "googleanalytics.download_handler = ckanext.s3filestore.views:resource_download" && \
    # DP+ settings
    # These settings should be configured in .env-ckan.env but DP+ is not picking them up correctly, so we're setting them here until we can resolve that
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.use_proxy = false" && \
    # ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.download_proxy = " && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.ssl_verify = false" && \
    # supports INFO, DEBUG, TRACE - use DEBUG or TRACE when debugging scheming Formulas
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.upload_log_level = INFO" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.formats = csv tsv tab ssv xls xlsx xlsxb xlsm ods geojson shp qgis zip" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.pii_screening = false" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.pii_found_abort = false" && \
    # ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.pii_regex_resource_id_or_alias =" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.pii_show_candidates = false" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.pii_quick_screen = false" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.qsv_bin = /usr/local/bin/qsvdp" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.preview_rows = 1000" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.download_timeout = 300" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.max_content_length = 1256000000000" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.chunk_size = 16384" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.default_excel_sheet = 0" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.sort_and_dupe_check = true" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.dedup = false" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.unsafe_prefix = unsafe_" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.reserved_colnames = _id" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.prefer_dmy = false" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.ignore_file_hash = true" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.auto_index_threshold = 3" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.auto_index_dates = true" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.auto_unique_index = true" && \
    # ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.summary_stats_options =" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.add_summary_stats_resource = false" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.summary_stats_with_preview = false" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.qsv_stats_string_max_length = 32767" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.qsv_dates_whitelist = date,time,due,open,close,created" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.qsv_freq_limit = 10" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.auto_alias = true" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.auto_alias_unique = false" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.copy_readbuffer_size = 1048576" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.type_mapping = {\"String\": \"text\", \"Integer\": \"numeric\",\"Float\": \"numeric\",\"DateTime\": \"timestamp\",\"Date\": \"date\",\"NULL\": \"text\"}" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.auto_spatial_simplication = true" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.spatial_simplication_relative_tolerance = 0.1" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.latitude_fields = latitude,lat" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.longitude_fields = longitude,long,lon" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.jinja2_bytecode_cache_dir = /tmp/jinja2_bytecode_cache" && \
    ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.auto_unzip_one_file = true" && \
    # Change ownership to app user
    chown -R ckan:ckan /srv/app && \
    # Create log directory for `ckan jobs worker` process
    mkdir -v /var/log/ckan

# Setup supervisor
COPY ./supervisord.conf /etc/supervisor/
COPY ./supervisor-ckan-worker.conf /etc/supervisor/conf.d/

# Remove wheels
RUN rm -rf /srv/app/wheels

# Copy necessary scripts
COPY setup/app ${APP_DIR}

WORKDIR ${APP_DIR}

# Create entrypoint directory for children image scripts
# Removed ONBUILD - ok?
RUN mkdir docker-entrypoint.d

# Create afterinit directory for children image scripts
# Removed ONBUILD - ok?
RUN mkdir docker-afterinit.d

# Run before prerun.py
COPY ./entrypoint.d ${APP_DIR}/docker-entrypoint.d
# Run after prerun.py
COPY ./afterinit.d ${APP_DIR}/docker-afterinit.d

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 CMD curl --fail http://0.0.0.0:5000/api/3/action/status_show || exit 1

RUN python -V
RUN pip -V
RUN pip list

CMD ["/srv/app/start_ckan.sh"]


# ┌─────────────────────────────────────────────────────────────┐
# │                                                             │
# │ Dev image (Development env)                                 │
# │ ---------------------------                                 │
# │ This is only built when ENV=dev                             │
# │                                                             │
# └─────────────────────────────────────────────────────────────┘


FROM base AS dev

# Install dev tools
RUN pip install flask-debugtoolbar==0.14.1
RUN pip install debugpy
RUN apt-get update && apt-get install --no-install-recommends -y \
    inotify-tools \
    psmisc \
    lsb-release \
    vim \
    nano \
    less

# Set DEBUG mode
RUN ckan config-tool ${APP_DIR}/production.ini "debug = true"

# Set DP+ log level to DEBUG or TRACE as appropriate
RUN ckan config-tool ${APP_DIR}/production.ini "ckanext.datapusher_plus.upload_log_level = TRACE"

CMD ["/srv/app/start_ckan_dev.sh"]

FROM ${ENV} AS final
