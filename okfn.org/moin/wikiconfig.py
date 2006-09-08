# -*- coding: iso-8859-1 -*-
# IMPORTANT! This encoding (charset) setting MUST be correct! If you live in a
# western country and you don't know that you use utf-8, you probably want to
# use iso-8859-1 (or some other iso charset). If you use utf-8 (a Unicode
# encoding) you MUST use: coding: utf-8
# That setting must match the encoding your editor uses when you modify the
# settings below. If it does not, special non-ASCII chars will be wrong.

"""
This is a sample config for a wiki that isn't part of a farm but does use
farmconfig for common stuff. Here we define what has to be different from
the farm's common settings.
"""
# Need to set the path since file will be installed in wiki instance dir
import sys
sys.path.insert(0, '/etc/moin')
# we import the FarmConfig class for common defaults of our wikis:
from farmconfig import FarmConfig

# now we subclass that config (inherit from it) and change what's different:
class Config(FarmConfig):

    # basic options (you normally need to change these)
    sitename = u'Open Knowledge Foundation' # [Unicode]
    interwikiname = 'Open Knowledge Foundation'
    data_dir = './data/'

    logo_string = u'''
    	<h1><a href="/">The Open Knowledge Foundation</a></h1>
	<h2>Protecting and Promoting Open Knowledge in a Digital Age</h2>
	'''

    # follow HelpOnAccessControlLists example for a CMS
    acl_rights_default = u'All:read'
    acl_rights_before = u'rgrp,zool:read,write,delete,revert,admin'

    sidebar = u'''
            <h3><a href="/">General</a></h3>
            <ul>
                <li><a href="http://blog.okfn.org/">Weblog and News</a></li>
                <li><a href="/projects/">Projects</a></li>
                <li><a href="/participate/">Participate</a></li>
                <li><a href="/support/">Support the Foundation</a></li>
                <li><a href="/contact/">Contact Us</a></li>
            </ul>
            
            <h3><a href="/resources/">Resources</a></h3>
            <ul>
                <li><a href="/wiki/">Wiki</a></li>
                <li><a href="http://lists.okfn.org/mailman/listinfo">Mailing Lists</a></li>
                <li><a href="/search/">Search</a></li>
                <li><a href="/ok_trail/">Open Knowledge Trail</a></li>
                <li><a href="/research/">Research</a></li>
            </ul>
            
            <h3><a href="/about/">About</a></h3>
            <ul>
                <li><a href="/advisory_board/">Advisory Board</a></li>
                <li><a href="/activities/">Activities</a></li>
                <li><a href="/roadmap/">Roadmap</a></li>
                <li><a href="/governance/">Governance</a></li>
            </ul>
	    '''

    # The default theme anonymous or new users get
    theme_default = 'okfn'
    theme_force = 'true'

