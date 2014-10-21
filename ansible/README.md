# Ansible configuration management

This repository contains scripts and data used in managing the configuration of
the Open Knowledge Foundation's servers.

The files in this repository are used by
[Ansible](http://www.ansibleworks.com/).

## Using this repository

1. [Install Ansible](http://docs.ansible.com/intro_installation.html).

2. Clone this repository and
   [`okfn/credentials`](https://github.com/okfn/credentials) alongside one
   another.

3. Run `ansible-playbook` 

## Example invocations

Run plays that apply to nodes tagged with `monitoring`:

    ansible-playbook main.yml -t monitoring

Run play to add a new group and its users

    ansible-playbook main.yml -t add_group,add_users,add_ssh_keys,sudoers -e host=all

Run a play to just run one role

    ansible-playbook main.yml -vvvv -i inventory/hosts -s -t project_users -l s107.okserver.org

You can also use the `ansible` command directly to run tasks on remote hosts:

    ansible all -i inventory/hosts -e uptime

Adding -vvvv (or --verbose) will get you lots of useful debug info.

## Repository structure

### `main.yml`, `bootstrap.yml`, etc.

Top-level ansible playbooks.

### `roles/`

Application-specific configuration.

### `inventory/`

Host or host-group specific configuration. The main inventory lives at
`inventory/hosts` and host and group variables files live in
`inventory/{host,group}_vars`.

### `vars/`

Global variables, applicable to all hosts.

### `files/`

More application-specific configuration (?).
