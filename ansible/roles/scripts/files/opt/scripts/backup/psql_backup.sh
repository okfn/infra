#!/bin/bash

#this script expects /root/.pgpass to be in place with the passwords

backup_config=/opt/scripts/backup/psql_backup.conf
backup_dir=/root/psql_backups
db_host=localhost
db_port=5432
db_admin=dbadmin
pg_pass=/root/.pgpass

if [ ! -f ${pg_pass} ];
then
	echo "$0 requires ${pg_pass} in place to backup sucessfully."
	exit 1
fi


if [ -f $backup_config ];
then
	rsync_target=$(awk -F: /backup_rsync_target/'{print $2}' $backup_config | sed -e 's/^ //g')
        db_list=$(awk -F: /psql_backup_list/'{print $2}' ${backup_config} | sed -e 's/^ //g')
	
	port=$(awk -F: /psql_port/'{print $2}' ${backup_config} | sed -e 's/^ //g')	
	if [ ! -z "${port}" ]; 
	then
		db_port=${port}
	fi

	host=$(awk -F: /psql_host/'{print $2}' ${backup_config} | sed -e 's/^ //g')	
	if [ ! -z "${host}" ];
	then
		db_host=${host}
	fi

	if [ ! -d ${backup_dir} ];
	then
		mkdir -p ${backup_dir}
	fi
	
	#delete any backup archives older than 3 days.	
	find ${backup_dir}/* -mtime +3 -exec rm {} \;
	
	for db in $db_list;
	do
		ts=$(date +%s)
		backup_archive="${ts}-$(hostname -s)-${db}-pql.gz"
		
		/usr/bin/pg_dump -U${db_admin} -h${db_host} -p${db_port} ${db} | gzip > ${backup_dir}/${backup_archive}
		if [ -s ${backup_dir}/${backup_archive} ];
		then
			/usr/bin/rsync ${backup_dir}/${backup_archive} rsync://${rsync_target}/psql_backups
		fi	
	done
else
	echo "$backup_config not found, please check if you've defined the dbs to be backed up in ansible."
	exit 1
fi
