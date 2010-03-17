'''A fabric fabfile. See available commands do::

    fab -l

You can specify host and username using --hosts and --user options
'''
from __future__ import with_statement
import os
import datetime
import urllib2

from fabric.api import *
from fabric.contrib.console import *
from fabric.contrib.files import *


def fix_profile():
    '''(NOT WORKING) Fix up root profile on ec2 (o/w complaints about: err: stdin: is
    not a tty).
    '''
    text = '''if `tty -s`; then
    mesg n
fi
'''
    fn = '/root/.profile'
    comment(fn, '^mesg n', backup='')
    append(fn, text)


def move_directories_to_mnt():
    '''Move /var, /home to /mnt/root/XXX and fstab them in.

    NB: assume we run as root.
    
    NB: if you already have a service such as mysql of postgresql running
    you'll need to stop it.

    Inspired by http://developer.amazonwebservices.com/connect/entry.jspa?externalID=1663
    '''
    assert not exists('/mnt/root'), '/mnt/root already exists!'
    run('mkdir /mnt/root')
    dirs = [ 'var', 'home' ]
    for dir in dirs:
        # avoid possible problem with being in dir that is being moved
        with cd('/'):
            run('mv /%s /mnt/root' % dir)
            run('mkdir /%s' % dir)
            append('/mnt/root/%s /%s     none bind' % (dir, dir), '/etc/fstab',
                    use_sudo=False)
            run('mount /%s' % dir)


def adduser_okfn():
    '''Create the okfn users.'''
    assert not exists('/home/okfn'), 'okfn user already exists'
    # use useradd rather than adduser so as to not be prompted for info
    run('useradd --create-home okfn')


def add_ssh_keys(authorized_keys_file, user='root'):
    '''Add ssh keys provided in `authorized_keys_file` for user `user`.
    
    NB: assumes root access (TODO: change this)
    '''
    data = open(authorized_keys_file).read()
    if user == 'root':
        append(data, '/root/.ssh/authorized_keys')
    else:
        userdir = '/home/%s' % user
        assert exists(userdir), 'No home directory for user: %s' % user
        sshdir = userdir + '/.ssh'
        if not exists(sshdir):
            run('mkdir %s' % sshdir)
        append(data, '%s/authorized_keys' % sshdir)
        run('chown -R %s:%s %s' % (user, user, sshdir))
        run('chmod go-rwx -R %s' % sshdir)


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
        'postgresql',
        'python-psycopg2',
        'set::web',
    ],
    'python_basics': [
        'python',
        # may be recent enough
        # in which case do: e.g. easy_install --always-unzip setuptools
        'python-setuptools',
        # not recent enough
        # 'python-virtualenv'
        'cmd::easy_install --always-unzip virtualenv',
        # pip not yet in debian
        # 'python-pip'
        'cmd::easy_install --always-unzip pip',
    ],
    # unlikely to need this on the *remote* host
    'fabric': [
        'python-paramiko'
        # no fabric in debian lenny
    ],
    'kforge': [
        'python-dev',
        'build-essential',
        # django apparently needs this!
        'apache2-mpm-prefork',
        'libapache2-mod-python',
        # unnecessary dependency on mx datetime so install from source
        # 'python-psycopg2',
        'postgresql',
        'exim4'
        ],
    'kforge-plugins': [
        'python-moinmoin',
        'subversion',
        'libapache2-svn',
    ],
    'isitopen': [
        'postgresql',
        'python-psycopg2',
        'mercurial',
        'set::python-installers'
        ],
    'mercurial': [
        'mercurial'
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
        if '::' not in pkgname: # default
            run('apt-get -y install %s' % pkgname)
        elif pkgname.startswith('set::'):
            setname = pkgname.split('::')[1]
            install_packages(package_set=setname)
        elif pkgname.startswith('cmd::'):
            cmd = pkgname.split('::')[1]
            run(cmd)
        else:
            print 'Unrecognized package format'



def setup_sudoers():
    '''Add standard okfn as admin config to sudoers'''
    fn = '/etc/sudoers'
    # double escape as passed through to sed ...
    after = '# User alias specification\\nUser_Alias      ADMINS = okfn'
    sed(fn, '# User alias specification', after)

    in2 = r'root.*ALL=\(ALL\) ALL'
    # double escape as passed through to sed ...
    out2 = 'root   ALL=(ALL) ALL' + '\\n' + 'ADMINS  ALL = (ALL) NOPASSWD: ALL'
    print out2
    sed(fn, in2, out2, backup='')


def etc_in_mercurial():
    '''Start versioning /etc in mercurial.'''
    etc_hgignore = '''syntax: glob
*.lock*
ld.so.cache
links.cfg
adjtime
udev
ppp
localtime
ssl/private/ssl-cert-snakeoil.key
ssl/certs
*.swp
*.dpkg-old
*.old

syntax: regexp
.*~$
'''
    install_packages('mercurial')
    append(etc_hgignore, '/etc/.hgignore')
    with cd('/etc/'):
        run('hg init')
        run('hg add')
        run('hg commit --user "okfn sysadmin" -m "[all][l]: import existing /etc contents into hg"')

