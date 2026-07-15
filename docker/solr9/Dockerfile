FROM ckan/ckan-solr:2.10-solr9.9-spatial

USER root

COPY ./docker-entrypoint-initdb.d/overwrite.schema.xml /opt/solr-9.9.0/server/solr/configsets/ckan/conf/managed-schema

USER 1001
