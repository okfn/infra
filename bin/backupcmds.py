import os.path
import shutil
import sys

def run(cmd):
    if os.system(cmd):
        print 'Error executing command: %s' % cmd

def pgdump(db_name, dump_path): 
    cmd = 'sudo -u postgres pg_dump --user postgres --inserts ' + db_name
    cmd += ' | gzip > %s' % dump_path
    run(cmd)

def backup_etc_repo(base):
    dest = os.path.join(base, 'repo_sysadmin.gz')
    cmd = 'svnadmin -q dump /root/repo_sysadmin | gzip > ' + dest
    run(cmd)

def backup_mailman(base):
    dest = os.path.join(base, 'mailman.tgz')
    cmd = 'tar -czf %s %s' % (dest, '/var/lib/mailman/data /var/lib/mailman/archives')
    run(cmd)

def backup_ckan(base):
    path = os.path.join(base, 'ckan.sql.gz')
    pgdump('ckan', path)
    cfg = '/home/rgrp/svn-ckan/ckan/trunk/www.ckan.net.ini'
    shutil.copy(cfg, base)

