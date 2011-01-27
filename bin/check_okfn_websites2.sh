#!/bin/bash

# Author:  Nils Toedtmann <nils@toedtmann.net> 2011
# ToDo:    Make script autodetect apache/nginx/squid


DOMAIN="okfn.org"
MAX_HOST=15
HOST_NAME[15]="us1" # EXPLICITLY configure names of non "euXY" server hostnames
APACHE="0 1 2 3 4 5 7 8 9 13 14 15"
NGINX="10 12"
SQUID="6"
NO_OKFN="6"  # Servers where role account "okfn" does not work


WARNING="10"
CRITICAL="60"
SERVICE_TEMPLATE="okfn-webservice"


ALL=`seq 0 1 ${MAX_HOST}`
for i in $ALL; do 
    [ -z ${HOST_NAME[$i]} ] &&HOST_NAME[$i]="eu${i}"
    HOST_IP[$i]="not_resolved_yet"
    HOST_USER[$i]="okfn"
done


if [ -z "${1}" ] ; then
    NO_OKFN_USER="${USER}"
    NO_OKFN_SERVERS=`for s in ${NO_OKFN}; do echo -n ${HOST_NAME[$s]}; done`
    echo "NOTE: I assume you want to use your current username \"${NO_OKFN_USER}\" to log into the servers which do not" 1>&2
    echo "      accept the generic username \"okfn\" (${NO_OKFN_SERVERS}). Otherwise tell me as first argument." 1>&2
else 
    NO_OKFN_USER="${1}"
fi
for i in $NO_OKFN; do 
    HOST_USER[$i]="${NO_OKFN_USER}"
done


UNKNOWN_SERVER="OTHERHOST"
UNRESOLVED="DOES_NOT_RESOLV"
IGNORE="^(localhost|_|WILDCARD) "


DIR="/tmp/okfn-webservice-check"
CACHE_SERVERS="${DIR}/okfn-webservice-01-server-ips"
CACHE_SERVICES="${DIR}/okfn-webservice-02-configured"
CACHE_RESOLVED="${DIR}/okfn-webservice-03-resolved"
CACHE_MAPPING="${DIR}/okfn-webservice-04-mapping"
CACHE_NAGIOS="${DIR}/okfn-webservice-05-nagios"
SSH="ssh -4"
mkdir -p ${DIR}


######
# Function to resolv domain names to IP addresses across CNAMEs
# WARNING: Correct pattern depends on version of Bind's "host" tool! 

#HOST_PATTERN="[[:space:]]A[[:space:]]*" ; 
HOST_PATTERN="[[:space:]]has address[[:space:]]*" ; 
resolv() {
  host -t a ${1}. 2>&1 | egrep "${HOST_PATTERN}" | sed -e "s/^.*${HOST_PATTERN}//g" | tail -1
}



#######
# Part #1: resolv names of our servers {eu,us}*.okfn.org to IP addresses:
#
if [ -r ${CACHE_SERVERS} ] ; then
    echo "NOTE: using cached server IPs from ${CACHE_SERVERS} , remove this file to force new DNS lookup of servers" 1>&2
    while read j ip; do HOST_IP[$j]=${ip}; done < ${CACHE_SERVERS}
else
    echo    "NOTE: resolving hostnames of servers, caching results in ${CACHE_SERVERS}" 1>&2
    echo -n "      " 1>&2
    for i in `seq 0 1 ${MAX_HOST}` ; do
        echo -n "${HOST_NAME[$i]} " 1>&2
        HOST_IP[$i]=`resolv ${HOST_NAME[$i]}.${DOMAIN}`
        echo "$i ${HOST_IP[$i]}" 
    done > ${CACHE_SERVERS}
    echo " " 1>&2
fi
# Check result:
# for i in `seq 0 1 ${MAX_HOST}` ; do echo "${HOST_NAME[$i]} ${HOST_IP[$i]}" ; done


#######
# Part #2: Look into the apache/nginx/squid configs of all our hosts
#

if [ -r ${CACHE_SERVICES} ] ; then
    echo "NOTE: using cached service definitions from ${CACHE_SERVICES} , remove this file to force new gathering from servers" 1>&2
