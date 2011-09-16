'''A fabric fabfile. See available commands do::

    fab -l

You can specify host and username using --hosts and --user options

TODO: 
 * [2010-05-06] start writing tests.
 * make all commands idempotent so they can be run twice without doing any damage
 * get rid of errors 'stdin: is not a tty' and '/root/.bash_profile: Permission denied'
 * Change layout of mount points for instance-store based EC2 instances
 * instance_setup():
  * Also lock account 'ubuntu'
  * add munin_node_install()
  * add backup_setup()
 * Create new funtions and add them to instance_setup():
  * install and setup postfix
  * set root mail alias & send testmail
  * add customizations specific to managed rackspace servers (fail2ban, ssh password exceptions)
  * install OpenPortChecker
  * configure firewall?
  * cutomize .bashrc? 
  * add new server to nagios?

'''
from __future__ import with_statement
import os
import pprint
import datetime
import urllib2
try:
    import json
except ImportError:
    import simplejson as json

from fabric.api import *
from fabric.contrib.console import *
from fabric.contrib.files import *

#import server_roles
#
#env.roledefs = server_roles.get_roles()


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

def _sudo(*args, **kwargs):
    if env.user == 'root':
        run(*args, **kwargs)
    else:
        sudo(*args, **kwargs)

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

def _get_unique_filepath(dir_, filename):
    '''Create (what should be) a unique filepath in `dir_` by appending to `filename` a timestamp (including microseconds).
    
    :param dir_: dir_ in which to create the filename.
    :param filename: base filename to use in dir_.
    '''
    date = datetime.datetime.today().strftime('%Y-%m-%dT%H%M.%f')
    filepath = os.path.join(dir_, filename + '.' + date)
    return filepath

def _mkdir(dir):
    '''Create a directory if it does not already exist.'''
    if not exists(dir):
        run('mkdir -p %s' % dir)
    else:
        print 'Path already exists: %s' % dir

## ++++++++++++++++++++++++++++
## Fabric commands

## ============================
## Setup instances

def instance_setup_old(okfn_id):
    '''Obsoleted. Setup a new instance named by `okfn_id` the (old) standard way.

        * hostname
        * adduser
        * setup_sudoers
        * ssh_add_public_key_group - sysadmin
        * etc_in_mercurial
        * sysadmin_repo_clone
    '''
    set_hostname(okfn_id)
    adduser('okfn')
    setup_sudoers()
    ssh_add_public_key_group('../ssh_keys.js', 'sysadmin', 'okfn')
    etc_in_mercurial()
    sysadmin_repo_clone()
    

def instance_setup(hostname='', harden=False, team='okfn', flavour='AUTODETECT', keyfile='../ssh_keys.js'):
    '''Setup a new instance a in standard way:

        * Generate (UK) locales
        * set_hostname (if hostname is set)
        * install_set - vim, sudo, upgrade 
        * etc_in_mercurial
        * default_shell_bash
        * prepare_sudoers
        * add_team - okfn
        * lock_user - root (if harden==True)
        * harden_sshd (if harden==True)
        * sysadmin_repo_clone
     '''

    root_alias = _get_default_root_alias()
    additional_firewall_rules = []

    if flavour == 'AUTODETECT':
        flavour = detect_flavour()
        
    if flavour == 'Fry':
        harden = False
        root_alias += ',system-reports@fry-it.com'

    generate_locale() 
    if hostname :
        set_hostname(hostname)
    upgrade()
    install_set('basics')
    etc_in_mercurial()
    default_shell_bash()
    prepare_sudoers()
    add_team(team, key_config = keyfile)
    set_root_alias(root_alias)
    if harden :
        lock_user(username='root')
        harden_sshd()
    sysadmin_repo_clone()

    if flavour == 'Fry':
        # fix_fry_postfix()
        additional_firewall_rules = [
            '-A INPUT -j ACCEPT -p tcp  -s monitor1.fry-it.com  # Allow Fry monitors',
            '-A INPUT -j ACCEPT -p tcp  -s monitor2.fry-it.com'
        ]
        install_firewall(rules=additional_firewall_rules)


