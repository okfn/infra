# okfn-org-manager Role

A custom role to install a few different things on okfn servers.  Including awscli, okfn-heroku-copyapp and a cronjob to move prod data to staging.

## Tags

None

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts --sudo --tags=

## Variables

None
