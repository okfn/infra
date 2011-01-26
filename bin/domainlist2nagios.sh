#!/bin/bash

MAX_HOST=15
DOMAIN="okfn.org"
UNKNOWN="otherhost"

WARNING="10"
CRITICAL="60"
SERVICE_TEMPLATE="okfn-webservice"


for i in `seq 0 1 ${MAX_HOST}`; do 
  HOST_NAME[$i]="eu${i}"
  HOST_CACHE[$i]="NO"
done
HOST_CACHE[6]="YES"
HOST_NAME[14]="us1"
HOST_NAME[15]="us2"


resolv() {
  PATTERN="[[:space:]]A[[:space:]]*" ; 
  host -t a $1 2>&1 | egrep "${PATTERN}" | sed -e "s/^.*${PATTERN}//g" | tail -1
}


for i in `seq 0 1 ${MAX_HOST}` ; do
  HOST_IP[$i]=`resolv ${HOST_NAME[$i]}.${DOMAIN}`
# echo "${HOST_NAME[$i]} = ${HOST_IP[$i]}"
done


cat << EOF
###################################################################
# This is an automatically created file, DO NOT EDIT
# Instead, create a list of domain names and pipe it though 
# $0


EOF

while read webdomain origin; do 
  webhost="${UNKNOWN}"
  cached="NO"
  webip=`resolv ${webdomain}`
  for i in `seq 0 1 ${MAX_HOST}` ; do
    if [ "X${webip}" = "X${HOST_IP[$i]}" ] ; then
      webhost="${HOST_NAME[$i]}"
      cached="${HOST_CACHE[$i]}"
      break
    fi
  done

  if [ "${cached}" = "YES" ]; then
     [ "${origin}" = "" ] && prefix="cache-xxx" || prefix="cache-${origin}"
  else
    prefix="HTTP"
  fi


  if [ "${webhost}" = "${UNKNOWN}" ] ; then
  # check="check_webpage!http://${webdomain}/"
    check="check_http_hostname2!${webdomain}"
  else
    check="check_http2!${webdomain}!${WARNING}!${CRITICAL}"
  fi

  cat << EOF
define service {
    service_description    ${prefix}-${webdomain}
    check_command          ${check}
    host                   ${webhost}
    use                    ${SERVICE_TEMPLATE}
}
    
EOF

done