def info():
    '''Tries to log into other host and display hostname, username, and whether sudo works.
    '''
    run('hostname')
    run('id')
    sudo('id')


def detect_flavour():
    '''Logs into host and tries to determine it's flavour (e.g. "Fry")
    '''

    flavour = None
    if contains('^ *nameserver  *193.34.146.1 *$', '/etc/resolv.conf', exact=False, use_sudo=False) :
        flavour = 'Fry'

    if flavour:
        print 'Auto-detected flavour "%s".' % flavour
    else:
        print 'No flavour auto-detected.'

    return flavour


## ============================
## User and sudo

def default_shell_bash():
    '''Set the default shell for new users to bash.
    '''
    assert exists('/bin/bash'), '/bin/bash not found'
    _sudo('useradd -D --shell /bin/bash')


def adduser(username='okfn', bash=True):
    '''Create a user with username `username` (defaults to okfn).
    '''
    assert not exists('/home/%s' % username), '%s user already exists' % username
    # use useradd rather than adduser so as to not be prompted for info
    _sudo('useradd --create-home %s' % username)
    _sudo('echo "%s:`tr -dc _A-Z-a-z-0-9 < /dev/urandom | head -c20`" | chpasswd' % username)
    if bash:
        user_shell_bash(username=username)


def user_shell_bash(username='okfn'):
    '''Set the shell of user `username` to /bin/bash (defaults to okfn).
    '''
    assert exists('/home/%s' % username), '%s user does not exist' % username
    assert exists('/bin/bash'), '/bin/bash not found'
    _sudo('usermod --shell /bin/bash %s' % username)


def prepare_sudoers():
    '''Add group 'ADMINS' to /etc/sudoers'''
    fn = '/etc/sudoers'

    if contains('User_Alias *ADMINS *=', fn, use_sudo=True):
        print 'User_Alias ADMINS already in %s' % fn
    else:
        print 'Adding "User_Alias ADMINS" to %s' % fn 
        # double escape as passed through to sed ...
        after = '# User alias specification\\nUser_Alias      ADMINS = root'
        sed(fn, '# User alias specification', after, use_sudo=True)

    if contains('^ADMINS *ALL *=', fn, use_sudo=True):
        print 'AMINDS rule already in %s' % fn
    else:
        print 'Adding AMINDS rule to %s' % fn
        in2 = r'root.*ALL=\(ALL\) ALL'
        # double escape as passed through to sed ...
        out2 = 'root   ALL=(ALL) ALL' + '\\n' + 'ADMINS  ALL = (ALL) NOPASSWD: ALL'
        sed(fn, in2, out2, backup='', use_sudo=True)


def adduser_to_sudo_admins(username):
    '''Add a user as admin to /etc/sudoers'''
    # TODO: check whether user is already listed
    fn = '/etc/sudoers'
    prepare_sudoers()
    sed(fn, '^(User_Alias *ADMINS *=.*)', '\\1, %s' % username, use_sudo=True)


def setup_sudoers():
    '''Only for backwards compatibility - Prepare /etc/sudoers and add standard user 'okfn' as admin config to sudoers'''
    adduser_to_sudo_admins('okfn')


def add_team(team, key_config = '../ssh_keys.js'):
    key_group = team
    if team == 'okfn': key_group = 'sysadmin'
    adduser(team)
    #user_shell_bash(team)
    adduser_to_sudo_admins(team)
    ssh_add_public_key_group(key_config, key_group, team)


def lock_user(username='root'):
    '''Lock password of user `username` (defaults to root).
    '''
    _sudo('passwd --lock %s' % username)


## ============================
## Miscellaneous sysadmin setup

def set_hostname(new_hostname):
    _sudo('hostname %s' % new_hostname)
    _sudo('echo %s > /etc/hostname' % new_hostname)
    _sudo('echo %s > /etc/mailname' % new_hostname)
    sed('/etc/hosts', '^(127\.0\.0\.1 .*)', '\\1 %s' % new_hostname, use_sudo=True)
    _sudo('sudo restart rsyslog')



