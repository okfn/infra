#!/usr/bin/env python
# Based off instructions like:
# http://paste.lisp.org/display/59757
# http://svn.pythonpaste.org/Paste/trunk/paste/modpython.py

import os

binfile = '''
import os
import site
site.addsitedir('%s')

from paste.modpython import handler
'''

apache_config = \
'''SetHandler python-program
PythonPath "['%s'] + sys.path"
PythonHandler %s
PythonOption paste.ini %s'''

def get_site_packages(venv):
    lib = os.path.join(venv, 'lib')
    # do not know the python version
    # lib/pythonVERSION/site-packages'
    fn = os.listdir(lib)[0]
    sp = os.path.join(lib, fn, 'site-packages')
    return sp

def doit(venv, paste_config_fp='production.ini'):
    bin = os.path.abspath(os.path.join(venv, u'bin'))
    sitepackages = get_site_packages(venv)
    binfilename = 'pylonsapp'
    binfile_path = os.path.join(bin, binfilename + '.py')

    create_cmd = 'virtualenv --no-site-packages %s' % venv
    print '### Step 1: create your virtualenv and deploy your code'
    print 'Run: %s' % create_cmd
    print 'Run: %s setup.py install (or develop)' % os.path.join(bin, 'python')
    print

    print '### Step 2: Create frontend script for mod python'
    print 'Creating script'
    ourbinfile = binfile % sitepackages
    print 'Installing script %s' % (binfile_path)
    if os.path.exists(binfile_path):
        print
        print 'WARNING: overwriting existing script at: %s' % binfile_path
        # raise Exception('File already exists at: %s' % binfile_path)
    fo = open(binfile_path, 'w')
    fo.write(ourbinfile)
    fo.close()
    print

    print '### Step 3'
    print 'Put this in your apache config file'
    print '-------------'
    ourapache = apache_config % (bin, binfilename, paste_config_fp)
    print ourapache
    print '-------------'


import optparse
if __name__ == '__main__':
    usage = '''%prog

Setup virtualenv and convert pylons setup to use it.
'''
    parser = optparse.OptionParser(usage)
    parser.add_option('-e', '--environment',
        dest='venv',
        help='path to your virtualenv (default=%default)',
        default='pyenv'
        )
    parser.add_option('-c', '--config',
        dest='config',
        help='path to paste/pylons configuration (default=%default)',
        default='production.ini'
        )
    options, args = parser.parse_args()
    doit(options.venv, os.path.abspath(options.config))

