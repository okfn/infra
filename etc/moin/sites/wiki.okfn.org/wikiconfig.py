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
    sitename = u'Open Knowledge Foundation Wiki' # [Unicode]
    interwikiname = 'Open Knowledge Foundation Wiki'
    page_front_page = u'FrontPage'

    # The default theme anonymous or new users get
    theme_default = 'monobook'
    theme_force = 'true'

    logo_string = u'''
    <div style="text-align: center;">
    <img style="width: 100px;" src="http://m.okfn.org/gfx/logo/okf_logo_white_and_green.png" alt="OKF Logo"/></span>
    <br />
    <h1 style="border-bottom: none; font-size: 1.3em; color: #666;">
    Open Knowledge Foundation
    </h1>
    </div>
    '''

    # follow HelpOnAccessControlLists example for a CMS
    superuser = [u'RufusPollock',u'NateOlson',u'JonathanGray']
    acl_rights_default = u'All:read,write'
    acl_rights_before = u'RufusPollock,AdminGroup:read,write,delete,revert,admin'

    html_head = u'''
    <link rel="shortcut icon" href="/images/favicon.ico">
    <!-- ... more header stuff ... -->
    '''

    stylesheets = [ ('screen', 'http://m.okfn.org/tmp/wiki.okfn.org.css') ]

    sidebar = u'''
            <h3>This Page</h3>
            <ul>
                <li><a href="?action=edit">Edit</a></li>
                <li><a href="?action=info">Page History</a></li>
                <li><a href="?action=raw">Raw Text</a></li>
                <li><a href="#footer">More Actions ...</a></li>
            </ul>

            <h3>General</h3>
            <ul>
                <li><a href="?action=login">Login</a></li>
                <li><a href="?action=logout">Logout</a></li>
                <li><a href="?action=newaccount">Register</a></li>
            </ul>

            <h3>Support Us</h3>
            <p>Help us continue our work:</p>
            <ul>
                <li><a href="http://www.okfn.org/support/">Become a Supporter</a></li>
                <li><a href="http://www.okfn.org/support/donate/">Make a Donation</a></li>
            </ul>
	    '''

    page_footer2 = u'''
        <p>
            <a title="Valid HTML" href="http://validator.w3.org/check/referer">Valid HTML</a>
            - <a title="Valid CSS 1/2" href="http://jigsaw.w3.org/css-validator/check/referer">Valid CSS</a>
            - <a href="http://www.okfn.org/contact/">Contact Us</a>
            - <a href="http://www.okfn.org/privacy-policy/">Privacy Policy</a>
        </p>
        <p>
        (c) Open Knowledge Foundation
        - Available under an <a href="http://www.okfn.org/ip-policy/">open license</a>
        - <a href="http://www.opendefinition.org/"><img style="border: none; margin-bottom: -4px;" src="http://m.okfn.org/images/ok_buttons/ok_90x15_blue.png" alt="This Material is Open"></a>
        </p>

        <!-- Get Satisfaction -->
<script type="text/javascript" charset="utf-8">
  var is_ssl = ("https:" == document.location.protocol);
  var asset_host = is_ssl ? "https://s3.amazonaws.com/getsatisfaction.com/" : "http://s3.amazonaws.com/getsatisfaction.com/";
  document.write(unescape("%3Cscript src='" + asset_host + "javascripts/feedback-v2.js' type='text/javascript'%3E%3C/script%3E"));
</script>

<script type="text/javascript" charset="utf-8">
  var feedback_widget_options = {};

  feedback_widget_options.display = "overlay";  
  feedback_widget_options.company = "okfn";
  feedback_widget_options.placement = "right";
  feedback_widget_options.color = "#222";
  feedback_widget_options.style = "idea";
  var feedback_widget = new GSFN.feedback_widget(feedback_widget_options);
</script>

        <!-- Google Analytics -->
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-8271754-3");
pageTracker._trackPageview();
} catch(err) {}</script>
        '''
    
    from MoinMoin.auth import MoinAuth
    from MoinMoin.auth.openidrp import OpenIDAuth
    auth = [OpenIDAuth(), MoinAuth()]
    # have to enable anonymous session for openid
    anonymous_session_lifetime = 1

    from MoinMoin.security.antispam import SecurityPolicy
    textchas_disabled_group = u"AdminGroup" # members of this don't get textchas
    textchas = {
        'en': {
            # u"What is 5+3?": ur"8",
            u"What are last 4 letters of 'openness'?": ur"ness",
            u"What are the first four letters of 'freedom'?": ur"free",
        },
    } 

    # enable email
    mail_smarthost = "localhost"
    mail_from = u'no-reply@okfn.org'

