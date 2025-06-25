FROM bitnami/solr:9.8.0

USER root

ADD https://repo1.maven.org/maven2/org/locationtech/jts/jts-core/1.17.1/jts-core-1.17.1.jar /opt/bitnami/solr/server/solr-webapp/webapp/WEB-INF/lib/jts-core-1.17.1.jar

RUN chmod 644 /opt/bitnami/solr/server/solr-webapp/webapp/WEB-INF/lib/jts-core-1.17.1.jar

USER 1001
