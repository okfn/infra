# -*- coding: iso-8859-1 -*-
"""
    MoinMoin modern theme

    @copyright: (c) 2003-2004 by Nir Soffer, Thomas Waldmann
    @license: GNU GPL, see COPYING for details.
"""

from MoinMoin.theme import ThemeBase


class Theme(ThemeBase):
    """OKFN fcuk theme adapated from the moinmoin modern theme.

    """

    name = "fcuk"

    def userCanWrite(self, page):
        return self.request.user.may.write(page.page_name)

    def header(self, d, **kw):
        """ Assemble wiki header
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: page header html
        """
        html = [
            # Pre header custom html
            self.emit_custom_html(self.cfg.page_header1),
            
            # Header
            u'<div id="header">',
            self.special_logo(),
            # self.searchform(d),
            # self.username(d),
            # self.trail(d),
            self.navibar(d),
            #u'<hr id="pageline">',
            # u'<div id="pageline"><hr style="display:none;"></div>',
            self.msg(d),
            # self.editbar(d),
            u'</div>',
            
            # Post header custom html (not recommended)
            self.emit_custom_html(self.cfg.page_header2),
            
            # sidebar (ADDED by rgrp):
            self.sidebar(),
            
            # Start of page
            self.startPage(),
            # self.title(d),
        ]
        return u'\n'.join(html)
    
    def special_logo(self):
        special_logo_string = ''
        try: # sidebar attribute may not exist
            special_logo_string = self.cfg.special_logo_string
            return u'''<div id="logo">%s</div>''' % special_logo_string
        except:
            return self.logo()
    
    def sidebar(self):
        html = u"""
        <div id="sidewrap">
	        <div id="sidebartop">
	          <span>&nbsp;</span>
	        </div><!-- /sidebartop -->
	        
	        <div id="sidebar">
                %s
	        </div><!-- /sidebar -->
	        
        </div><!-- /sidewrap -->
        """
        sideBarContent = None
        try: # sidebar attribute may not exist
            sideBarContent = self.cfg.sidebar
        except:
            sideBarContent = ''
        if sideBarContent:
            return html % sideBarContent
        else:
            return ''
    
    def footer(self, d, **keywords):
        """ Assemble wiki footer
        
        @param d: parameter dictionary
        @keyword ...:...
        @rtype: unicode
        @return: page footer html
        """
        page = d['page']
        editbar = u''
        show_edit_bar = False
        try:
            show_edit_bar = self.cfg.show_editbar
        except:
            pass
        if self.userCanWrite(page) or show_edit_bar:
            editbar = self.editbar(d)

        html = [
            # End of page
            self.pageinfo(page),
            self.endPage(),
            
            # Pre footer custom html (not recommended!)
            self.emit_custom_html(self.cfg.page_footer1),
            
            # Footer
            u'<div id="footer">',
            editbar,
            u'<div id="div-pagetrail">',
            self.trail(d),
            u'</div>',
            u'<div id="new-credits">',
            # Post footer custom html
            self.emit_custom_html(self.cfg.page_footer2),
            u'</div>',
            u'</div>',
            ]
        return u'\n'.join(html)
        

def execute(request):
    """
    Generate and return a theme object
        
    @param request: the request object
    @rtype: MoinTheme
    @return: Theme object
    """
    return Theme(request)

