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
# we import the FarmConfig class for common defaults of our wikis:
from farmconfig import FarmConfig

# now we subclass that config (inherit from it) and change what's different:
class Config(FarmConfig):

    # basic options (you normally need to change these)
    sitename = u'OKF Private Board Wiki' # [Unicode]
    interwikiname = 'OKF Private Board Wiki'
    page_front_page = u'FrontPage'

    # follow HelpOnAccessControlLists example for a CMS
    acl_rights_before = u'All:read,write,delete,revert,admin'

    data_dir = '/home/okfn/var/moinmoin/wiki/board.okfn.org/data'


