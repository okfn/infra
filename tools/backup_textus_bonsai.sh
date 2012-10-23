#!/bin/bash

ES_HOST=index.bonsai.io
ES_INDEX=`cat /root/heroku_es_index`

/home/okfn/hg-sysadmin/tools/backup-es.sh $ES_HOST $ES_INDEX
mkdir -p $1
mv $ES_INDEX-documents-* $1
mv $ES_INDEX-mappings-* $1


