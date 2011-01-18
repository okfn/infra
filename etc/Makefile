help:

	@echo 'Usage: make SUBDIRS="munin squid3 ..." install'

install:
	for dir in ${SUBDIRS}; do make -C $$dir install; done
