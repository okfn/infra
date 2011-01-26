#!/bin/bash

SQUID_CFG=~okfn/etc/squid3/squid.conf


egrep "^acl *[^ ]*_sites *dstdomain *" ${SQUID_CFG} | sed -e 's/_sites//g' | awk '{ print $4 " " $2 }'
