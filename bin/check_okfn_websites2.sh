#!/bin/bash

# Author:  Nils Toedtmann <nils@toedtmann.net> 2011
# ToDo:    Make script autodetect apache/nginx/squid


DOMAIN="okfn.org"
MAX_HOST=26
# EXPLICITLY configure names of non "euXY" server hostnames
HOST_NAME[17]="us1" 
HOST_NAME[18]="us2" 
HOST_NAME[19]="us3" 
HOST_NAME[20]="us4" 
HOST_NAME[21]="us5" 
HOST_NAME[22]="us6" 
HOST_NAME[23]="us7" 
HOST_NAME[24]="us8" 
HOST_NAME[25]="us9" 
HOST_NAME[26]="us10" 
#PACHE="0 1 2 3 4 5 7 9 13 14 15 17 19 20 24 25"
APACHE="0 1 2   4 5 7 9 13 14 15 17 19 20 24 25"
NGINX="10 12 16 22"
SQUID="6"
# NO_OKFN="6"  # Servers where role account "okfn" does not work
NO_OKFN="" 


IGNORE_HOSTNAME="^(localhost|_|WILDCARD) "
IGNORE_ORIGIN="^(river)$"


WARNING="10"
CRITICAL="60"
SERVICE_TEMPLATE="okfn-webservice"
SLOW_HOSTS="eu3"
#SLOW_HOSTS_DIRECTIVE="check_interval                3600 # Don't annoy server too much with checks"
SLOW_HOSTS_DIRECTIVE="active_checks_enabled         0"


ALL=`seq 0 1 ${MAX_HOST}`
for i in $ALL; do 
    [ -z ${HOST_NAME[$i]} ] &&HOST_NAME[$i]="eu${i}"
    HOST_IP[$i]="not_resolved_yet"
    HOST_USER[$i]="okfn"
done


stderr() {
  echo -n "${@}" 1>&2
}

stderrn() { 
  echo   "${@}" 1>&2
}


if [ -z "${1}" ] ; then
    NO_OKFN_USER="${USER}"
    NO_OKFN_SERVERS=`for s in ${NO_OKFN}; do echo -n ${HOST_NAME[$s]}; done`
    stderrn "NOTE: I assume you want to use your current username \"${NO_OKFN_USER}\" to log into the servers which do not" 
    stderrn "      accept the generic username \"okfn\" (${NO_OKFN_SERVERS}). Otherwise tell me as first argument." 
else 
    NO_OKFN_USER="${1}"
fi
for i in $NO_OKFN; do 
    HOST_USER[$i]="${NO_OKFN_USER}"
done


UNKNOWN_SERVER="OTHERHOST"
UNRESOLVED="DOES_NOT_RESOLV"


DIR="/tmp/okfn-webservice-check"
CACHE_SERVERS="${DIR}/okfn-webservice-01-server-ips"
CACHE_SERVICES="${DIR}/okfn-webservice-02-configured"
CACHE_SERVICEIPS="${DIR}/okfn-webservice-03-service-ips"
CACHE_RESOLVED="${DIR}/okfn-webservice-04-resolved"
CACHE_MAPPING="${DIR}/okfn-webservice-05-mapping"
CACHE_NAGIOS="${DIR}/okfn-webservice-06-nagios"
SSH="ssh -4"
mkdir -p ${DIR}


######
# Function to resolv domain names to IP addresses across CNAMEs
# WARNING: Correct pattern depends on version of Bind's "host" tool! 

HOST_PATTERN1="[[:space:]]*A[[:space:]]*" ;
HOST_PATTERN2="[[:space:]]*has address[[:space:]]*" ;    
HOST_PATTERN="[[:space:]]+(has address|A)[[:space:]]+" ; 

resolv() {
    host -t a ${1}. 2>&1 | grep -v "A record currently not present" | egrep "${HOST_PATTERN}" | sed -e "s/^.*${HOST_PATTERN1}//g" -e "s/^.*${HOST_PATTERN2}//g" | tail -1
}



#######
# Part #1: resolv names of our servers {eu,us}*.okfn.org to IP addresses:
#
if [ -r ${CACHE_SERVERS} ] ; then
    stderr "NOTE: using cached server IPs from ${CACHE_SERVERS} , remove this file to force new DNS lookup of servers" 
    while read j ip; do HOST_IP[$j]=${ip}; done < ${CACHE_SERVERS}
