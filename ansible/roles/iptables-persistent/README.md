# iptables-persistent Role

Installs and configures iptables-persistent.

## Tags

install_iptables_persistent
iptables_config

## Dependencies

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts --sudo --tags=

## Variables



None

## Notes

This command will throw a dpkg error on linode hosts because linode does not
allow modprobe, the fix is to run the following:

sudo sed \
    -i 's/\(modprobe -q ip6\?table_filter\)/\1 || true/g' \
    /var/lib/dpkg/info/iptables-persistent.postinst; \
sudo apt-get install iptables-persistent

See https://forum.linode.com/viewtopic.php?t=9070&p=58732

