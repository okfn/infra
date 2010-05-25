'''A fabric fabfile. See available commands do::

    fab -l

You can specify host and username using --hosts and --user options

TODO: 2010-05-06 start writing tests.
'''
from __future__ import with_statement
import os
import datetime
import urllib2

from fabric.api import *
from fabric.contrib.console import *
from fabric.contrib.files import *

## ==============================
## Helper methods/classes

# work whether on windows or linux
def _join(*paths):
    '/'.join(paths)

def _run(*args, **kwargs):
    if env.use_sudo:
        sudo(*args, **kwargs)
    else:
        run(*args, **kwargs)


class _SSH(object):
    @classmethod
    def ssh_dir(self, user):
        if user == 'root':
            userdir = '/root/.ssh'
        else:
            userdir = '/home/%s' % user
        return userdir

    @classmethod
    def authorized_keys_path(self, user):
        return _join(self.ssh_dir, 'authorized_keys')


## ==============================
## Fabric commands


def adduser(username='okfn'):
    '''Create a user with username `username` (defaults to okfn).
    '''
    assert not exists('/home/%s' % username), '%s user already exists' % username
    # use useradd rather than adduser so as to not be prompted for info
    run('useradd --create-home %s' % username)

def ssh_add_to_authorized_keys(authorized_keys_file, user='root'):
    '''Add ssh keys provided in `authorized_keys_file` for user `user`.
    
    NB: assumes root access (TODO: change this)
    '''
    data = open(authorized_keys_file).read()
    authorized_keys = _SSH.authorized_keys_path(user)
    if user == 'root':
        append(data, authorized_keys)
    else:
        userdir = '/home/%s' % user
        assert exists(userdir), 'No home directory for user: %s' % user
        sshdir = userdir + '/.ssh'
        if not exists(sshdir):
            run('mkdir %s' % sshdir)
        append(data, authorized_keys)
        run('chown -R %s:%s %s' % (user, user, sshdir))
        run('chmod go-rwx -R %s' % sshdir)

def ssh_add_key(key_path, user='root'):
    '''Add private key at `key_path` for `user`.

    @param key_path: path to key
    @parm user: (default: root) user to add key for.
    '''
    key_name = os.path.basename(key_path)
    dest = _join(_SSH.ssh_dir(user), key_name)
    put(key_path, dest)


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
        ],
    'supervisor': [
        'cmd::easy_install --always-unzip supervisor'
        ],
}

import pprint
def install(package_set='basics', update_first=False):
    '''Install package set onto host.
    
    Should try to login as root for this as may not have sudo
installed yet.

    Primarily system packages provided by apt.

    :param package: string specifying package set (list of package sets given
        below).
    :param update_first: run apt-get update first.

    Package Sets
    ============
    
    %s
    '''
    if update_first:
        _run('apt-get update')
    for pkgname in package_sets[package_set]:
        if '::' not in pkgname: # default
            _run('apt-get -y install %s' % pkgname)
        elif pkgname.startswith('set::'):
            setname = pkgname.split('::')[1]
            install_packages(package_set=setname)
        elif pkgname.startswith('cmd::'):
            cmd = pkgname.split('::')[1]
            _run(cmd)
        else:
            print 'Unrecognized package format'
install.__doc__ = install.__doc__ % pprint.pformat(package_sets)


def install_supervisor():
    '''Install supervisor(d) including /etc/init.d and standard /etc script.

    NB: supervisor is a proper package in debian squeeze and ubuntu lucid
    onwards
    '''
    install('supervisor')
    _initd = 'http://svn.supervisord.org/initscripts/debian-norrgard'
    get(initd, '/etc/init.d/supervisord')


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


import tempfile
def _setup_rsync(key_name, remote_dir, local_dir):
    '''

    1. Set up a new key pair just for this rsync (or use existing if already
        there ...)
    2. Install key pair on relevant machines
    3. Install rsync command into relevant cron ...
    '''
    tmpdir = tempfile.gettempdir()
    privatekey = os.path.join(tmpdir, key_name)
    # TODO: customize pub key to restrict usage
    # see http://www.eng.cam.ac.uk/help/jpmg/ssh/authorized_keys_howto.html 
    # see http://www.nardol.org/2009/4/15/rsync-logs-with-restricted-ssh 
    commandtorun = 'rsync -avz ...'
    pubkey = privatekey + '.pub'
    # -N '' = no passphrase
    cmd = 'ssh-keygen -N "" -f %s' % privatekey
    local(cmd)
    ssh_add_authorized
    # set host and user ...
    # env.host = 
    ssh_add_key(privatekey)
    ssh_add_to_authorized_keys(pubkey, user)


## ============================
## Wordpress

def wordpress_install(path, version='2.9.2'):
    '''Install wordpress at `path` using svn method.
    
    http://codex.wordpress.org/Installing/Updating_WordPress_with_Subversion

    @param path: path to install to (created if not already existent)
    @param version: (defaults to 2.9.2) version of worpdress to use.
    '''
    if not exists(path):
        run('mkdir %s' % path)
    with cd(path):
        cmd = 'svn co http://core.svn.wordpress.org/tags/%s .' % version
        run(cmd)


## ============================
## Backup

def _setup_backup():
    '''Set up backup for host specified by --host.'''
    # standard locations -- you can configure as you want ...
    backup_device = '/dev/sdp'
    snapshot_rw = '/mnt/backup'
    snapshot_ro = snapshot_rw + '_ro'

def backup_report():
    '''Provide a backup report for host specified by --host.'''
    backup_device = run('. /etc/backup_config && echo $MOUNT_DEVICE')
    snapshot_ro = run('. /etc/backup_config && echo $SNAPSHOT_RO')
    hostname = run('hostname -s')
    assert backup_device != ''
    assert snapshot_ro != ''
        
    print 'backup device on %s is %s' % (env['host'], backup_device)
    print 'checking for device node and mount point...'
    run('ls %(backup_device)s' % locals())
    run('ls %(snapshot_ro)s' % locals())
    
    print 'getting times of latest backups'
    try:
        sudo('mount -r %(backup_device)s %(snapshot_ro)s' % locals())
        backups = sudo('ls -l %(snapshot_ro)s/%(hostname)s' % locals())
        print 'backups...'
        dates = [x.split()[5] for x in backups.split('\n')[1:]]
        dates = map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"), dates)
        deltas = map(lambda x: datetime.datetime.now() - x, dates)
        min_delta = min(deltas)
        print 'last backup occured %(min_delta)s ago' % locals() 
        if min_delta > datetime.timedelta(days=1):
            print 'WARNING no backup in 24 hours on', env['host']
        else: 
            print 'backups look good'
    finally: 
        sudo('umount %(snapshot_ro)s' % locals())

