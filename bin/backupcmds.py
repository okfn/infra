import os.path
import shutil
import sys

# ---------------------------------------------------------
# Helper Methods

def run(cmd):
    if os.system(cmd):
        print 'Error executing command: %s' % cmd

def pgdump(db_name, dump_path): 
    cmd = 'sudo -u postgres pg_dump --user postgres --inserts ' + db_name
    cmd += ' | gzip > %s' % dump_path
    run(cmd)

def mysqldump(db_name, dump_path):
    mysqlcmd = 'mysqldump %s -c | gzip > %s' % (db_name, dump_path)
    run(mysqlcmd)

def svndump(repo_path, dump_path):
    '''Dump svn repository.

    Use dump rather than hotcopy as portable across versions.

    # TODO: do we need to hotcopy and then dump
    '''
    cmd = 'svnadmin --quiet dump %s | gzip > %s' % (repo_path, dump_path)
    run(cmd)

def clean_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

# ---------------------------------------------------------
# Per Host Stuff

def backup_etc_repo(base):
    # TODO: give this a machine specific name
    dest = os.path.join(base, 'repo_sysadmin.gz')
    repo = '/root/repo_sysadmin'
    svndump(repo,dest)

# ---------------------------------------------------------
# General Sysadmin

def backup_mailman(base):
    dest = os.path.join(base, 'mailman.tgz')
    cmd = 'tar -czf %s %s' % (dest, '/var/lib/mailman/data /var/lib/mailman/archives')
    run(cmd)

# ---------------------------------------------------------
# CKAN

def backup_ckan(base):
    path = os.path.join(base, 'ckan.sql.gz')
    pgdump('ckan', path)
    cfg = '/home/rgrp/svn-ckan/ckan/trunk/www.ckan.net.ini'
    shutil.copy(cfg, base)

# ---------------------------------------------------------
# OKFN Core

def okfn_blog_db(base):
    blogDbBackupPath = os.path.join(base, 'blog.okfn.org.sql.gz')
    mysqldump('okfn_blog_wp', blogDbBackupPath)

def okfn_drn(base):
    drnDbBackupPath = os.path.join(base, 'drn.okfn.org.sql.gz')
    mysqldump('okfn_drn_drupal', drnDbBackupPath)
   
def okfn_wikis(base):
    wikiPath = '/home/okfn/var/moin'
    backupPath = os.path.join(base, 'moin.tgz')
    cmd = 'tar -czf %s %s' % (backupPath, wikiPath)
    if os.system(cmd):
    	print 'Error executing command: %s' % cmd

def okfn_www(base):
    wwwPath = '/home/okfn/var/www'
    backupPath = os.path.join(base, 'www.tgz')
    cmd = 'tar -czf %s %s' % (backupPath, wwwPath)
    if os.system(cmd):
    	print 'Error executing command: %s' % cmd

def okfn_svn(base):
    # TODO
    pass

# TODO: sysadmin trac stuff
