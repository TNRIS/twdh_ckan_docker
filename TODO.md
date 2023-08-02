X - db postgis init for ckan db
X - fix redis issues for ckanext security, login, etc
    X - add env vars for ckanext security, beaker
- ci/cd pipeline
    - build
    - test
    - push/fail

- who.ini
    - whodev.ini COPY into docker
    - whodev.ini set to sessions name = ckandev
    - push image
    - change CKAN___WHO__CONFIG_FILE = whodev.ini