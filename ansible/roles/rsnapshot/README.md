# rsnapshot Role

Installs and configures rsnapshot.  rsnapshot is a collection of perl scripts which is used to backup servers, through a series of snapshots.  It uses symlinks on unchanged files to keep the backup set size manageable.  We currently use it to backup our mailman install.

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts --sudo --tags=

## Variables

None
