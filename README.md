Ansible playbook setup:
---

#main.yml

This file is the top level ansible file, which should include config for hosts from all projects,
Ansible will be invoked with main.yml in cron to ensure the config across all hosts is consistent according to the playbooks.

#inventory/
This folder holds the 'hosts' file, which sorts hosts into groups/projects based on datacenter/project etc
The inventory/{host_vars,group_vars} folder contains files which have host specific variables defined.

#files/ 
contains all of the application/${project} specific config files, which are included when deploying applications

#handlers/
contains restart/reload, mainly service related plays

#playbooks/
contains plays on a per host or per application basis

#tasks/
contains plays that might be run just once, e.g bootstrap a server, inject keys or such.

#templates/
contains jinja2 templates for config files that need to be generated on a per host basis, e.g a vhost for somedomain.ckan.org

#vars/
contains variables that are global across all plays.


Get Ansible running
---

#Fetch source:
``` git clone https://github.com/ansible/ansible```

#Setup env:
``` source ansible/hacking/env-setup```

#Run playbook: 
(if the playbook uses the okfn user)  
``` ansible-playbook --connection=ssh  --extra-vars="host=s999.okserver.org" tasks/ckan-dbserver-setup.yml  -i inventory/hosts  -vv ```

#Run plays using thier tags from the playbook:
``` ansible-playbook --connection=ssh  --extra-vars="host=s999.okserver.org" tasks/ckan-dbserver-setup.yml  -i inventory/hosts  -vv --tags="jetty_config,fetch_solr_config" ```

#Run commands across all hosts:
``` ansible all -m command -a uptime -u okfn --connection=ssh ```

#Run commands on the ckan group of servers:
``` ansible ckan -m command -a uptime -u okfn --connection=ssh ```
