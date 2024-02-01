##################
### Build CKAN ###
##################
FROM ubuntu:focal-20210827 as ckanbuild

# Set CKAN version to build

ENV GIT_URL=https://github.com/TNRIS/ckan.git
ENV GIT_BRANCH=twdh-patches-2.9.9

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
        python3.8-venv \
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
# Downgrade setuptools so that CKAN requirements can be built
RUN pip install --upgrade pip
RUN pip install setuptools==44.1.0
RUN pip install wheel

# Fetch and build CKAN and requirements
RUN pip install -e git+${GIT_URL}@${GIT_BRANCH}#egg=ckan

RUN pip wheel --wheel-dir=${VIRTUAL_ENV}/src -r ckan/requirements.txt

#############
### MAIN ####
#############
FROM ubuntu:focal-20210827

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
# must add geo_view for ckanext-spatial views
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
    twdh_theme \
    security \
    report \
    check_link \
    text_view \
    webpage_view \
    image_view \
    video_view \
    datastore \
    harvest \
    ckan_harvester \
    spatial_metadata \
    spatial_query \
    twdh_schema \
    scheming_datasets \
    scheming_organizations \
    composite \
    contact \
    pages \
    resource_proxy \
    geo_view \ 
    geojson_view \
    wmts_view \
    shp_view \
    datatablesview_plus \
    datapusher \
    openapi_viewer \
    s3filestore \
    googleanalytics \
    ags_fs_view \ 
    twdh_gazetteer \
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
    python3.8-venv \
	python3-distutils \
	libpython3.8 \
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
# Downgrade setuptools so that CKAN requirements can be built
RUN pip install --upgrade pip
RUN pip install setuptools==44.1.0
RUN pip install wheel

# Get artifacts from build stages
COPY --from=ckanbuild ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=ckanbuild ${WHEEL_DIR} /srv/app/wheels
COPY --from=ckanbuild ${CKAN_DIR} ${CKAN_DIR}
COPY ./plugins ${SRC_DIR}/plugins

RUN ls ${SRC_DIR}/plugins

# Additional install steps for build stages artifacts
RUN pip install uWSGI==2.0.20 gevent==21.12.0
# Create a local user and group to run the app
RUN groupadd -g 92 ckan && \
    useradd -rm -d /srv/app -s /bin/bash -g ckan -u 92 ckan

WORKDIR ${CKAN_DIR}


# Install CKAN
RUN pip install -e /srv/app/src/ckan
# COPY overwrite.who.ini into app dir for ckanext-security required configurations
COPY ./overwrite.who.ini ${APP_DIR}/who.ini
COPY ./overwrite.who.dev.ini ${APP_DIR}/devwho.ini

# comment out below if using ckanext-security and use own who.ini
RUN pip install --no-index --find-links=/srv/app/wheels -r requirements.txt
RUN pip install future

# Generate CKAN config
RUN ckan generate config ${APP_DIR}/production.ini
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
    ckan config-tool ${APP_DIR}/production.ini "scheming.dataset_schemas = ckanext.twdh_schema:schemas/dataset.yaml ckanext.twdh_schema:schemas/application.yaml" && \
    ckan config-tool ${APP_DIR}/production.ini "scheming.organization_schemas = ckanext.twdh_schema:schemas/organization.yaml" && \
    ckan config-tool ${APP_DIR}/production.ini "scheming.presets = ckanext.scheming:presets.json ckanext.composite:presets.json ckanext.twdh_schema:schemas/presets.yaml" && \
    # add ckan.spatial.search_backend to enable solr spatial search
    ckan config-tool ${APP_DIR}/production.ini "ckanext.spatial.search_backend = solr-bbox" && \
    # change default logo to tx water logo from cdn.tnris.org
    ckan config-tool ${APP_DIR}/production.ini "ckan.site_logo = https://cdn.tnris.org/images/Hub_NavIcon_dark.png" && \
    # add config option for google analytics download view
    ckan config-tool ${APP_DIR}/production.ini "googleanalytics.id = G-SJK5R9G5F5" && \
    ckan config-tool ${APP_DIR}/production.ini "googleanalytics.download_handler = ckanext.s3filestore.views:resource_download" && \
    # Change ownership to app user
    chown -R ckan:ckan /srv/app

# Remove wheels
RUN rm -rf /srv/app/wheels

# Copy necessary scripts
COPY setup/app ${APP_DIR}

WORKDIR ${APP_DIR}

# Create entrypoint directory for children image scripts
ONBUILD RUN mkdir docker-entrypoint.d

# Create afterinit directory for children image scripts
ONBUILD RUN mkdir docker-afterinit.d

# Run before prerun.py
COPY ./entrypoint.d ${APP_DIR}/docker-entrypoint.d
# Run after prerun.py
COPY ./afterinit.d ${APP_DIR}/docker-afterinit.d

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 CMD curl --fail http://0.0.0.0:5000/api/3/action/status_show || exit 1

USER ckan

CMD ["/srv/app/start_ckan.sh"]
