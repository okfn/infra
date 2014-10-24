# check-mk-agent Role

Installs the check_mk agent on either debian or ubuntu servers.  Also installed xinetd, changes the firewall and sets up some plugins.

## Tags

## Dependencies

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts --sudo --tags=

## Variables

iptables_config_file
check_mk_port
monitoring_server
enabled_plugin_check

local_checks_paths
