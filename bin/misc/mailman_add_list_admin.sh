#!/bin/sh

# See http://trac.okfn.org/ticket/922

lists=`sudo list_lists --bare`

TMP_FILE="/tmp/add_list_admin.${RANDOM}.py"

for list in ${lists} ; do
    before=`sudo config_list -o - $list | grep '^owner ='`

    cat <<EOF | python - > $TMP_FILE
${before}
la = 'list-admin@okfn.org'
if la not in owner:
    owner.insert(0, la)

print 'owner =', owner
EOF
  
    echo ""
    echo "#### $list ######################"
    echo "Before: ${before}"

    sudo config_list -i $TMP_FILE ${list}

    echo "After:  `sudo config_list -o - $list | grep '^owner ='`"
done 

rm $TMP_FILE
