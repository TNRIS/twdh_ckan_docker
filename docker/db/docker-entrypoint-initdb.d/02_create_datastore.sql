CREATE ROLE datastore WITH LOGIN NOCREATEDB NOCREATEROLE ENCRYPTED PASSWORD 'datastore';
CREATE DATABASE datastore WITH OWNER datastore;
