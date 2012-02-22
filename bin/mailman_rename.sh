#!/bin/bash
OLD=$1
NEW=$2
#service mailman stop
test -a /var/lib/mailman/archives/private/${NEW} && echo "*** That mailing list name already exists. *** " 
mv /var/lib/mailman/lists/${OLD} /var/lib/mailman/lists/${NEW}
mv /var/lib/mailman/archives/private/${OLD} /var/lib/mailman/archives/private/${NEW} 
mv /var/lib/mailman/archives/private/${OLD}.mbox /var/lib/mailman/archives/private/${NEW}.mbox 
mv /var/lib/mailman/archives/private/${NEW}.mbox/${OLD}.mbox /var/lib/mailman/archives/private/${NEW}.mbox/${NEW}.mbox 
/usr/lib/mailman/bin/arch ${NEW}
#service mailman start
