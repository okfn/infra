# collectd Role

Installs collectd.  collectd is a daemon which collects system performance statistics periodically and provides mechanisms to store the values in a variety of ways, for example in RRD files.  We run a custom version of collectd and have a debfile just for that.

## Tags

collectd
fetch_collectd_deb
install_collectd_deb
setup_collectd_config
collectd_init_script
reload_collectd

## Dependencies

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts --sudo --tags=

## Variables

None
