# apt Role

Installs pip, then awscli and then configures awscli using keys supplied through extra vars.

## Tags

awscli
awscli_install
awscli_create_config_dir
awscli_configure

## Dependencies

## Usage

ansible-playbook main.yml --verbose -i inventory/hosts --extra-vars="awscli_aws_access_key_id=accesskey awscli_aws_secret_access_key=secretaccesskey awscli_region=ireland aws_user_home=/root awscli_user=root awscli_group=root" -t awscli -l s138.okserver.org -s

## Variables

awscli_aws_access_key - the access key
awscli_aws_secret_access_key
awscli_region - the region, we're normally ireland
aws_user_home - has to start with a slash but have no trailing slash.  eg /home/bob or /root
awscli_user - a specific user for the config to go in
awscli_group - a specific group for the config to go in

