#!/usr/bin/env python
import os
import shutil

if __name__ == '__main__':
    backupBase = '/home/okfn/backup'
    if os.path.exists(backupBase):
    	shutil.rmtree(backupBase)
    os.makedirs(backupBase)
    
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
    cmd3 = 'kforge-admin --env %s backup %s' % (src, dest)
    if os.system(cmd3):
        print 'Error on command %s' % cmd3
    
    # TODO: backup publicgeodata stuff
