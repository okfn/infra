#!/bin/bash

set -e

wp_site="okfn.org"
wp_db="wordpress_okfn_org"
wp_user="wp_okfn_org"

wp_config="/home/okfn/var/wp/okfn.org/wp-config.php"
wp_pass=`grep "^define.*DB_PASSWORD" ${wp_config} | cut -d "'" -f 4`

db_server_1="db-euw1.okserver.org"
db_server_2="db-sov.okserver.org"

if ! [ "`ssh ${db_server_2} sudo id -u`" == "0" ] ; then
    echo "ERROR: cannot log into ${db_server_2} - log in with agent forwarding."
    exit 1
fi

echo "Emptying database ${wp_db}@${db_server_2} ..."
ssh ${db_server_2} mysql -h ${db_server_2} -u root --password=`ssh ${db_server_2} sudo cat /etc/mysql/my.pw` <<EOF
DROP   DATABASE ${wp_db};
CREATE DATABASE ${wp_db};
GRANT USAGE ON *.* TO '${wp_user}'@'%' IDENTIFIED BY '${wp_pass}';
GRANT ALL PRIVILEGES ON ${wp_db}.* TO '${wp_user}'@'%';
QUIT
EOF

echo "Start of migration: `date`"

echo "Disabling site ${wp_site}"
sudo a2dissite ${wp_site}
sudo sudo /etc/init.d/apache2 reload

echo "Copying database ${wp_db}@${db_server_1} ==> ${wp_db}@${db_server_2} ..."
mysqldump -h ${db_server_1} -u ${wp_user} --password=${wp_pass} ${wp_db} | mysql -h ${db_server_2} -u ${wp_user} --password=${wp_pass} ${wp_db}

echo "Changing WP config"
sudo cp -a ${wp_config} ${wp_config}.ORIG
sudo sed -e "s/^\(define.'DB_HOST', '\).*\('.;\)/\1${db_server_2}\2/" -i ${wp_config}

echo "Enabling site ${wp_site} ..."
sudo a2ensite ${wp_site}
sudo sudo /etc/init.d/apache2 reload

echo "End of migration: `date`"
