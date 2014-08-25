#!/bin/bash

#this config file is placed by ansible, look in the scripts role for mysql related scripts
#this script expects /root/.my.cnf to be in place with the passwords
       
backup_config=/opt/scripts/backup/mysql_backup.conf
backup_dir=/root/mysql_backups
db_host=localhost
db_port=3306
mysql_exclude_dbs='information_schema performance_schema'
       

if [ -f $backup_config ];
then   
        rsync_target=$(awk -F: /backup_rsync_target/'{print $2}' $backup_config | sed -e 's/^ //g')
        db_list=$(mysql -e "show databases" --skip-column-names -B)
     
		exclude_dbs=$(awk -F: /mysql_exclude_dbs/'{print $2}' ${backup_config} | sed -e 's/^ //g')
		if [ ! -z "${exclude_dbs}" ];
		then
			mysql_exclude_dbs="${mysql_exclude_dbs} ${exclude_dbs}"
		fi

        port=$(awk -F: /mysql_port/'{print $2}' ${backup_config} | sed -e 's/^ //g')
        if [ ! -z "${port}" ];
        then   
                db_port=${port}
        fi
       
        host=$(awk -F: /mysql_host/'{print $2}' ${backup_config} | sed -e 's/^ //g')
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
                echo $mysql_exclude_dbs | grep -P '\b'${db}'\b' -q
                if [ $? -eq 1 ];
                then   
                        ts=$(date +%s)
                        backup_archive="${ts}-$(hostname -s)-${db}-sql.gz"
                        
                        /usr/bin/mysqldump -uroot -P${db_port} -h${db_host} ${db} | gzip > ${backup_dir}/${backup_archive} 
                        
                        if [ -s ${backup_dir}/${backup_archive} ];
                        then
                                /usr/bin/rsync ${backup_dir}/${backup_archive} rsync://${rsync_target}/mysql_backups/
                        fi
                fi
        done
else   
        echo "$backup_config not found, please check if you've defined the dbs to be backed up in ansible."
        exit 1
fi 
