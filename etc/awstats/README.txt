## Howto

### 0. Preliminaries

Two main config files in /etc/awstats:

  awstats.conf
  awstats.conf.local

Usually defaults will do since we are just going to include these in
site-specific file and override some values. May need to ensure that
awstats.conf does *not* include awstas.conf.local.

### 1. Create Config

For each domain copy awstats.conf.template to:

  awstats.${DOMAIN_NAME}.conf

Edit the file as necessary (instructions in file). T

### 2. Symlink

Symlink the file to /etc/awstats

### 3. Add to cron (cron.d/awstats if it exists) a command like

35 5 * * * root  /usr/lib/cgi-bin/awstats.pl -config=${DOMAIN_NAME}
-update >/dev/null

