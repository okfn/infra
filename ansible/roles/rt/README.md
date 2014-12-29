# rt Role

Installs and configures RT on a server.  It assumes that the RT database has already been setup and is stored on an existing database server.  In our case that's RDS, but this could be any other database server.  So this role is really for installing RT as a front-end.

This also installs a number of plugins, the current list is below:

https://github.com/bestpractical/rt-extension-activityreports
https://github.com/bestpractical/rt-extension-commandbymail
https://github.com/bestpractical/rt-extension-mergeusers
https://github.com/bestpractical/rt-extension-repeatticket
https://github.com/gitpan/RT-Extension-ResetPassword
https://github.com/bestpractical/rt-extension-spawnlinkedticketinqueue

## Usage

ansible-playbook --verbose main.yml -i inventory/hosts -s -t rt -l server.to.install.rt.on.tld

## Variables

None
