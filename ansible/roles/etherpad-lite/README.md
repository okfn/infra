# etherpad-lite Role

Installs and configures etherpad.  Installs nodejs as well.  Suspect that it would be better if it just used the nodejs role to do that.  

## Tags

add_etherpad_group
add_etherpad_user
git_checkout_etherpad
set_permissions_etherpad
settings_config_etherpad

## Dependencies

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts --sudo --tags=

## Variables

None
