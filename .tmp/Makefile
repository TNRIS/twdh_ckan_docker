CONTAINER = $(shell docker ps | grep 29_ckan | cut -d ' ' -f1)


patchPlugin:    
	@echo ${CONTAINER}

	docker cp ./plugin.py ${CONTAINER}:/srv/app/src/ckan/ckanext-twdh_theme/ckanext/twdh_theme