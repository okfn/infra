# set-facts Role

This role is used to define and set_fact's before roles depending on those facts run, 
for e.g the 'sudo' role requires sudo_users to be defined which is setup by this set-facts role.

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts --sudo --tags=

## Variables

None
