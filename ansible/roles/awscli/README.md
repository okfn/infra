# apt Role

Installs pip, then awscli and then configures awscli using keys supplied through extra vars.

## Tags

awscli

## Dependencies

## Usage

ansible-playbook main.yml --verbose -i inventory/hosts --extra-vars="awscli_aws_access_key_id=accesskey awscli_aws_secret_access_key=secretaccesskey awscli_region=ireland" -t awscli -l s138.okserver.org -s

## Variables

None

