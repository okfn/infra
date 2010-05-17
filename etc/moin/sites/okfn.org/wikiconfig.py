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
    sitename = u'The Open Knowledge Foundation' # [Unicode]
    page_front_page = u'FrontPage'

    # The default theme anonymous or new users get
    theme_default = 'boxyellow'
    theme_force = 'true'

    logo_string = u'''
        <a href="/">
            <img class="logo"
            src="http://m.okfn.org/gfx/logo/okf_logo_white_and_green.png"
            alt="OKF Logo" style="heigt: 55px;" />
        </a>
    	<a href="/">The Open Knowledge Foundation</a>
        <p style="font-size: 0.5em; letter-spacing: 0em;">Promoting Open Knowledge in a Digital Age</p>
	'''

    # follow HelpOnAccessControlLists example for a CMS
    acl_rights_default = u'All:read'
    acl_rights_before = u'rgrp,AdminGroup:read,write,delete,revert,admin'

    # enable email
    mail_smarthost = "localhost"
    mail_from = u'no-reply@okfn.org'

    html_head = u'''
    <link rel="shortcut icon" href="/images/favicon.ico">
    <!-- ... more header stuff ... -->
    '''

    navi_bar = [
        u'[[/|Home]]',
        u'[[http://blog.okfn.org/|Blog]]',
        u'[[/projects/|Projects]]',
        u'[[/events/|Events]]',
        u'[[/participate/|Get Involved]]',
        u'[[/support/|Support Us]]',
        u'[[/about/|About]]',
        u'[[/contact|Contact]]',
	]

    _sidebar = u'''
            <h3><a href="/">General</a></h3>
            <ul>
                <li><a href="http://blog.okfn.org/">Weblog and News</a></li>
                <li><a href="/projects/">Projects</a></li>
                <li><a href="/participate/">Participate</a></li>
                <li><a href="/contact/">Contact Us</a></li>
                <li><a href="/support/">Support the Foundation</a></li>
            </ul>

        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" style="margin-left: 20%; margin-bottom: 7px;">
            <input type="hidden" name="cmd" value="_xclick" />
            <input type="hidden" name="business" value="admin@okfn.org" />
            <input type="hidden" name="item_name" value="Open Knowledge Foundation" />
            <input type="hidden" name="item_number" value="okfn" />
            <input type="hidden" name="no_shipping" value="1" />
            <input type="hidden" name="cn" value="Donation to be used for (opt):" />
            <input type="hidden" name="currency_code" value="GBP" />
            <input type="hidden" name="tax" value="0" />
            <input type="hidden" name="bn" value="PP-DonationsBF" />
            <input type="image" src="https://www.paypal.com/en_US/i/btn/x-click-but21.gif" border="0" name="submit" alt="Make payments with PayPal - it's fast, free and secure!" />
            <img alt="" border="0" src="https://www.paypal.com/en_GB/i/scr/pixel.gif" width="1" height="1" />
        </form>    
            
            <h3><a href="/resources/">Resources</a></h3>
            <ul>
                <li><a href="/wiki/">Wiki</a></li>
                <li><a href="http://lists.okfn.org/mailman/listinfo">Mailing Lists</a></li>
                <li><a href="/search/">Search</a></li>
                <li><a href="/research/">Research</a></li>
            </ul>
            
            <h3><a href="/about/">About</a></h3>
            <ul>
                <li><a href="/about/people/">People</a></li>
                <li><a href="/advisory_board/">Advisory Board</a></li>
                <li><a href="/activities/">Activities</a></li>
                <li><a href="/roadmap/">Roadmap</a></li>
                <li><a href="/governance/">Governance</a></li>
            </ul>
	    '''

    page_footer2 = u'''
        <p>
            <a title="Valid HTML" href="http://validator.w3.org/check/referer">Valid HTML</a>
            - <a title="Valid CSS 1/2" href="http://jigsaw.w3.org/css-validator/check/referer">Valid CSS</a>
            - <a href="/contact/">Contact Us</a>
            - <a href="/privacy-policy/">Privacy Policy</a>
        </p>
        <p>
        (c) Open Knowledge Foundation
        - Available under an <a href="/ip-policy/">open license</a>
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
var pageTracker = _gat._getTracker("UA-8271754-1");
pageTracker._setDomainName("www.okfn.org");
pageTracker._trackPageview();
} catch(err) {}</script>
        '''