else
    stderrn    "NOTE: resolving hostnames of servers, caching results in ${CACHE_SERVERS}" 
    stderr "      " 
    for i in `seq 0 1 ${MAX_HOST}` ; do
        stderr "${HOST_NAME[$i]} " 
        HOST_IP[$i]=`resolv ${HOST_NAME[$i]}.${DOMAIN}`
        echo "$i ${HOST_IP[$i]}" 
    done > ${CACHE_SERVERS}
    stderrn " " 
fi
# Check result:
# for i in `seq 0 1 ${MAX_HOST}` ; do echo "${HOST_NAME[$i]} ${HOST_IP[$i]}" ; done


#######
# Part #2: Look into the apache/nginx/squid configs of all our hosts
#

remove_newline() {
    echo $@
}


if [ -r ${CACHE_SERVICES} ] ; then
    stderrn "NOTE: using cached service definitions from ${CACHE_SERVICES} , remove this file to force new gathering from servers" 
else
    stderrn "NOTE: Gathering service definitions from servers, caching results in ${CACHE_SERVICES}" 
    stderr "      " 

    stderr "SQUID: " 
    for s in ${SQUID}; do
        stderr "${HOST_NAME[$s]} " 
        ${SSH} ${HOST_USER[$s]}@${HOST_NAME[$s]}.${DOMAIN} egrep "^[[:space:]]*acl[[:space:]]+[^[:space:]]*_sites[[:space:]]*dstdomain[[:space:]]*" /etc/squid3/squid.conf |\
        sed -e "s/_sites/ ${HOST_NAME[$s]}/g" | awk '{ print $5 " " $3 " Cache " $2 }'
    done | egrep -v $IGNORE_HOSTNAME >> ${CACHE_SERVICES}


    stderr ";  NGINX: " 
    for s in ${NGINX}; do
        stderr "${HOST_NAME[$s]} " 
        ${SSH} ${HOST_USER[$s]}@${HOST_NAME[$s]}.${DOMAIN} egrep -rh \'^[[:space:]]*server_name[[:space:]]+\' /etc/nginx/sites-enabled/  |\
        sed -e 's/;.*$//' -e 's/\*/WILDCARD/' -e "s/^.*server_name[[:space:]]*\(.*\)/\1/g" |\
        while read name aliases ; do 
            echo "$name ${HOST_NAME[$s]} Name"
            for alias in $aliases ; do 
                echo "$alias ${HOST_NAME[$s]} Alias" 
            done
        done
    done | egrep -v $IGNORE_HOSTNAME >> ${CACHE_SERVICES}


    stderr ";  APACHE: " 
    for s in $APACHE; do
        stderr "${HOST_NAME[$s]} " 
        APACHE_CONFIG="/etc/apache2/sites-enabled/"
        APACHE_INCLUDES=`${SSH} ${HOST_USER[$s]}@${HOST_NAME[$s]}.${DOMAIN} egrep -hr \'^[[:space:]]*Include[[:space:]]+\' ${APACHE_CONFIG} | \
        awk '{print $2}' | sort -u`
        APACHE_CONFIG+=" `remove_newline ${APACHE_INCLUDES}`"
        # stderr "==>${APACHE_CONFIG}<=="

        ${SSH} ${HOST_USER[$s]}@${HOST_NAME[$s]}.${DOMAIN} egrep -hr \'^[[:space:]]*Server\(Name\|Alias\)[[:space:]]+\' ${APACHE_CONFIG} | \
        sed -e "s/^[[:space:]]*Server\([NameAlias]*\)[[:space:]]*\(.*\)/\1 \2/g" -e 's/\*/WILDCARD/' | \
        while read type names; do
            for name in $names; do 
                echo "$name ${HOST_NAME[$s]} $type"
            done
        done
    done | egrep -v $IGNORE_HOSTNAME >> ${CACHE_SERVICES}

    stderrn " " 

fi


#######
# Part #3: Resolve all service domainnames to IP addresses 
#

if [ -r ${CACHE_SERVICEIPS} ] ; then
    stderrn "NOTE: Reading cached service IP addresses from ${CACHE_SERVICEIPS} and caching new results there."
    stderrn "      Remove this file to force new DNS lookup of all services" 
