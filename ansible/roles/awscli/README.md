# awscli Role

Installs pip, then awscli and then configures awscli using keys supplied through extra vars.

We have an extra store for the variables so you need to specify that with setting a private_dir extra var.  For example:

    - "{{ private_dir }}/p.yml"

And in p.yml you'll need the following:

aws_keys:
  - 
    id: user0
    key: somekey
    secret_key: somesecretkey
    region: eu-west-1
  - 
    id: user1
    key: key
    secret_key: secretkey
    region: eu-west-2


So if you want user0 you'd call it like this in main.yml:

- hosts: s138.okserver.org
  sudo: true
  vars_files:
    - "{{ private_dir }}/p.yml"
  roles:
    - role: awscli
      tags: ['awscli']
      key: "{{ aws_keys[0].key }}"
      secret_key: "{{ aws_keys[0].secret_key }}"
      region: "{{ aws_keys[0].region }}"
      


Just change the number to reference the key you want.



## Tags

awscli
awscli_install
awscli_create_config_dir
awscli_configure

## Dependencies

## Usage

Ideally specify the variables in main.yml, but you can pass them on the command line like this:

ansible-playbook main.yml --verbose -i inventory/hosts --extra-vars="awscli_user_home=/root awscli_user=root awscli_group=root" -t awscli -l s138.okserver.org -s

Or assuming that you've defined everything in main.yml just:

ansible-playbook main.yml --verbose -i inventory/hosts -t awscli -l s138.okserver.org -s

## Variables

awscli_aws_access_key - the access key
awscli_aws_secret_access_key
awscli_region - the region, we're normally ireland
aws_user_home - has to start with a slash but have no trailing slash.  eg /home/bob or /root
awscli_user - a specific user for the config to go in
awscli_group - a specific group for the config to go in

