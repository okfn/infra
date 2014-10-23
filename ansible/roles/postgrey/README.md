# postgrey Role

Installs postgrey.  Postgrey is software which provides greylisting functionality to postgres.  Greylisting is whereby email not on the whitelist gets rejected initially, but allowed through after 10 minutes (configurable) once it's been allowed once it's whitelisted.  Spammers don't normally try more than once, so this cuts down on spam.

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts --sudo --tags=

## Variables

None
