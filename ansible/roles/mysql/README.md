# mysql Role

Installs and configures percona mysql.

## Tags

mysql
add_percona_aptkeys
add_percona_repo_src
install_percona_pkgs
install_vanilla_mysql
setup_mysqlpass_fact
setup_mysql_root_user
setup_mysql_monitor_user
setup_mysql_root_cnf

## Dependencies

- { role: apt, pkg_list: ['python-mysqldb', 'python-apt', 'python-pycurl'] }
- { role: scripts } #adds backup script

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts --sudo --tags=

## Variables

None
