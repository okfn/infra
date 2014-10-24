# nodejs Role

Adds a node.js ppa and then installs node.js.

## Tags

install_nodejs

## Dependencies

- { role: apt, pkg_list: [ 'python-pycurl' ] }

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts --sudo --tags=

## Variables

None
