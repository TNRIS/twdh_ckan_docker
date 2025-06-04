#!/bin/bash
#
# Initialize SOLR for CKAN by creating a ckan core
# Arguments are supplied via environment variables: CKAN_CORE_NAME CKAN_VERSION
# Example:
#   CKAN_CORE_NAME=ckan
#   CKAN_VERSION=2.10.5

set -e

CKAN_SOLR_SCHEMA_URL=https://raw.githubusercontent.com/TNRIS/twdh_ckan_docker/refs/heads/twdh-0.8.0-dev/docker/solr9/solr-configset/overwrite.schema.xml

echo "Check whether managed schema exists for CKAN $CKAN_VERSION"
if ! curl --output /dev/null --silent --head --fail "$CKAN_SOLR_SCHEMA_URL"; then
  echo "Can't find CKAN SOLR schema at URL: $CKAN_SOLR_SCHEMA_URL. Exiting..."
  exit 1
fi

echo "Check whether SOLR is initialized for CKAN"
CORESDIR=/var/solr/data

COREDIR="$CORESDIR/$CKAN_CORE_NAME"
if [ -d "$COREDIR" ]; then
    echo "SOLR already initialized, skipping initialization"
else
    echo "Initializing SOLR core $CKAN_CORE_NAME for CKAN $CKAN_VERSION"
    # init script for handling an empty /var/solr
    /opt/solr/docker/scripts/init-var-solr
    
    # Precreate CKAN core
    /opt/solr/docker/scripts/precreate-core $CKAN_CORE_NAME
    
    # Replace the managed schema with CKANs schema
    echo "Adding CKAN managed schema"
    curl $CKAN_SOLR_SCHEMA_URL -o /var/solr/data/$CKAN_CORE_NAME/conf/managed-schema -s
    
    echo "SOLR initialized"
fi

