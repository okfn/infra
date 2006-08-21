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
            <h3>General Information</h3>
            <ul>
              	<li><a href="/">Home</a></li>
                <li><a href="/activities/">Activities</a></li>
                <li><a href="/roadmap/">Roadmap</a></li>
                <li><a href="http://blog.okfn.org/">Blog and News</a></li>
                <li><a href="/wiki/">Wiki</a></li>
                <li><a href="/about/">About</a></li>
                <li><a href="/contact/">Contact</a></li>
                <li><a href="/support/">Support the Foundation</a></li>
            </ul>
            <h3>Open Knowledge Trail</h3>
            <ul>
                <li><a href="/ok_trail/">Home</a></li>
                <li><a href="/ok_trail/think_again/">Think Again</a></li>
                <li><a href="/ok_trail/copyright/">Copyright</a></li>
                <li><a href="/ok_trail/drug_patents/">Drug Patents</a></li>
                <li><a href="/ok_trail/file_sharing/">File sharing</a></li>
                <li><a href="/ok_trail/open_source_software/">Open Source Software</a></li>
                <li><a href="/ok_trail/open_projects/">Open Information</a></li>
            </ul>
            
            <h3>
                Projects
            </h3>
            <ul>
              <li><a href="/projects/">Home</a></li>
                <li><a href="/okforums/">Open Knowledge Forums</a></li>
                <li><a href="/okd/">Open Knowledge Definition</a></li>
                <li><a href="/drn/">Digital Rights Network</a></li>
                <li><a href="http://www.freeculture.org.uk/">Free Culture UK</a></li>
                <li><a href="/iai/">Information Accessibility Initiative</a></li>
                <li><a href="/kforge/">KnowledgeForge</a></li>
                <li><a href="/geo/">Open Geodata</a></li>
                <li><a href="http://www.witbd.org/">What is To be Done</a></li>
                <li><a href="/wsfii/">WSFII</a></li>
            </ul>
	    '''

    # The default theme anonymous or new users get
    theme_default = 'okfn'
    theme_force = 'true'

