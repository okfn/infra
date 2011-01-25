#!/bin/bash

SQUID_CFG=~okfn/etc/squid3/squid.conf


egrep "^acl *[^ ]*_sites *dstdomain *" ${SQUID_CFG} | awk '{ print $4 }'
