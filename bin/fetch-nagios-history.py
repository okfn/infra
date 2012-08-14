#!/usr/bin/python

# Call this script and pipe its output through bash
# <nils.toedtmann@okfn.org> 2012-08


# Nagios credentials
nagios_base     = 'https://monitor-okfn.fry-it.com/cgi-bin/nagios2'
nagios_username = 'okfn'
nagios_password = '********'


# Hosts of which we want the Nagios history
nagios_hosts = ['s045.okfn-db', 's046.okfn-solr', 's047.okfn-datanl', 's048.okfn-datagm', 's049.okfn-iati', 's050.okfn-cache', 's051.okfn-db2', 's052.okfn-solr2', 's053.okfn-blogfarm', 's054.okfn-datacatalogs', 's055.okfn-thedatahub', 's057.okfn-ckanfarm', 's058.okfn-backup', 's059.okfn-ops', 's063.okfn-webapps1', 's064.okfn-pad', 's065.okfn-elasticsearch2', 's066.okfn-lov']


# Months of which we want the Nagios history
list_of_months = []
for m in range(7,13) :
    list_of_months.append((2011, m))
for m in range(1,9) :
    list_of_months.append((2012, m))


import datetime, time
def month_epoch(year, month):
    if month > 12 :
        year += 1
        month -= 12
    return int(time.mktime(datetime.datetime(year, month, 1, 0, 0, 0).timetuple()))


for host in nagios_hosts :
    for (year, month) in list_of_months:
        t1 = month_epoch(year, month)
        t2 = month_epoch(year, month+1)

        URL = '%s/avail.cgi?host=%s&t1=%s&t2=%s' % (nagios_base, host, t1, t2)
        command = "wget --user=%s --password=%s -O %s-%s-%02d.html '%s'" % (nagios_username, nagios_password, host, year, month, URL)
        print command

print '''sed -e 's,/nagios2/stylesheets/,,' -i ./s0*.html'''

print 'echo "Also download the stylesheets into this dir"'
