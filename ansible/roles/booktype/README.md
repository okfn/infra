# booktype Role

Installs booktype from a custom deb.

## Tags

add_booktype_group
add_booktype_user
fetch_booktype_deb
install_booktype_deb
set_permissions_booktype

## Dependencies

 role: apt, pkg_list: ['git-core', 'python', 'python-dev', 'sqlite3', 'python-pip', 'python-virtualenv', 'redis-server', 'libxml2-dev', 'libxslt1-dev', 'libxslt1.1'] 
 role: supervisor 
 role: nginx 

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts --sudo --tags=

## Variables

None
