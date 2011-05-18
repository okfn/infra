#!/bin/bash

#
# This (terrible) script expects the bash variables EC2_CERT and EC2_PRIVATE_KEY 
# to be properly set and exported. E.g. i do this:
# 
#    export EC2_CERT=~/.aws/aws-cert-okfn.pem
#    export EC2_PRIVATE_KEY=~/.aws/aws-pk-okfn.pem
#
# Ask me for the cert and key files if you need them. /nils
#


REVERSE_DNS="/tmp/okfn.org-reverse"
DOMAIN="okfn.org"

hosts="us1 us2 us3 us4 us5 us6 eu0 eu1 eu2 eu3 eu4 eu5 eu6 eu7 eu8 eu9 eu10 eu11 eu12 eu13 eu14 eu15 eu16 eu18 bkn-1 bkn-2 epsi"


resolv() {
    HOST_PATTERN1="[[:space:]]*A[[:space:]]*" ;
    HOST_PATTERN2="[[:space:]]*has address[[:space:]]*" ;    
    HOST_PATTERN="[[:space:]]+(has address|A)[[:space:]]+" ; 

    host -t a ${1}. 2>&1 | \
        grep -v "A record currently not present" | \
        egrep "${HOST_PATTERN}" | \
        sed -e "s/^.*${HOST_PATTERN1}//g" -e "s/^.*${HOST_PATTERN2}//g" | \
        tail -1
}


if ! [ -f ${REVERSE_DNS}  ] ; then 
    for h in ${hosts} ; do 
        echo "s/^`resolv ${h}.${DOMAIN}|sed -e 's,\.,\\.,g'`/${h}.${DOMAIN}/"
    done > ${REVERSE_DNS}
fi

#REGEXP=$(cat ${REVERSE_DNS} | awk '{print " -e '\''s,^" $1 "," $2 ",'\''"}' | sed ':a;N;$!ba;s/\n//g')
#REGEXP=$(cat ${REVERSE_DNS} | awk '{print " -e s,^" $1 "\t," $2 "\t,"}' | sed ':a;N;$!ba;s/\n//g')


regions="us-east-1 eu-west-1"

for region in $regions ; do
    ec2-describe-instances --region ${region} | \
        grep -v ^RESERVATION | \
        sed -e '/BLOCKDEVICE/s/\t\([^\t]*\)\t\([^\t]*\).*$/:\2:\1,/g' -e 's/instance-store/inst/g' -e "s,^INSTANCE,${region}," | \
        sed ':a;N;$!ba;s/\nBLOCKDEVICE://g' | \
        sed ':a;N;$!ba;s/\nTAG//g' | \
        cut  -f 1,2,6,10,17,21,27,31 |\
        awk '{print $5 "\t" $5 "\t" $2 "\t" $1 "\t" $4 "\t" $3 "\t" $6 "\t" $7 "\t" $8 }' | \
        sed -f ${REVERSE_DNS}
done

