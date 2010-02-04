'''usage:
    fab -f aws_fabfile.py

You can specify host and username using --hosts and --user options
'''
from __future__ import with_statement
import os
import datetime
import urllib2

from fabric.api import *
from fabric.contrib.console import *
from fabric.contrib.files import *

def move_directories_to_mnt():
    '''Move /var, /home to /mnt/root/XXX and fstab them in.
    
    NB: if you already have a service such as mysql of postgresql running
    you'll need to stop it.

    See http://developer.amazonwebservices.com/connect/entry.jspa?externalID=1663&categoryID=100
    '''
    assert not exists('/mnt/root'), '/mnt/root already exists!'
    sudo('mkdir /mnt/root')
    dirs = [ 'var', 'home' ]
    for dir in dirs:
        # avoid possible problem with being in dir that is being moved
        with cd('/'):
            sudo('mv /%s /mnt/root' % dir)
            sudo('mkdir /%s' % dir)
            append('/mnt/root/%s /%s     none bind' % (dir, dir), '/etc/fstab', use_sudo=True)
            sudo('mount /%s' % dir)


package_sets = {
    # TODO visudo and add relevant users to sudo list
    'basics': [
        'vim-nox',
        'sudo',
    ],
    'web': [
        'apache2',
        'libapache2-mod-wsgi'
    ],
    'ckan': [
        'postgresql'
    ],
    'python_basics': [
        'python-setuptools'
        # probably not recent enough
        # in which case do: e.g. easy_install --always-unzip setuptools
        'python-virtualenv'
        # pip as well but not in debian
        # easy_install --always-unzip pip
    ],
    # unlikely to need this on the *remote* host
    'fabric': [
        'python-paramiko'
        # no fabric in debian lenny
    ]
}

def install_packages(package_set='basics', update_first=False):
    '''Install packages onto host.
    
    Should try to login as root for this as may not have sudo
installed yet.

    Primarily system packages provided by apt.
    '''
    if update_first:
        run('apt-get update')
    for pkgname in package_sets[package_set]:
        run('apt-get -y install %s' % pkgname)

