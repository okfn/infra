#!/usr/bin/env python
# Based off instructions like:
# http://pypi.python.org/pypi/virtualenv#using-virtualenv-without-bin-python
# http://paste.lisp.org/display/59757
# http://svn.pythonpaste.org/Paste/trunk/paste/modpython.py

import os
import shutil

class DeployBase(object):
    deployment_type = ''

    def binfile_contents(self):
        raise NotImplementedError()

    def apache_config(self):
        raise NotImplementedError()

    def get_site_packages(self, venv):
        lib = os.path.join(venv, 'lib')
        # do not know the python version
        # lib/pythonVERSION/site-packages'
        fn = os.listdir(lib)[0]
        sp = os.path.abspath(os.path.join(lib, fn, 'site-packages'))
        return sp

    def doit(self, venv, paste_config_fp='production.ini'):
        self.bin_path = os.path.abspath(os.path.join(venv, u'bin'))
        self.paste_config_fp = paste_config_fp
        self.site_packages = self.get_site_packages(venv)
        self.binfilename = 'pylonsapp_' + self.deployment_type
        self.binfile_path = os.path.join(self.bin_path, self.binfilename + '.py')

        print '### Preliminaries:'
        print 'Testing existence of virtualenv environment at %s'  % venv
        assert os.path.exists(venv), 'No virtualenv environment at %s' % venv

        print '### Step 2: Creating frontend script for mod python'
        print 'Creating script'
        contents = self.binfile_contents()
        print 'Installing script %s' % (self.binfile_path)
        if os.path.exists(self.binfile_path):
            print
            print 'WARNING: existing script at: %s' % self.binfile_path
            tbackup = self.binfile_path + '.bak'
            print 'Copying backup to: %s' % tbackup
            shutil.copy(self.binfile_path, tbackup)

        fo = open(self.binfile_path, 'w')
        fo.write(contents)
        fo.close()
        print

        print '### Step 3'
        print 'Put this in your apache config file'
        print '-------------'
        ourapache = self.apache_config()
        print ourapache
        print '-------------'

class DeployModWsgi(DeployBase):
    # http://code.google.com/p/modwsgi/wiki/VirtualEnvironments
    # According to that may be issues with activate_this.py
    # (recommend their own bespoke script)
    # However seems to work fine for us ...
    deployment_type = 'modwsgi'
    _binfile = '''import os

# Does not deal with reordering of sys.path
# See http://code.google.com/p/modwsgi/wiki/VirtualEnvironments
# import site
# site.addsitedir('%s')

here = os.path.abspath(os.path.dirname(__file__))
activate_this = os.path.join(here, 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

from paste.deploy import loadapp
application = loadapp('config:%s')
'''

    def binfile_contents(self):
        return self._binfile % ( self.site_packages, self.paste_config_fp)

    def apache_config(self):
        return 'WSGIScriptAlias / %s' % self.binfile_path


class DeployModPython(DeployBase):
    deployment_type = 'modpython'

    # Follows
    # http://pypi.python.org/pypi/virtualenv#using-virtualenv-without-bin-python 
    # simpler approach just uses site.addsitedir but not sufficient
    # (does not result in correct ordering of sys.path)
    # activate_this also messes with sys.prefix which can be a problem see
    # http://code.google.com/p/modwsgi/wiki/VirtualEnvironments
    binfile = '''import os
here = os.path.abspath(os.path.dirname(__file__))
activate_this = os.path.join(here, 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

from paste.modpython import handler
'''
    def binfile_contents(self):
        return self.binfile

    _apache_config = \
    '''SetHandler python-program
PythonPath "['%s'] + sys.path"
PythonHandler %s
PythonOption paste.ini %s'''

    def apache_config(self):
        return self._apache_config % (self.bin_path, self.binfilename, self.paste_config_fp)



import optparse
import sys
if __name__ == '__main__':
    usage = '''%prog virtualenv_path

Setup virtualenv for production deployment via mod_wsgi, mod_python etc.
'''
    parser = optparse.OptionParser(usage)
    parser.add_option('-c', '--config',
        dest='config',
        help='path to paste/pylons configuration (default=%default)',
        default='production.ini'
        )
    parser.add_option('-t', '--type',
        dest='type',
        help='Type of deployemnt (mod-wsgi (default), mod-python)',
        default='mod-wsgi'
        )
    options, args = parser.parse_args()
    if options.type == 'mod-wsgi':
        _cls = DeployModWsgi()
    elif options.type == 'mod-python':
        _cls = DeployModPython()
    else:
        print 'Unknown type: %s' % options.type
        sys.exit(1)
    if not args:
        print 'No virtualenv path supplied'
        sys.exit(1)
    venv = args[0]
    _cls.doit(venv, os.path.abspath(options.config))

