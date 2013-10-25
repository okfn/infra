#!/bin/bash

#this config file is placed by ansible, look in the scripts role for mysql related scripts
backup_config=/opt/scripts/backup/mysql_backup.conf
backup_dir=/root/mysql_backups


if [ -f $backup_config ];
then
	rsync_target=$(awk -F: /backup_rsync_target/'{print $2}' $backup_config | sed -e 's/^ //g')
        db_list=$(awk -F: /db_backup_list/'{print $2}' ${backup_config} | sed -e 's/^ //g')	
	
	if [ ! -d ${backup_dir} ];
	then
		mkdir -p ${backup_dir}
	fi
	
	#delete any backup archives older than 3 days.	
	find ${backup_dir}/* -mtime +3 -exec rm {} \;
	
	for db in $db_list;
	do
		ts=$(date +%s)
		backup_archive="${ts}-$(hostname -s)-${db}-sql.gz"
		
		/usr/bin/mysqldump ${db} | gzip > ${backup_dir}/${backup_archive} 
		
		if [ -s ${backup_dir}/${backup_archive} ];
		then
			/usr/bin/rsync ${backup_dir}/${backup_archive} rsync://${rsync_target}/mysql_backups/
		fi	
	done
else
	echo "$backup_config not found, please check if you've defined the dbs to be backed up in ansible."
	exit 1
fi
