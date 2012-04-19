#!/bin/bash

SCROLL_SIZE=100
TODAY=$(date +'%Y%m%d')

if [[ "${#}" -ne 2 ]]; then
  echo "Usage: $(basename $0) <elasticsearch host> <index name>"
  echo 
  echo " e.g. $(basename $0) localhost:9200 posts"
  exit 1
fi

ELASTICSEARCH="${1}"
INDEX="${2}"

function json_get_key () {
  local key="${1}"
  python -c "import sys; import json; r = json.load(sys.stdin)['${key}']; print(r if isinstance(r, basestring) else json.dumps(r))"
}

function json_drop_key () {
  local key="${1}"
  python -c "import sys; import json; r = json.load(sys.stdin); r.pop('${key}', None); print(json.dumps(r))"
}

function json_array_to_lines () {
  python -c "import sys; import json; [sys.stdout.write(json.dumps(o) + '\n') for o in json.load(sys.stdin)]"
}

function get_batch () {
  local res=$(curl -sS -XGET "${ELASTICSEARCH}/_search/scroll?scroll=10m&scroll_id=${scroll_id}")
  local hits=$(echo "${res}" | json_get_key hits | json_get_key hits | json_array_to_lines)

  if [[ -n "${hits}" ]]; then
    scroll_id="$(echo "${res}" | json_get_key _scroll_id)"
    
    echo "${hits}" | while read -r line; do
      echo "${line}" | json_drop_key "_index" | json_drop_key "_score"
    done
  else
    scroll_id=""
  fi
}

echo "Writing mappings to ${INDEX}-mappings-${TODAY}.json"
curl -sS -XGET "${ELASTICSEARCH}/${INDEX}/_mapping" | json_get_key "${INDEX}" > "${INDEX}-mappings-${TODAY}.json"


res=$(curl -sS -XGET -d '{"query":{"match_all":{}}}' \
           "${ELASTICSEARCH}/${INDEX}/_search?search_type=scan&scroll=10m&size=${SCROLL_SIZE}")
scroll_id=$(echo "${res}" | json_get_key _scroll_id)

echo "Writing docs to ${INDEX}-documents-${TODAY}.json"
while [[ -n "${scroll_id}" ]]; do
  get_batch
  echo " got batch" 1>&2
done > "${INDEX}-documents-${TODAY}.json"

