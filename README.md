Get Ansible running
---

####Fetch source:
``` git clone https://github.com/ansible/ansible```

####Setup env:
``` source ansible/hacking/env-setup```

####Run playbook: 
(if the playbook uses the okfn user)  
``` ansible-playbook --connection=ssh  --extra-vars="host=s999.okserver.org" tasks/ckan-dbserver-setup.yml  -i inventory/hosts  -vv ```

####Run plays using thier tags from the playbook:
``` ansible-playbook --connection=ssh  --extra-vars="host=s999.okserver.org" tasks/ckan-dbserver-setup.yml  -i inventory/hosts  -vv --tags="jetty_config,fetch_solr_config" ```

####Run commands across all hosts:
``` ansible all -m command -a uptime -u okfn --connection=ssh ```

####Run commands on the ckan group of servers:
``` ansible ckan -m command -a uptime -u okfn --connection=ssh ```


Ansible playbook directory structure
---

####main.yml

This file is the top level ansible file, which should include config for hosts from all projects,
Ansible will be invoked with main.yml in cron to ensure the config across all hosts is consistent according to the playbooks.

####roles/
All applications are managed using its respective role


####inventory/
This folder holds the 'hosts' file, which sorts hosts into groups/projects based on datacenter/project etc
The inventory/{host_vars,group_vars} folder contains files which have host specific variables defined.

####tasks/
contains plays that might be run just once, e.g bootstrap a server, inject keys or such.

####vars/ 
contains variables that are global across all plays (users)

####files/ 
contains all of the application/${project} specific config files, which are included when deploying applications

####handlers/ (only used by tasks)
contains restart/reload, mainly service related plays

####templates/ (only used by tasks)
contains jinja2 templates for config files that need to be generated on a per host basis, e.g a vhost for somedomain.ckan.org


OKF Ansible host specific magic vars ( define under inventory/host_vars/$host or inventory/hosts )
----

####disable_nagios_checks
Define this var, and run the check_mk role to disable ALL nagios checks for the host, the host will essentially be removed from nagios.
Accepted args are True/False
e.g
        disable_nagios_checks=True


####disabled_checks
disabled_checks accepts an array of elements which the names of local passive checks that should be disabled for a host.
Once added to the host var file, the check_mk-server role should be invoked to apply changes to the nagios server.
e.g
        disabled_checks: ['apt-security-check']

see check_mk local checks http://mathias-kettner.de/checkmk_localchecks.html

####backup_postgres
This was added to identify hosts that need postgres to be backed up, and a cronjob was added to each host that defines it.
Accepted args are True/False 
e.g
        backup_postgres=true

####sites_to_monitor
This var expects an array with elements  '<domain.name>:<port>:<http_status>', 
It is used by the check_mk play to add http nagios checks.
e.g

        sites_to_monitor: ['subdomain.okfn.org:80:301','foo.bar:8000:200']

http_status is the expected normal http status return code.

####sites_enabled
This var expects an array of domain names, which have been added into the nginx/apache (sites-available folder) and need to be enabled.
e.g
        
        sites_enabled: ['new-site.okfn.org']

####rsnapshot_backup
This var is fed is used by the rsnapshot role to build the rsnaphot config running on the backup host.
It expects one or more array elements which contain key, value pairs (src, dest, exclude)

Each array element should define 'src' , 'dest' values, 'exclude' is optional.

e.g
        rsnapshot_backup:
           - { src: 'root@somehost:/home/okfn/', dest: 'somehost/' }
           - { src: 'root@somehost:/var/lib/munin/', dest: 'somehost/' }

####rsnapshot_backup_scripts
This var is similar to rsnapshot_backup, except it defines the scripts rsnapshot needs to run for the backup process of a host.
All keys must be defined (src, script, dest)

e.g
        rsnapshot_backup_script:
            - { src: '/usr/bin/ssh       somehost.org', script: '"/usr/bin/sudo -u postgres /usr/bin/pg_dumpall | gzip > /var/backups/pgdump.sql.gz"', dest: 'empty/1' }

####ban_abusive_ips
This var expects an array of ips that should be blocked on the server, its used by the iptables-persistent role.

e.g
        ban_abusive_ips: ['192.168.1.1', '192.168.1.2']

####custom_iptables_rules
This var expects an array of rules that should be directly applied to the server, was added to allow adding custom rules without having to create rule files for each host.
