#!/usr/bin/env python
import os
import shutil

if __name__ == '__main__':
    backupBase = '/home/okfn/backup'
    if os.path.exists(backupBase):
    	shutil.rmtree(backupBase)
    os.makedirs(backupBase)
    
    blogDbBackupPath = os.path.join(backupBase, 'blog.okfn.org.sql.gz')
    mysqlcmd = 'mysqldump okfn_blog_wp -c | gzip > %s' % blogDbBackupPath
    if os.system(mysqlcmd):
        print 'Error on command %s' % mysqlcmd
    
    drnDbBackupPath = os.path.join(backupBase, 'drn.okfn.org.sql.gz')
    mysqlcmd = 'mysqldump okfn_drn_drupal -c | gzip > %s' % drnDbBackupPath
    if os.system(mysqlcmd):
        print 'Error on command %s' % mysqlcmd
    
    wikiPath = '/home/okfn/var/moin'
    backupPath = os.path.join(backupBase, 'moin.tgz')
    cmd = 'tar -czf %s %s' % (backupPath, wikiPath)
    if os.system(cmd):
    	print 'Error executing command: %s' % cmd
   
    wwwPath = '/home/okfn/var/www'
    backupPath = os.path.join(backupBase, 'www.tgz')
    cmd = 'tar -czf %s %s' % (backupPath, wwwPath)
    if os.system(cmd):
    	print 'Error executing command: %s' % cmd

    src = '/home/okfn/kforge'
    dest = '/home/okfn/backup/kforge'
    config = os.path.join(src, 'kforge.conf')
    cmd3 = 'kforge-admin --config %s backup %s' % (config, dest)
    if os.system(cmd3):
        print 'Error on command %s' % cmd3
    
    # TODO: backup publicgeodata stuff
