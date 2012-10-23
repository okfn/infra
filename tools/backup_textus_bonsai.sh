#!/bin/bash

ES_HOST=index.bonsai.io

mkdir -p $1

while read ES_INDEX; do
	/home/okfn/hg-sysadmin/tools/backup-es.sh $ES_HOST $ES_INDEX &>/dev/null
	mv $ES_INDEX-documents-* $1
	mv $ES_INDEX-mappings-* $1
done < /root/heroku_es_index


