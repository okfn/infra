#!/bin/bash

MAX_HOST=15
DOMAIN="okfn.org"
UNKNOWN="otherhost"


for i in `seq 0 1 ${MAX_HOST}`; do 
  HOST_NAME[$i]="eu${i}"
done
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


while read webdomain; do 
  webhost="${UNKNOWN}"
  webip=`resolv ${webdomain}`
  for i in `seq 0 1 ${MAX_HOST}` ; do
    if [ "X${webip}" = "X${HOST_IP[$i]}" ] ; then
      webhost="${HOST_NAME[$i]}"
      break
    fi
  done

  # alternative: "check_webpage!http://${webdomain}/"

  cat << EOF
define service {
    service_description    HTTP-${webdomain}
    check_command          check_http_hostname2!${webdomain}
    host                   ${webhost}
    use                    generic-service
}
    
EOF

done
