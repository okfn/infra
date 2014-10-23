# db-backup Role

Copies a number of backup scripts over to the server and makes sure they're running in cron.

## Tags

ensure_backup_scripts_dir
ensure_backup_cron
copy_backup_scripts
psql_backup_config
mysql_backup_config

## Dependencies

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts --sudo --tags=

## Variables

None
