# tmpreaper Role

A role to install the tmpreaper software on a server.  tmpreaper can be used to clean down files over a certain age.  It's mainly intended to be used on the tmp directory.

## Tags

install_tmpreaper
configure_tmpreaper

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts --sudo --tags=

## Variables

None