SYSADMIN_REPO_PATH = '/home/okfn/hg-sysadmin'
OKFN_ETC = '/home/okfn/etc'
def sysadmin_repo_clone():
    '''Clone okfn sysadmin repo onto machine and symlink to /home/okfn/etc'''
    # adduser(okfn)
    # install_set('mercurial')
    okfn_bin = '/home/okfn/bin'
    if env.user != 'okfn':
        def ourrun(cmd):
            sudo(cmd, user='okfn')
    else:
        ourrun = run
    
    if not exists(SYSADMIN_REPO_PATH):
        ourrun('hg clone https://bitbucket.org/okfn/sysadmin %s' %
                SYSADMIN_REPO_PATH)
    if not exists(OKFN_ETC):
        ourrun('ln -s %s %s' % (SYSADMIN_REPO_PATH + '/etc', OKFN_ETC))
    if not exists(okfn_bin):
        ourrun('ln -s %s %s' % (SYSADMIN_REPO_PATH + '/bin', okfn_bin))

def sysadmin_repo_update():
    '''Update okfn sysadmin repo'''
    run('hg pull -u -R %s' % SYSADMIN_REPO_PATH)


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
*.bak
*.orig

syntax: regexp
.*~$
'''
    install_set('mercurial')
    append(etc_hgignore, '/etc/.hgignore', use_sudo=True)
    with cd('/etc/'):
        _sudo('hg init')
        _sudo('hg add')
        _sudo('hg commit --user "okfn sysadmin" -m "[all][l]: import existing /etc contents into hg"')


def unattended_upgrades():
    '''Install and configure "unattended-upgrades" such that security 
    patches get installed automagically
    '''
    install('unattended-upgrades', update_first=True)


## ============================
## SSH Keys

def ssh_add_public_key(key_config, user, dest_user):
    '''Add public key of user in config file to `dest_user` on remote host.

    :param key_config: json file giving key config
    :param user: user to add from config file.
    :param dest_user: user on dest host to add public key to.
    '''
    info = json.load(open(key_config))
    key = info['users'][user]['key']
    _ssh_add_public_key(key, dest_user)

def ssh_add_public_key_group(key_config, group, dest_user):
    '''Add public keys of users listed in `group` in config file to
    `dest_user` on remote host.

    :param key_config: json file giving key config
    :param group: group to add from config file.
    :param dest_user: user on dest host to add public key to.
    '''
    info = json.load(open(key_config))
    for user in info['groups'][group]:
        key = info['users'][user]['key']
        _ssh_add_public_key(key, dest_user)

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
            _sudo('mkdir %s' % sshdir)
            _sudo('chown -R %s:%s %s' % (dest_user, dest_user, sshdir))
            _sudo('chmod go-rwx -R %s' % sshdir)
        append(public_key, authorized_keys_path, use_sudo=True)

def ssh_add_private_key(key_path, user='root'):
    '''Add private key at `key_path` for `user`.

    @param key_path: path to key
    @parm user: (default: root) user to add key for.
    '''
    key_name = os.path.basename(key_path)
    dest = _join(_SSH.ssh_dir(user), key_name)
    put(key_path, dest)


def harden_sshd():
    '''Disables root login and password based login via ssh.
    '''
    config = '/etc/ssh/sshd_config'
    sed(config, '^[ \\t#]*(PermitRootLogin)[ \\t]+[yn][eo].*',        '\\1 no', backup='.ORIG', use_sudo=True)
    sed(config, '^[ \\t#]*(PasswordAuthentication)[ \\t]+[yn][eo].*', '\\1 no', backup='',      use_sudo=True)
    _sudo('restart ssh')


def generate_locale(locale='en_GB.utf8'):
    '''Generates missing locales
    '''
    # Todo: find out necessary locale automagically!
    _sudo('locale-gen %s' % locale )


def firewall_insert_rule(rule):
    '''Add a rule to "filter" table of /etc/iptables.conf
    '''

    cf = '/etc/iptables.conf'
    assert exists(cf), 'Fatal: iptables ruleset %s does not exist!' % cf
    
    marker = 'FAB-INSERT-IPTABLES-INPUT-RULES'
    if not contains(marker, cf, exact=False, use_sudo=False) :
        print 'Fatal: iptables ruleset %s does not contain marker "%s"!' % (cf, marker)
        return False

    sed(cf, '^(.*%s.*)' % marker, '\\1\\n%s' % rule, backup='', use_sudo=True)


def install_firewall(rules=[], copy_config=False):
    '''Install iptables load script and default firewall ruleset.
    Use "copy_config=True" to copy the config from Bitbucket rather than
    softlinking it from the local hg repository
    '''

    install('iptables')

    REMOTE_REPO = 'https://bitbucket.org/okfn/sysadmin/raw/default/etc'

    if copy_config :
        sudo('wget -P /etc                  %s/iptables/iptables.conf' % REMOTE_REPO )
        sudo('wget -O /etc/init.d/iptables  %s/iptables/iptables.sysv' % REMOTE_REPO )
    else :
        sysadmin_repo_update()
        sudo('cp --preserve=timestamps %s/iptables/iptables.conf /etc/iptables.conf'   % OKFN_ETC)
        sudo('ln -s                    %s/iptables/iptables.sysv /etc/init.d/iptables' % OKFN_ETC)

    sudo('chmod +x /etc/init.d/iptables')

    for rule in rules:
        firewall_insert_rule(rule)

    # Check that the iptables modules we need are there:
    for match in ['state'] :
        if not contains(match, '/proc/net/ip_tables_matches', exact=True, use_sudo=True) :
            print 'WARNING: iptables match "%s" not found - not activating firewall!' % match
            return
    
    print 'INFO: Activating firewall.'
    sudo('update-rc.d iptables start 09 2 3 4 5 .')
    sudo('/etc/init.d/iptables start')


def install_firewall_fry():
    additional_firewall_rules = [
            '-A INPUT -j ACCEPT -p tcp  -s monitor1.fry-it.com  # Allow Fry monitors',
            '-A INPUT -j ACCEPT -p tcp  -s monitor2.fry-it.com'
    ]
    install_firewall(rules=additional_firewall_rules, copy_config=True)


## =========================================
## Installation of packages and applications

package_sets = {
    # TODO visudo and add relevant users to sudo list
    'basics': [
        'vim-nox',
        'sudo',
        'man-db',
        'bsd-mailx',
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

def install(package, update_first=False):
    '''Install package onto host.
    
    Should try to login as root for this as may not have sudo installed yet.

    :param package: apt package name or a command if starts with cmd:: (e.g. 
        cmd::easy_install --always-unzip supervisor)
    :param update_first: run apt-get update first.
    '''
    # avoid using sudo when root (so we can e.g. install sudo package!)
    if env.user != 'root':
        env.use_sudo = True
    if update_first:
        _sudo('apt-get update')
    if '::' not in package: # default
        _sudo('apt-get -y install %s' % package)
    elif package.startswith('cmd::'):
        cmd = package.split('::')[1]
        _sudo(cmd)
    else:
        print 'Unrecognized package format: %s' % package


def upgrade(update_first=True):
    '''Upgrade all packages'''
    if env.user != 'root':
        env.use_sudo = True
    if update_first:
        _sudo('apt-get update')
    _sudo('apt-get -y autoremove')
    _sudo('apt-get -y upgrade')


def install_set(package_set='basics', update_first=False):
    '''Install package set onto host.
    
    Should try to login as root for this as may not have sudo installed yet.

    Primarily system packages provided by apt.

    :param package: string specifying package set (list of package sets given
        below).
    :param update_first: run apt-get update first.

    Package Sets
    ============
    
    %s
    '''
    # avoid using sudo when root (so we can e.g. install sudo package!)
    if update_first:
        _sudo('apt-get update')
    for pkgname in package_sets[package_set]:
        if pkgname.startswith('set::'):
            setname = pkgname.split('::')[1]
            install_set(package_set=setname)
        else:
            install(pkgname)
install_set.__doc__ = install_set.__doc__ % pprint.pformat(package_sets)


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

    

def db_pg_dump(db_name, db_user, db_pass, db_host='localhost'):
    '''Dump postgres database `db_name` accessed with `db_user` and `db_pass`
    and retrieve dump to local machine (at ~/db_backup/{remote-host}).

    :param db_name: name of the db.
    :param db_user: name of db user.
    :param db_pass: db password.
    :param db_host: (default localhost) host string to connect with (from
        remote machine)
    '''
    # if hasattr(env, 'db_backup_dir_remote')
    remote_backup_dir = '/home/%s/db_backup/localhost' % env.user
    _mkdir(remote_backup_dir)
    pg_dump_filepath = _get_unique_filepath(remote_backup_dir, db_name + '.pg_dump') + '.gz'
    assert not exists(pg_dump_filepath), 'Dump filepath exists!'

    run('export PGPASSWORD=%s&&pg_dump -U %s -h %s %s | gzip > %s' % (db_pass, db_user, db_host, db_name, pg_dump_filepath), shell=False)
    assert exists(pg_dump_filepath)
    run('ls -l %s' % pg_dump_filepath)
    ## copy backup locally
    if env.host_string == 'localhost': # already on the machine
        return

    local_backup_dir = os.path.join(os.path.expanduser('~'), 'db_backup',
            env.host_string)
    if not os.path.exists(local_backup_dir):
        os.makedirs(local_backup_dir)
    local_filepath = get(pg_dump_filepath, local_backup_dir)
    ## unzip it
    # subprocess.check_call('gunzip %s' % local_zip_filepath, shell=True)
    # local_filepath = os.path.join(local_backup_dir, pg_dump_filename)
    print 'Backup saved locally: %s' % local_filepath

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
def backup_check_setup():
    if not exists('/etc/cron.daily/01check_backup'):
        sudo('ln -s /home/okfn/bin/01check_backup /etc/cron.daily/01check_backup')
    if not exists('/etc/cron.daily/99check_backup'):
        sudo('ln -s /home/okfn/bin/99check_backup /etc/cron.daily/99check_backup')
    if not exists('/usr/local/bin/stamp_backup'):
        sudo('ln -s /home/okfn/bin/stamp_backup /usr/local/bin/stamp_backup')

def backup_setup():
    '''Set up backup for host specified by --host.'''
    if not exists('/etc/backup'):
        sudo('ln -s /home/okfn/etc/backup /etc/backup')
    else:
        print 'WARNING: /etc/backup already exists'
    filedest = '/etc/cron.daily/backuprotatingsnapshot'
    if not exists(filedest):
        sudo('ln -s /home/okfn/etc/cron/backuprotatingsnapshot %s' % filedest)
    # standard locations -- you can configure as you want ...
    # TODO: source this info from /etc/backup/backuprc for DRY reasons
    config = {
        'mount_device' : '/dev/sdp',
        'snapshot_rw' : '/mnt/backup_rw',
        'snapshot_ro' : '/mnt/backup_ro'
        }
    if not exists(config['snapshot_rw']):
        sudo('mkdir -p %s' % config['snapshot_rw'])
    if not exists(config['snapshot_ro']):
        sudo('mkdir -p %s' % config['snapshot_ro'])
    setup_backup_check()
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
        backups = sudo('ls -l --time-style=long-iso %(snapshot_ro)s/%(hostname)s' % locals())
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


## ============================
## Munin

def munin_node_install(copy_config=False):
    '''Install munin node on a host.
    Use "copy_config=True" to copy the config from Bitbucket rather than
    softlinking it from the local hg repository
    '''

    install('munin-node')

    REMOTE_REPO = 'https://bitbucket.org/okfn/sysadmin/raw/default/etc'
    LOCAL_REPO  = OKFN_ETC

    nodeconf_suffix = '/munin/munin-node.conf'
    nodeconf = '/etc' + nodeconf_suffix

    if exists(nodeconf):
        sudo('mv %s %s.orig' % (nodeconf, nodeconf))

    if copy_config :
        sudo('wget -O %s %s' % (nodeconf, REMOTE_REPO + nodeconf_suffix))
    else :
        sysadmin_repo_update()
        sudo('ln -s %s %s' % (OKFN_ETC + nodeconf_suffix, nodeconf))

    sudo('/etc/init.d/munin-node restart')


## ============================
## Supervisor

def supervisor_install():
    '''Install supervisor(d) including /etc/init.d and standard /etc script.

    NB: supervisor is a proper package in debian squeeze and ubuntu lucid
    onwards
    '''
    install_set('supervisor')
    _initd = 'http://svn.supervisord.org/initscripts/debian-norrgard'
    get(initd, '/etc/init.d/supervisord')


def create_swap_file(size=1) :
    '''Create and activate swap file of size 'size' (in GB)
    '''
    fstab = '/etc/fstab'
    swapfile = '/swap'
    MB = 1024*1024
    swapsize_in_MB = int(size) * 1024

    assert not exists(swapfile), 'Error: swap file %s already exists!' % swapfile

    print 'Creating swap file %s of size %s MB' % (swapfile, swapsize_in_MB)
    sudo('dd if=/dev/zero of=%s bs=%s count=%s' % (swapfile, MB, swapsize_in_MB) )
    sudo('mkswap %s' % swapfile)

    fstab_line = swapfile + ' swap swap defaults 0 0'
    print 'appending "%s" to %s' % (fstab_line, fstab)
    append(fstab_line, fstab, use_sudo=True)

    print 'Activating swap' 
    sudo('swapon -a')


def postfix_install(copy_config=False):
    '''Install postfix and coufigure from sysadmin repo for sending only
    Use "copy_config=True" to copy the config from Bitbucket rather than
    softlinking it from the local hg repository
    '''

    service = 'postfix'
    config_rel = '/postfix/main.cf'

    config_abs = '/etc' + config_rel
    REMOTE_REPO = 'https://bitbucket.org/okfn/sysadmin/raw/default/etc'
    LOCAL_REPO  = OKFN_ETC

    mta_binary = '/usr/sbin/sendmail'
    assert not exists(mta_binary), 'Error: A MTA %s is already installed!' % mta_binary 

    assert not exists(config_abs), 'Error: Configuration file %s already exists!' % config_abs
    if not copy_config: 
        sysadmin_repo_update()

    install('debconf-utils')
    run('echo "postfix postfix/mailname        string  localhost" | sudo debconf-set-selections')
    run('echo "postfix postfix/main_mailer_type        select  No configuration" | sudo debconf-set-selections')
    install(service)
    sudo('mv %s %s.ORIG' % (config_abs, config_abs))

    if copy_config :
        sudo('wget -O %s %s' % (config_abs, REMOTE_REPO + config_rel ))
    else :
        sudo('ln -s %s %s' % (OKFN_ETC + config_rel, config_abs))
    sudo('/etc/init.d/%s restart' % service )

    set_root_alias()

    install('bsd-mailx')


def _get_default_root_alias():
    '''OKFN default root alias is this.'''
    return 'sysadmin@okfn.org'


def set_root_alias(mail_address='') :
    '''Sets mail alias for root@localhost. 
    If emtpy use default, see _get_default_root_alias() for default.
    '''

    if not mail_address:
        mail_address = _get_default_root_alias()

    aliasfile = '/etc/aliases'
    # assert exists(aliasfile), 'Error: Alias file %s missing!' % aliasfile
    # Soft error instead
    if not exists(aliasfile):
        print 'ERROR: Alias file %s is missing, no root alisas configured!' % aliasfile
        return True

    # Removing the root alias first and then append the new one is not very elegant, i know, 
    # but i don't know how to have a condition here "is there alread a root alias?"
    sudo('sed -e  "/^root:/D" -i /etc/aliases')
    append('root: %s' % mail_address, aliasfile, use_sudo=True)
    sudo('newaliases')
    sudo('/etc/init.d/postfix reload')


def fix_fry_postfix() :
    '''On Fry machines, the postfix's main.cf has an explicit hostname set for 
    "myhostname" and "mydestination", this function fixes that.
    Fry will fix their template. Once that is done, this function can go
    '''

    config = '/etc/postfix/main.cf'

    sudo('cp -a %s %s.ORIG' % (config, config) )
    sed(config, '^(myhostname =).*',     '# \\1',                      backup='', use_sudo=True)
    sed(config, '^(myorigin =).*',       '\\1 $myhostname',            backup='', use_sudo=True)
    sed(config, '^(mydestination =).*' , '\\1 $myhostname, localhost', backup='', use_sudo=True)
   
    sudo('/etc/init.d/postfix reload')

