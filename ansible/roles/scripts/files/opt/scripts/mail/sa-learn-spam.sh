#!/bin/sh
f=/tmp/spam-mail-$$
cat > ${f}
/usr/bin/sa-learn --spam $f &>/dev/null
rm $f
