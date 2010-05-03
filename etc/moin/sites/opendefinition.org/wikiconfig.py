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
    sitename = u'Open Knowledge Definition - Defining the Open in Open Data, Open Content and Open Information' # [Unicode]
    interwikiname = 'Open Knowledge Definition'
    page_front_page = u'FrontPage'

    logo_string = u'''
    <h1><a href="/">The Open Knowledge Definition</a></h1>
    <h2>Defining the <em>Open</em> in Open Data, Open Content and Open Information</h2>
    '''

    # follow HelpOnAccessControlLists example for a CMS
    acl_rights_default = u'All:read'
    acl_rights_before = u'AdminGroup,RufusPollock:read,write,delete,revert,admin'

    navi_bar = [
        u'SECTIONHEADING: General Information',
        u'[[/|Home]]',
        u'[[about/|About]]',
        u'[[advisory-council/|Advisory Council]]',
        u'[[guide/|Guide]]',
        u'[[buttons/|Web Buttons]]',
        u'[[participate/|Participate]]',
        u'[[resources/|Resources]]',
        u'[[http://www.okfn.org/|Open Knowledge Foundation]]',
        u'SECTIONHEADING: The Definition',
        u'[[history/|History]]',
        u'[[1.0/|v1.0]]',
        u'[[dev/|Development Version]]',
        u'[[licenses/|Conformant Licenses]]',
        u'SECTIONHEADING: Other Definitions',
        u'[[ossd/|Open Service Definition]]',
    ]

    page_footer2 = u'''
    <!-- Google Analytics -->
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-8271754-4");
pageTracker._trackPageview();
} catch(err) {}</script>
    '''

    # The default theme anonymous or new users get
    theme_default = 'okfn'
    theme_force = 'true'

    from MoinMoin.security.antispam import SecurityPolicy
