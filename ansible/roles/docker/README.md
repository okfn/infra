# docker Role

Installs docker and them makes sure all the okfn docker containers are running.  This is currently mariadb, etherpad, booktype, opensendy and RT.

## Tags

start-mariadb55
start-okfnpad
start-booktype
start-sendy
start-rt

## Dependencies

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts --sudo --tags=

## Variables

None
