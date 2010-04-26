#!/usr/bin/env python
import os
import urllib

# http://codex.wordpress.org/Installing/Updating_WordPress_with_Subversion
def install_svn(path, version='2.9.2'):
    cmd = 'svn co http://core.svn.wordpress.org/tags/%s %s' % (version, path)
    print 'Running: %s' % cmd
    os.system(cmd)

def secretkey():
    # since 2.6
    url = 'https://api.wordpress.org/secret-key/1.1/'
    out = urllib.urlopen(url)
    print out.read()

if __name__ == '__main__':
    import optparse
    import sys
    usage = '''%prog {action}

    install-svn path  # install wp via svn method to path
    secretkey # generate secret keys for config
    '''
    parser = optparse.OptionParser(usage)
    parser.add_option('-w', '--wp-version',
            help='Wordpress version (e.g. 2.9.2) to use',
            default='2.9.2')
    options, args = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        sys.exit(1)
    action = args[0] 
    if action == 'install-svn':
        path = args[1]
        install_svn(path, options.wp_version)
    elif action == 'secretkey':
        secretkey()
    else:
        parser.print_help()
        sys.exit(1)