else
    stderrn "NOTE: Resolving service domain names to IP addresses, caching results in ${CACHE_SERVICEIPS}"
fi

stderr      "      " 

cat ${CACHE_SERVICES} | awk '{print $1}' | sort -u |\
while read webdomain; do 
    if grep -q "^${webdomain} " ${CACHE_SERVICEIPS}; then 
        stderr "."
    else
        webip=`resolv ${webdomain}`
        if [ "X${webip}" = "X" ] ; then
            stderr "-" 
            echo "${webdomain} ${UNRESOLVED}"
        else
            stderr "x" 
          # stderrn "x ${webdomain} x ${webip} x"
            echo "${webdomain} ${webip}"
        fi
      fi
done >> ${CACHE_SERVICEIPS}
sort -o ${CACHE_SERVICEIPS} ${CACHE_SERVICEIPS}
stderrn  " DONE" 


#######
# Part #4: Compare IP addresses of services and servers
#

if [ -r ${CACHE_RESOLVED} ] ; then
    stderrn "NOTE: using cached comparison of service and server IP addresses from ${CACHE_RESOLVED} , remove this file to force new comparison" 
else
    stderrn "NOTE: Comparing service and server IP addresses, caching results in ${CACHE_RESOLVED}" 
    stderr  "      " 

    cat ${CACHE_SERVICEIPS} | sort -u |\
    while read webdomain webip; do 
        webhost="${UNKNOWN_SERVER}"
        if [ "${webip}" = "${UNRESOLVED}" ] ; then
            stderr "-" 
            echo    "${webdomain} ${UNRESOLVED}"
        elif echo "X${webip}" | grep -q "^X10\." ; then
            stderr "p" 
            echo    "${webdomain} RFC1918"
        else
            for i in `seq 0 1 ${MAX_HOST}` ; do
                if [ "X${webip}" = "X${HOST_IP[$i]}" ] ; then
                    webhost="${HOST_NAME[$i]}"
                    break
                fi
            done
            if [ ${webhost} = ${UNKNOWN_SERVER} ] ; then
                stderr "o" 
            else
                stderr "x" 
            fi
            echo "${webdomain} ${webhost}"
        fi
        # stderrn "${webdomain} YY ${webip} ZZ ${webhost}"
    done > ${CACHE_RESOLVED}
    stderrn  " DONE" 
fi


#######
# Part #5: Check whether DNS and service definitions match, and print matches
#

if [ -r ${CACHE_MAPPING} ] ; then
    stderrn "NOTE: using cached service-to-server mappings from ${CACHE_MAPPING} , remove this file to force fresh mapping" 
else
    stderrn "NOTE: Mapping services to servers, caching results in ${CACHE_RESOLVED}" 
    stderrn " " 

    cat ${CACHE_RESOLVED} | while read domain res_server; do
        if [ "${res_server}" = "${UNRESOLVED}" ]; then
            egrep "^${domain} *" ${CACHE_SERVICES} | grep -v "${UNRESOLVED}" | while read d s rest; do 
              stderrn "    WARN: ${s} : ${domain} is configured here but does not resolv!" ; 
            done
        elif [ "${res_server}" = "${UNKNOWN_SERVER}" ]; then
            echo "${domain} ${res_server} Unknown ${res_server}"
        elif [ "${res_server}" = "RFC1918" ]; then
            stderrn "    INFO: ${domain} resolves to RFC1918 IP address, ignoring" 
        else
            #echo "${domain}"
            res_line=`egrep "^${domain} *${res_server} *" ${CACHE_SERVICES}`
            if [ "X${res_line}" = "X" ]; then 
              stderrn "    WARN: ${res_server} : ${domain} is pointing here but ${res_server} does not feel responsible!" 
            fi
            echo "${res_line}" |while read d r type origin ; do
                #echo "D=${domain} R=${res_server} d=$d r=$r type=$type origin=$origin"
                case $type in
                    "Name"|"Alias")
                        echo "${domain} ${res_server} ${type} ${res_server}"
                        ;;

                    "Cache")
                        origin_service=`grep "^${domain} *${origin}" ${CACHE_SERVICES}`
                        if [ "X${origin_service}" = "X" ] ; then
                          # stderrn "if ! echo \"${origin}\" | egrep -q \"${IGNORE_ORIGIN}\" ; then"
                            if ! echo "${origin}" | egrep -q "${IGNORE_ORIGIN}" ; then
                                stderrn "    WARN: ${origin} : ${domain} is pointing to proxy ${res_server}, but origin ${origin} does not feel responsible!" 
                            fi
                        else 
                            echo "${origin_service}" | while read d2 o2 type2 ; do
                                echo "${domain} ${res_server} ${type2} ${origin}"
                              # stderrn "   FOUND: ${domain} ${res_server} ${type2} ${origin}"
                            done
                        fi 
                        ;;

                    "*")
                        stderrn "    WARN: ${domain} of unknown type ${type}!" 
                        ;;
                esac
                if [ "${origin}" = "" ]; then origin=${res_server}; fi
                egrep "^${domain} " ${CACHE_SERVICES} | egrep -v "^${domain} *${origin} " | grep -v " Cache "| while read d r t o ; do
                    stderrn "    INFO: ${r} : ${domain} is configured on ${r}, but neither DNS nor proxy are pointing to that." 
                done
            done
        fi
    done | sort -u > ${CACHE_MAPPING}
    stderrn " " 
