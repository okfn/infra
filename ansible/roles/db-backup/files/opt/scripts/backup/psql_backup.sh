#!/bin/bash

#this script expects /root/.pgpass to be in place with the passwords - if the default user is postgres

backup_config=/opt/scripts/backup/psql_backup.conf
backup_dir=/root/psql_backups
db_host=localhost
db_port=5432
db_admin=postgres
pg_pass=/root/.pgpass
psql_exclude_dbs='template1 template0'
snitch=304f7bf902

function deadmansnitch()
{
  curl "https://nosnch.in/$1" &> /dev/null
}


if [ -f $backup_config ];
then
	rsync_target=$(awk -F: /backup_rsync_target/'{print $2}' $backup_config | sed -e 's/^ //g')
	
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
	
	dbadmin=$(awk -F: /psql_db_admin/'{print $2}' ${backup_config} | sed -e 's/^ //g')
	if [ ! -z "${dbadmin}" ];
	then
	        db_admin=${dbadmin}
	fi
		
		
	if [ "$db_admin" = "postgres" ]; #we assume the db is locally hosted
	then
		db_list=$(su - postgres -c "psql -l -t" | awk -F'|' '{print $1}' | sed  -e '/^\s*$/d'  -e 's/^ //g')
	else	
		db_list=$(psql -U${db_admin} -h${db_host} -p${db_port} -l -t | awk -F'|' '{print $1}' | sed  -e '/^\s*$/d'  -e 's/^ //g')
		if [ ! -f ${pg_pass} ];
		then
			echo "$0 requires ${pg_pass} in place to backup sucessfully."
			exit 1
		fi
	fi

	if [ -z "${db_admin}" ];
	then
		echo  "could not get list of dbs to backup, exiting"
		exit 1
	fi

	exclude_dbs=$(awk -F: /psql_exclude_dbs/'{print $2}' ${backup_config} | sed -e 's/^ //g')
	if [ ! -z "${exclude_dbs}" ];
	then
		psql_exclude_dbs="${psql_exclude_dbs} ${exclude_dbs}"
	fi

	if [ ! -d ${backup_dir} ];
	then
		mkdir -p ${backup_dir}
	fi
		
	#delete any backup archives older than 3 days.  
	find ${backup_dir}/* -mtime +3 -exec rm {} \;

	for db in $db_list;
	do  
		echo $psql_exclude_dbs | grep -P '\b'${db}'\b' -q
		if [ $? -eq 1 ];
		then
		
			ts=$(date +%s)
			backup_archive="${ts}-$(hostname -s)-${db}-pql.gz"

			if [ "$db_admin" = "postgres" ]; #we assume the db is locally hosted
			then
				su - postgres -c "/usr/bin/pg_dump ${db}" | gzip > ${backup_dir}/${backup_archive}
			else	
				/usr/bin/pg_dump -U${db_admin} -h${db_host} -p${db_port} ${db} | gzip > ${backup_dir}/${backup_archive}
			fi
			
			if [ -s ${backup_dir}/${backup_archive} ];
			then
			    /usr/bin/rsync ${backup_dir}/${backup_archive} rsync://${rsync_target}/psql_backups
				if [ $? -ne 0 ];
				then
					echo "Failed: /usr/bin/rsync ${backup_dir}/${backup_archive} rsync://${rsync_target}/psql_backups"
					echo "Ensure $(hostname) IP is whitelisted on ${rsync_target}"
					exit 1
				fi
	   		fi
		fi		
	deadmansnitch($snitch)

	done
else
        echo "$backup_config not found, please check if you've defined the dbs to be backed up in ansible."
        exit 1
fi

