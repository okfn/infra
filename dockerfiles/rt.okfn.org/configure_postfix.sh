
#!/bin/sh


RELAY_IP=$(route -n | awk /UG/'{print $2}' | head -1)

echo "setup relay host to ${RELAY_IP}"
sed -e 's/RELAY_IP/'${RELAY_IP}'/g' -i /etc/postfix/main.cf
sed -e 's/WEB_DOMAIN/'${WEB_DOMAIN}'/g' -i /etc/postfix/main.cf
sed -e 's/WEB_DOMAIN/'${WEB_DOMAIN}'/g' -i /etc/postfix/procmailrc.rt

cp /etc/resolv.conf /var/spool/postfix/etc/
cp /etc/services /var/spool/postfix/etc/

newaliases -C /etc/postfix

echo 'All done.'

