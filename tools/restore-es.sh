#!/bin/bash

BATCH_SIZE=100

if [[ "${#}" -ne 4 ]]; then
  echo "Usage: $(basename $0) <elasticsearch host> <index name> <mapping.json> <documents.json>"
  echo 
  echo " e.g. $(basename $0) localhost:9200 posts posts_mapping_backup.json posts_docs_backup.json"
  exit 1
fi

ELASTICSEARCH="${1}"
INDEX="${2}"
MAPPING_FILE="${3}"
DOCUMENTS_FILE="${4}"

function json_get_key () {
  local key="${1}"
  python -c "import sys; import json; r = json.load(sys.stdin)['${key}']; print(r if isinstance(r, basestring) else json.dumps(r))"
}

function json_drop_key () {
  local key="${1}"
  python -c "import sys; import json; r = json.load(sys.stdin); r.pop('${key}', None); print(json.dumps(r))"
}

function json_add_key () {
  local key="${1}"
  local value="${2}"
  python -c "import sys; import json; r = json.load(sys.stdin); r['${key}'] = '${value}'; print(json.dumps(r))"
}

function terminate () {
  [[ -n "${bulkfile}" ]] && rm -f "${bulkfile}"
  exit 1
}
trap terminate SIGINT

echo "Creating index ${INDEX} with mappings from ${MAPPING_FILE}"
echo '{"mappings": '"$(cat "${MAPPING_FILE}")"'}' | curl -sS -XPUT "${ELASTICSEARCH}/${INDEX}" -d "@-"
echo
echo

echo "Loading documents"

bulkfile=$(mktemp restore-es-XXXXXX)

function do_bulk_upload () {
  curl -sS -XPOST "${ELASTICSEARCH}/${INDEX}/_bulk" --data-binary "@${1}" > /dev/null
}

i=0
total=0
while read -r doc; do
  echo '{"create": '"$(echo "${doc}" | json_drop_key _source)"'}' >> "${bulkfile}"
  echo "${doc}" | json_get_key _source >> "${bulkfile}"
  (( i += 1 ))

  if (( i >= BATCH_SIZE )); then
    do_bulk_upload "${bulkfile}"
    echo > "${bulkfile}" # clear bulk upload file
    (( i = 0 ))
    (( total += BATCH_SIZE ))
    echo "  uploaded ${total} documents"
  fi
done < "${DOCUMENTS_FILE}"

remaining=$(wc -l < "${bulkfile}")
if (( remaining > 0 )); then
  do_bulk_upload "${bulkfile}"
  (( total += remaining ))
  echo "  uploaded ${total} documents"
fi

rm "${bulkfile}"
echo "Done"
