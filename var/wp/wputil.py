#!/usr/bin/env python
'''Set up wp sites in standard fashion.

  %prog [options] create {path}

Notes:

  1. To facilitate easy upgrading of wordpress (and finding out what gets
     changed) we install WP from subversion following:

     <http://codex.wordpress.org/Installing/Updating_WordPress_with_Subversion>
'''
import os
import optparse
import sys

WP_SVN_URL = 'http://svn.automattic.com/wordpress/tags/'

def wp_svn_url(version):
    return WP_SVN_URL + version

def create(path, wp_version):
    if os.path.exists(path):
        print 'Path already exists: %s' % path
        return
    else:
        print 'Creating directory: %s' % path
        os.makedirs(path)
    curdir = os.getcwd()
    os.chdir(path)
    svn_url = wp_svn_url(wp_version)
    cmd = 'svn checkout %s .' % svn_url
    # print 'Checking out to: %s' % path
    print cmd
    os.system(cmd)
    os.chdir(curdir)

import shutil
def test_create():
    path = 'testwputil'
    if os.path.exists(path):
        shutil.rmtree(path)
    # use and old version to cut down on checkout needed
    create(path, '2.0')
    assert os.path.exists(os.path.join(path, 'wp-admin'))

if __name__ == '__main__':
    parser = optparse.OptionParser(usage=__doc__)
    options, args = parser.parse_args()
    def error():
        print '~#~ Error! Please supply sufficient arguments\n'
        parser.print_help()
        sys.exit(1)
    if len(args) < 2:
        error()
    action = args[0]
    path = os.path.abspath(args[1])
    if action == 'create':
        create(path, '2.7')
    else:
        error()


