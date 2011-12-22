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

## =====================================
## AWS Specific
## =====================================

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
    '''DEPRICATED. Use method of same name from ../bin/fabfile.py instead.'''
    print 'DEPRICATED. Use method of same name from ../bin/fabfile.py instead.'
    

def format_ebs(attach_point='/dev/sdp'):
    '''Format an EBS volume at `attach_point` (may have issues).

    Unfortunately fabric swallows prompt following warning::
    
    /dev/sdp is entire device, not just one partition!
    Proceed anyway? (y,n) n

    So you cannot answer 'y'.

    :param attach_point: attach point (defaults to /dev/sdp)
    '''
    cmd = 'mke2fs -m0 -F -j %s' % attach_point
    if env.user != 'root':
        sudo(cmd)
    else:
        run(cmd)

