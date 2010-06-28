'''A fabric fabfile. See available commands do::

    fab -l

You can specify host and username using --hosts and --user options

TODO: 2010-05-06 start writing tests.
'''
from __future__ import with_statement
import os
import datetime
import urllib2
try:
    import json
except ImportError:
    import simplejson as json

from fabric.api import *
from fabric.contrib.console import *
from fabric.contrib.files import *

## ==============================
## Helper methods/classes

# work whether on windows or linux
def _join(*paths):
    # TODO: ? rstrip '/' from paths?
    return '/'.join(paths)

def _run(*args, **kwargs):
    if hasattr(env, 'use_sudo') and env.use_sudo:
        sudo(*args, **kwargs)
    else:
        run(*args, **kwargs)

class _SSH(object):
    @classmethod
    def ssh_dir(self, user):
        if user == 'root':
            userdir = '/root'
        else:
            userdir = '/home/%s' % user
        return _join(userdir, '.ssh')
        return userdir

    @classmethod
    def authorized_keys_path(self, user):
        return _join(self.ssh_dir(user), 'authorized_keys')


## ==============================
## Fabric commands


def adduser(username='okfn'):
    '''Create a user with username `username` (defaults to okfn).
    '''
    assert not exists('/home/%s' % username), '%s user already exists' % username
    # use useradd rather than adduser so as to not be prompted for info
    run('useradd --create-home %s' % username)

def ssh_add_public_key_from_config(key_config, user, dest_user):
    '''Add public key from a config file to `dest_user` on remote host.

    :param key_config: json file giving key config
    :param user: user to add from config file.
    :param dest_user: user on dest host to add public key to.
    '''
    info = json.load(open(key_config))
    key = info['users'][user]['key']
    _ssh_add_public_key(key, dest_user)

def ssh_add_to_authorized_keys(authorized_keys_file, dest_user='root'):
    '''Add ssh keys provided in `authorized_keys_file` for user `dest_user`.
    
    NB: assumes root access (TODO: change this)

    :param  authorized_keys: list of authorized keys (in correct format) to
        add.
    '''
    data = open(authorized_keys_file).read()
    _ssh_add_public_key(data, dest_user)

def _ssh_add_public_key(public_key, dest_user):
    '''Add `key`(s) string to authorized_keys file for `dest_user`.'''
    # unbelievably fabric will interpret unicode string as a list leading to
    # very weird results on e.g. appending (since it does not append if string
    # already in file)
    public_key = str(public_key)
    authorized_keys_path = _SSH.authorized_keys_path(dest_user)
    if dest_user == 'root':
        append(public_key, authorized_keys_path)
    else:
        userdir = '/home/%s' % dest_user
        assert exists(userdir), 'No home directory for user: %s' % dest_user
        sshdir = userdir + '/.ssh'
        if not exists(sshdir):
            run('mkdir %s' % sshdir)
        append(public_key, authorized_keys_path)
        run('chown -R %s:%s %s' % (dest_user, dest_user, sshdir))
        run('chmod go-rwx -R %s' % sshdir)

def ssh_add_private_key(key_path, user='root'):
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
    # avoid using sudo when root (so we can e.g. install sudo package!)
    if not env.user == 'root':
        env.use_sudo = True
    if update_first:
        _run('apt-get update')
    for pkgname in package_sets[package_set]:
        if '::' not in pkgname: # default
            _run('apt-get -y install %s' % pkgname)
        elif pkgname.startswith('set::'):
            setname = pkgname.split('::')[1]
            install(package_set=setname)
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
    install('mercurial')
    append(etc_hgignore, '/etc/.hgignore', use_sudo=True)
    with cd('/etc/'):
        sudo('hg init')
        sudo('hg add')
        sudo('hg commit --user "okfn sysadmin" -m "[all][l]: import existing /etc contents into hg"')


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
## Databases

def mysql_create(dbname, username, password):
    '''Create mysql database (DOES NOT SEEM TO WORK).

    :param dbname:
    :param username:
    :param password:
    '''
    sql = '''CREATE DATABASE %(db)s; GRANT ALL PRIVILEGES ON %(db)s.* TO "%(user)s"@"localhost" IDENTIFIED BY "%(password)s"; FLUSH PRIVILEGES;'''
    sql = sql % { 'db': dbname.replace('.','_'), 'user': username, 'password': password }
    cmd = "mysql -p --execute '%s'" % sql
    sudo(cmd)


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
        if not exists(path + '/index.php'):
            cmd = 'svn co http://core.svn.wordpress.org/tags/%s .' % version
            run(cmd)
    print 'You may wish to now set up a database using the mysql_create command'


## ============================
## Backup


def backup_setup():
    '''Set up backup for host specified by --host.'''
    scripts_dest = '/etc/backup/backup.d'
    config_dest = '/etc/backup/backuprc'
    # standard locations -- you can configure as you want ...
    config = {
        'mount_device' : '/dev/sdp',
        'snapshot_rw' : '/mnt/backup',
        'snapshot_ro' : '/mnt/backup_ro'
        }
    if exists(config_dest):
        print 'Config already exists at: %s' % config_dest
        print 'Overwriting!'
    sudo('mkdir -p %s' % scripts_dest)
    # ../etc/backup
    local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
            'etc', 'backup')
    for fn in os.listdir(local_path):
        fp = os.path.join(local_path, fn)
        print fp
        if os.path.isdir(fp):
            put(os.path.join(fp, '*'), '/etc/backup/%s' % fn)
        else:
            put(os.path.join(fp), '/etc/backup/')
    cron_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
        'cron', 'backuprotatingsnapshot')
    put(cron_file, '/etc/cron.daily/')
    if not exists(config['snapshot_rw']):
        sudo('mkdir -p %s' % config['snapshot_rw'])
    if not exists(config['snapshot_ro']):
        sudo('mkdir -p %s' % config['snapshot_ro'])
    print 'You may now wish to run backup_report to check backup mount device exists and can be mounted'


def backup_report():
    '''Provide a backup report for host specified by --host.'''
    config_dest = '/etc/backup/backuprc'
    backup_device = run('. %s && echo $MOUNT_DEVICE' % config_dest)
    snapshot_ro = run('. %s && echo $SNAPSHOT_RO' % config_dest)
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