else
    echo "NOTE: Gathering service definitions from servers, caching results in ${CACHE_SERVICES}" 1>&2
    echo -n "      " 1>&2

    echo -n "SQUID: " 1>&2
    for s in ${SQUID}; do
        echo -n "${HOST_NAME[$s]} " 1>&2
        ${SSH} ${HOST_USER[$s]}@${HOST_NAME[$s]}.${DOMAIN} egrep "^[[:space:]]*acl[[:space:]]+[^[:space:]]*_sites[[:space:]]*dstdomain[[:space:]]*" /etc/squid3/squid.conf |\
        sed -e "s/_sites/ ${HOST_NAME[$s]}/g" | awk '{ print $5 " " $3 " Cache " $2 }'
    done | egrep -v $IGNORE >> ${CACHE_SERVICES}


    echo -n ";  NGINX: " 1>&2
    for s in ${NGINX}; do
        echo -n "${HOST_NAME[$s]} " 1>&2
        ${SSH} ${HOST_USER[$s]}@${HOST_NAME[$s]}.${DOMAIN} egrep -rh \'^[[:space:]]*server_name[[:space:]]+\' /etc/nginx/sites-enabled/  |\
        sed -e 's/;.*$//' -e 's/\*/WILDCARD/' -e "s/^.*server_name[[:space:]]*\(.*\)/\1/g" |\
        while read name aliases ; do 
            echo "$name ${HOST_NAME[$s]} Name"
            for alias in $aliases ; do 
                echo "$alias ${HOST_NAME[$s]} Alias" 
            done
        done
    done | egrep -v $IGNORE >> ${CACHE_SERVICES}


    echo -n ";  APACHE: " 1>&2
    for s in $APACHE; do
        echo -n "${HOST_NAME[$s]} " 1>&2
        ${SSH} ${HOST_USER[$s]}@${HOST_NAME[$s]}.${DOMAIN} egrep -hr \'^[[:space:]]*Server\(Name\|Alias\)[[:space:]]+\' /etc/apache2/sites-enabled/ | \
        sed -e "s/^[[:space:]]*Server\([NameAlias]*\)[[:space:]]*\(.*\)/\1 \2/g" -e 's/\*/WILDCARD/' | \
        while read type names; do
            for name in $names; do 
                echo "$name ${HOST_NAME[$s]} $type"
            done
        done
    done | egrep -v $IGNORE >> ${CACHE_SERVICES}

    echo " " 1>&2

fi


#######
# Part #3: Resolve all service domainnames and compare with server hostnames 
#

if [ -r ${CACHE_RESOLVED} ] ; then
    echo "NOTE: using cached service domain name resolutions ${CACHE_RESOLVED} , remove this file to force new DNS lookup" 1>&2
else
    echo    "NOTE: Resolving service domain names and comparing them with server IPs, caching results in ${CACHE_RESOLVED}" 1>&2
    echo -n "      " 1>&2

    cat ${CACHE_SERVICES} | awk '{print $1}' | sort -u |\
    while read webdomain; do 
        webhost="${UNKNOWN_SERVER}"
        webip=`resolv ${webdomain}`

        if [ "X${webip}" = "X" ] ; then
            echo -n "x" 1>&2
            echo    "${webdomain} ${UNRESOLVED}"
        elif [ "X${webip}" = "X10\." ] ; then
            echo -n "p" 1>&2
            echo    "${webdomain} RFC1918"
        else
            for i in `seq 0 1 ${MAX_HOST}` ; do
                if [ "X${webip}" = "X${HOST_IP[$i]}" ] ; then
                    webhost="${HOST_NAME[$i]}"
                    break
                fi
            done
            if [ ${webhost} = ${UNKNOWN_SERVER} ] ; then
                echo -n "." 1>&2
            else
                echo -n "o" 1>&2
            fi
            echo "${webdomain} ${webhost}"
        fi
    done > ${CACHE_RESOLVED}
    echo  "DONE" 1>&2
fi


#######
# Part #4: Check whether DNS and service definitions match, and print matches
#

if [ -r ${CACHE_MAPPING} ] ; then
    echo "NOTE: using cached service-to-server mappings from ${CACHE_MAPPING} , remove this file to force fresh mapping" 1>&2
