#!/usr/bin/env python
'''
check_solr.py - v0.2 -  Chris Ganderton <github@thefraggle.com>

Nagios check script for checking replication issues and ping status on solr slaves.

We simply get the local generation that the core reports it has, and
then query the maximum possible replicateableGeneration the master has told the core about.

OPTIONS:

-H : hostname/ip of the solr server we want to query
-p : tcp port solr is listening on
-W : webapp path
-P : ping the solr cores on given webapp (not to be used with replication check)
-r : check replication on the given webapp (not to be used with ping check)
-w : delta between master and local replication version, to warn on (default 1)
-c : delta between master and local replication version, to crit on (defualt 2)
-i : ignore a core, use multiple times to ignore multiple cores.

EXAMPLE: ./check_solr_rep.py -H localhost -p 8093 -W solr -r -w 10 -c 20

'''
import urllib, json, sys
from optparse import OptionParser

def listcores():
    status_cmd  = baseurl + core_admin_url + urllib.urlencode({'action':'status','wt':'json'})
    print status_cmd
    cores       = set()

    res         = urllib.urlopen(status_cmd)
    data        = json.loads(res.read())

    core_data   = data['status']

    for core_name in core_data:
        cores.add(core_name)

    return cores

def repstatus(core):
    rep_cmd     = baseurl + core + '/replication?' + urllib.urlencode({'command':'details','wt':'json'})

    rres        = urllib.urlopen(rep_cmd)
    rdata       = json.loads(rres.read())

    localgeneration  = rdata['details'].get('generation')
    mastergeneration = rdata['details']['slave']['masterDetails']['master'].get('replicatableGeneration')

    if mastergeneration == None or localgeneration == None:
        status = "CRITICAL"
        return status

    generationdiff   = mastergeneration - localgeneration

    if generationdiff > threshold_warn:
        status = "WARNING"
    elif generationdiff > threshold_crit:
        status = "CRITICAL"
    else:
        status = "UNKNOWN"

    return status

def solrping(core):
    ping_cmd = baseurl + core + '/admin/ping?' + urllib.urlencode({'wt':'json'})

    res = urllib.urlopen(ping_cmd)
    data = json.loads(res.read())

    status = data.get('status')

    return status

def main():
    global baseurl, core_admin_url, threshold_warn, threshold_crit

    cmd_parser = OptionParser(version="%prog 0.1")
    cmd_parser.add_option("-H", "--host", type="string", action="store", dest="solr_server", default="localhost", help="SOLR Server address")
    cmd_parser.add_option("-p", "--port", type="string", action="store", dest="solr_server_port", help="SOLR Server port")
    cmd_parser.add_option("-W", "--webapp", type="string", action="store", dest="solr_server_webapp", help="SOLR Server webapp path")
    cmd_parser.add_option("-P", "--ping", action="store_true", dest="check_ping", help="SOLR Ping", default=False)
    cmd_parser.add_option("-r", "--replication", action="store_true", dest="check_replication", help="SOLR Replication check", default=False)
    cmd_parser.add_option("-w", "--warn", type="int", action="store", dest="threshold_warn", help="WARN threshold for replication check", default=1)
    cmd_parser.add_option("-c", "--critical", type="int", action="store", dest="threshold_crit", help="CRIT threshold for replication check", default=2)
    cmd_parser.add_option("-i", "--ignore", type="string", action="append", dest="ignore_cores", help="SOLR Cores to ignore", default=[])

    (cmd_options, cmd_args) = cmd_parser.parse_args()

    if not (cmd_options.solr_server and cmd_options.solr_server_port and cmd_options.solr_server_webapp):
        cmd_parser.print_help()
        return(3)

    if not cmd_options.check_replication and not cmd_options.check_ping:
        print "ERROR: Please specify -r or -P"
        return(3)

    if ((cmd_options.threshold_warn and not cmd_options.threshold_crit) or (cmd_options.threshold_crit and not cmd_options.threshold_warn)):
        print "ERROR: Please use -w and -c together."
        return(3)

    if cmd_options.threshold_crit <= cmd_options.threshold_warn:
        print "ERROR: the value for (-c|--critical) must be greater than (-w|--warn)"
        return(3)

    solr_server         = cmd_options.solr_server
    solr_server_port    = cmd_options.solr_server_port
    solr_server_webapp  = cmd_options.solr_server_webapp
    check_ping          = cmd_options.check_ping
    check_replication   = cmd_options.check_replication
    threshold_warn      = cmd_options.threshold_warn
    threshold_crit      = cmd_options.threshold_crit
    ignore_cores        = set(cmd_options.ignore_cores)

    core_admin_url      = 'admin/cores?'
    baseurl             = 'http://' + solr_server + ':' + solr_server_port + '/' +  solr_server_webapp + '/'

    repwarn             = set()
    repcrit             = set()

    pingerrors          = set()

    try:
        all_cores = listcores()
    except IOError as (errno, strerror):
        print "CRITICAL: {0} - {1}".format(errno,strerror)
        return(2)
    except (ValueError, TypeError):
        print "CRITICAL: probably couldn't format JSON data, check SOLR is ok"
        return(3)
    except:
        print "CRITICAL: Unknown error"
        return(3)

    cores = all_cores - ignore_cores

    # XXX: This is ugly...
    try:
        for core in cores:
            if check_replication:
                ret = repstatus(core)
                if ret == 'CRITICAL':
                    repcrit.add(core)
                elif ret == 'WARNING':
                    repwarn.add(core)
            if check_ping:
                if solrping(core) != 'OK':
                    pingerrors.add(core)
    except IOError as (errno, strerror):
        print "CRITICAL: {0} {1} ".format(errno, strerror)
        return(2)
    except KeyError as strerror:
        if 'slave' in strerror:
            print "CRITCAL: This doesn't seem to be a slave, are you sure you meant to call -r?"
            return(2)
        else:
            print "CRITICAL: unknown error (error string: {0})".format(strerror)
            print strerror
            return(3)

    if pingerrors:
        print "CRITICAL: Error pinging cores(s) - {0}. Tested core(s) - {1} |TotalOKCores={2}".format(", ".join(pingerrors), ", ".join(cores), len(cores-pingerrors))
        return(2)
    elif repcrit:
        print "CRITICAL: Replication errors on cores(s) - {0}. Tested core(s) - {1} |TotalOKCores={2}".format(", ".join(repcrit), ", ".join(cores), len(cores-repcrit))
        return(2)
    elif repwarn:
        print "WARNING: Replication errors on cores(s) - {0}. Tested core(s) - {1} |TotalOKCores={2}".format(", ".join(repwarn), ", ".join(cores), len(cores-repwarn))
        return(1)
    else:
        print "OK. Tested core(s) - {0} |TotalOKCores={1}".format(", ".join(cores), len(cores))
        return(0)

if __name__ == '__main__':
    sys.exit(main())