fi


#######
# Part #6: Create Nagios service definitions from our mapping
#

if [ -r ${CACHE_NAGIOS} ] ; then
    stderrn "NOTE: Nagios config ${CACHE_NAGIOS} already there. Remove this file to write a fresh one" 
else
    stderrn "NOTE: Using services-to-servers mapping to generate Nagios configuration file ${CACHE_NAGIOS} " 
    stderrn " " 


###
cat << EOF > ${CACHE_NAGIOS}
##############################################################################
# This is an automatically generated file. Might get overwritten occasionally!
# 


EOF
###

    while read domain res_server type origin; do
        ADD_DIRECTIVE=""
        # SLOW_HOSTS check_interval=60
        if echo "${SLOW_HOSTS}" | egrep -q "${origin}([^0-9]|$)" ; then 
            ADD_DIRECTIVE="${SLOW_HOSTS_DIRECTIVE}"
        fi
        if [ "${res_server}" = "${UNKNOWN_SERVER}" ] ; then
            # check="check_webpage!http://${webdomain}/"
            check="check_http_hostname2!${domain}"

######            
cat << EOF
# Webservice "${domain} on host ${origin}"
define service {
    service_description           http-${domain}
    check_command                 ${check}
    host                          ${origin}
    use                           ${SERVICE_TEMPLATE}
}


EOF
######

        else
            check="check_http2!${domain}!${WARNING}!${CRITICAL}"
        
            if [ ${type} = "Alias" ] ; then
                stderrn "      INFO: ${domain} is only a ServerAlias, not adding to Nagios config." 
            else
            
######  Check origin
cat << EOF
# Webservice "${domain} on host ${origin}"
define service {
    service_description           http-${domain}
    check_command                 ${check}
    host                          ${origin}
    use                           ${SERVICE_TEMPLATE}
    ${ADD_DIRECTIVE}
}
define servicedependency {
    host_name                     ${origin}
    service_description           HTTP
    dependent_host_name           ${origin}
    dependent_service_description http-${domain}
}


EOF
######

                if ! [ ${res_server} = ${origin} ]; then
                  
######  Check proxy too
cat << EOF
# Webservice "${domain} on host ${origin}, proxied on ${res_server}"
define service {
    service_description           cache-${origin}-${domain}
    check_command                 ${check}
    host                          ${res_server}
    use                           ${SERVICE_TEMPLATE}
    ${ADD_DIRECTIVE}
}
define servicedependency {
    host_name                     ${res_server}
    service_description           HTTP
    dependent_host_name           ${res_server}
    dependent_service_description cache-${origin}-${domain}
}
define servicedependency {
    host_name                     ${origin}
    service_description           http-${domain}
    dependent_host_name           ${res_server}
    dependent_service_description cache-${origin}-${domain}
}


EOF
####
                fi # If proxy
            fi # if Alias
        fi # if OTHERHOST
    done < ${CACHE_MAPPING} > ${CACHE_NAGIOS}

fi