else
    echo "NOTE: Mapping services to servers, caching results in ${CACHE_RESOLVED}" 1>&2
    echo " " 1>&2

    cat ${CACHE_RESOLVED} | while read domain res_server; do
        if [ "${res_server}" = "${UNRESOLVED}" ]; then
            echo -n "    WARN: ${domain} is configured on " 1>&2
            egrep "^${domain} *" ${CACHE_SERVICES} | grep -v "${UNRESOLVED}" | while read d s rest; do echo -n "${s}," ; done 1>&2 
            echo " but does not resolv!" 1>&2
        elif [ "${res_server}" = "${UNKNOWN_SERVER}" ]; then
            echo "${domain} ${res_server} Unknown ${res_server}"
        elif [ "${res_server}" = "RFC1918" ]; then
            echo "    INFO: ${domain} resolves to RFC1918 IP address, ignoring" 1>&2
        else
            #echo "${domain}"
            res_line=`egrep "^${domain} *${res_server} *" ${CACHE_SERVICES}`
            if [ "X${res_line}" = "X" ]; then 
                echo "    WARN: ${domain} is pointing to ${res_server} but is not configured there!" 1>&2
            fi
            echo "${res_line}" |while read d r type origin ; do
                #echo "D=${domain} R=${res_server} d=$d r=$r type=$type origin=$origin"
                case $type in
                    "Name"|"Alias")
                        echo "${domain} ${res_server} ${type} ${res_server}"
                        ;;

                    "Cache")
                        found="0"
                        grep "^${domain} *${origin}" ${CACHE_SERVICES} | while read d2 o2 type2 ; do
                            found="1"
                            echo "${domain} ${res_server} ${type2} ${origin}"
                        done
                        if [ ${found} = "0" ]; then
                            echo "    WARN: ${domain} is pointing to proxy ${res_server}, but origin ${origin} does not feel responsible!" 1>&2
                        fi
                        ;;

                    "*")
                        echo "    WARN: ${domain} of unknown type ${type}!" 1>&2
                        ;;
                esac
                if [ "${origin}" = "" ]; then origin=${res_server}; fi
                egrep "^${domain} " ${CACHE_SERVICES} | egrep -v "^${domain} *${origin} " | grep -v " Cache "| while read d r t o ; do
                    echo "    INFO: ${domain} is configured on ${r}, but neither DNS nor proxy are pointing to that." 1>&2
                done
            done
        fi
    done > ${CACHE_MAPPING}
    echo " " 1>&2
fi


#######
# Part #5: Create Nagios service definitions from our mapping
#

if [ -r ${CACHE_NAGIOS} ] ; then
    echo "NOTE: Nagios config ${CACHE_NAGIOS} already there. Remove this file to write a fresh one" 1>&2
else
    echo "NOTE: Using services-to-servers mapping to generate Nagios configuration file ${CACHE_NAGIOS} " 1>&2
    echo " " 1>&2


###
cat << EOF > ${CACHE_NAGIOS}
##############################################################################
# This is an automatically generated file. Might get overwritten occasionally!
# 


EOF
###

    while read domain res_server type origin; do
        if [ "${res_server}" = "${UNKNOWN_SERVER}" ] ; then
            # check="check_webpage!http://${webdomain}/"
            check="check_http_hostname2!${domain}"
        else
            check="check_http2!${domain}!${WARNING}!${CRITICAL}"
        fi
        if [ ${type} = "Alias" ] ; then
            echo "      INFO: ${domain} is only a ServerAlias, not adding to Nagios config." 1>&2
        else
            # Check origin
####
cat << EOF
define service {
    service_description    http-${domain}
    check_command          ${check}
    host                   ${origin}
    use                    ${SERVICE_TEMPLATE}
}
    
EOF
####

            # Check proxy too, if there is
            if ! [ ${res_server} = ${origin} ]; then
####
cat << EOF
define service {
    service_description    cache-${origin}-${domain}
    check_command          ${check}
    host                   ${res_server}
    use                    ${SERVICE_TEMPLATE}
}
    
EOF
####
            fi # If Cache
        fi # if Alias

    done < ${CACHE_MAPPING} > ${CACHE_NAGIOS}

fi


