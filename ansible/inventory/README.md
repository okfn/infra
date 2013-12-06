# OKF custom host vars

The following custom host variables are used in this inventory:

## `disable_nagios_checks`

Define this var, and run the `check_mk` role to disable ALL nagios checks for
the host, the host will essentially be removed from nagios.

Accepted args are True/False

    disable_nagios_checks=True

## `local_checks`

`local_checks` expects an array of check scripts which are `check_mk` specific and
need to be enabled on the host. Setting this var adds the script into the `check_mk` agent local checks folder, from which `check_mk` will periodically run scripts.

    local_checks: ['exim_mailqueue']

## `check_graphite`

`check_graphite` is an array of metrics from graphite to be monitored, each array element looks like 

    '<metric.datapoint>:timeperiod:<warning level>:<critical level>'
e.g
    ['mail_metrics.mailman.subscribe.lod2.pending:-1hours:20:30']

## `check_parameters`

`check_parameters` is an array of parameters should be used per check, these apply to both inventorized and manually defined checks,
each array element should be in the format:

    <check name>:<warning level>:<critical level>

 e.g: 

     check_parameters: ['Postfix Queue:80:120']

For more details on [checkmk_check parameters](check parameters http://mathias-kettner.de/checkmk_check_parameters.html)



## `disabled_checks`

`disabled_checks` accepts an array of elements with the names of local passive
checks that should be disabled for a host. Once added to the host var file, the `check_mk-server` role should be invoked to apply changes to the nagios server.

    disabled_checks: ['apt-security-check']

For further reference see [`check_mk` local checks](http://mathias-kettner.de/checkmk_localchecks.html)

## `backup_postgres`

This was added to identify hosts that need postgres to be backed up, and a
cronjob was added to each host that defines it.

Accepted args are True/False

    backup_postgres=True

## `sites_to_monitor`

This var expects an array with elements `<domainname>:<port>:<http_status>`.
It is used by the `check_mk` play to add http nagios checks.

    sites_to_monitor: ['subdomain.okfn.org:80:301','foo.bar:8000:200']

`http_status` is the expected normal http status return code.

## `sites_enabled`

This var expects an array of domain names, which have been added into the
nginx/apache (sites-available folder) and need to be enabled.

    sites_enabled: ['new-site.okfn.org']

## `rsnapshot_backup`

This var is used by the rsnapshot role to build the rsnaphot config
running on the backup host. It expects one or more array elements which contain key, value pairs (required: `src`, `dest`; optional: `exclude`)

    rsnapshot_backup:
      - { src: 'root@somehost:/home/okfn/', dest: 'somehost/' }
      - { src: 'root@somehost:/var/lib/munin/', dest: 'somehost/' }

## `rsnapshot_backup_scripts`

This var is similar to rsnapshot_backup, except it defines the scripts rsnapshot
needs to run for the backup process of a host. All keys must be defined (`src`, `script`, `dest`)

    rsnapshot_backup_script:
      - { src: '/usr/bin/ssh       somehost.org', script: '"/usr/bin/sudo -u postgres /usr/bin/pg_dumpall | gzip > /var/backups/pgdump.sql.gz"', dest: 'empty/1' }

## `ban_abusive_ips`

This var expects an array of IPs that should be blocked on the server. It is used
by the iptables-persistent role.

    ban_abusive_ips: ['192.168.1.1', '192.168.1.2']

## `custom_iptables_rules`

This var expects an array of rules that should be directly applied to the
server, was added to allow adding custom rules without having to create rule
files for each host.

## `graphite_collectors`

This variable expects an array of graphite collector script names. This allows
us to include just the right collector scripts, and add its cronjob on each
host/group.

    graphite_collectors: ['exim_stats.py', 'mailman_stats.py']

## `timezone`

This variable allows us to define the timezone for each host/group, which is
then setup by the ntpd role. The defined timezone should be a tz file defined under `/usr/share/zoneinfo`
 
    timezone: UTC


