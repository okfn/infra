# -*- coding: iso-8859-1 -*-
# IMPORTANT! This encoding (charset) setting MUST be correct! If you live in a
# western country and you don't know that you use utf-8, you probably want to
# use iso-8859-1 (or some other iso charset). If you use utf-8 (a Unicode
# encoding) you MUST use: coding: utf-8
# That setting must match the encoding your editor uses when you modify the
# settings below. If it does not, special non-ASCII chars will be wrong.
from MoinMoin.multiconfig import DefaultConfig

class Config(DefaultConfig):

    # basic options (you normally need to change these)
    sitename = u'FCUK theme' # [Unicode]

    # if you have a logo you can do
    # logo_string = u'

    theme_default = 'fcuk'
    theme_force = True

    # this will produce the buttons across the top
    # format is just as for moinmoin navi_bar
    navi_bar = [ u'[FrontPage Home]',
                 u'[GetInvolved Get Involved]',
                 u'[projects Projects]',
                 u'[FindPage Search]',
                 u'[RecentChanges Recent Changes]',
    ]

    # contents of this goes into the sidebar
    # format should be html which will be directly inserted
    sidebar = u'''
            <h3>
                Demo Heading     
            </h3>
            <ul>
                <li><a href="/">First Item</a></li>
                <li><a href="/">Second Item</a></li>
            </ul>
            '''

    # show the edit bar even if the user does not have write permissions
    # show_editbar = True

    # this will be added at the very bottom of the page.
    # format should be raw html
    page_footer2 = u'<p>Some extra footer stuff</p>'
