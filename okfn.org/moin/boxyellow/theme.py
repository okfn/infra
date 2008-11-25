# -*- coding: iso-8859-1 -*-
from MoinMoin.theme import ThemeBase


class Theme(ThemeBase):
    """OKFN theme adapated from the moinmoin modern theme.
    
    TODO: sort out some way to have normal links in navibar e.g.
    item like [/?action=login Login]
              [?action=edit Edit This Page]
    """

    name = "boxyellow"

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
            u'<div id="wrap">',
            
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

    def navibar(self, d):
        """Standard navibar function modified to exclude userlinks, and
        current page.
        """
        request = self.request
        items = [] # navibar items
        item = u'<li class="%s">%s</li>'
        current = d['page_name']

        # Process config navi_bar
        if request.cfg.navi_bar:
            for text in request.cfg.navi_bar:
                pagename, link = self.splitNavilink(text)
                cls = 'wikilink'
                if pagename == current:
                    cls = 'wikilink current'
                items.append(item % (cls, link))

        # Assemble html
        items = u'\n'.join(items)
        html = u'''
<ul id="navibar">
%s
</ul>
''' % items
        return html
    
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
        userinfo = u''
        show_edit_bar = False
        try:
            show_edit_bar = self.cfg.show_editbar
        except:
            pass
        if self.userCanWrite(page) or show_edit_bar:
            editbar = self.editbar(d)
            userinfo = self.username(d)

        html = [
            # End of page
            # self.pageinfo(page),
            self.endPage(),
            
            # Pre footer custom html (not recommended!)
            self.emit_custom_html(self.cfg.page_footer1),
            u'''<div id="clear">
                &nbsp;
            </div><!-- /clear -->''',
            # Footer
            u'<div id="footer">',
            userinfo,
            editbar,
            u'<div id="div-pagetrail">',
            self.trail(d),
            u'</div>',
            u'<div id="new-credits">',
            # Post footer custom html
            self.emit_custom_html(self.cfg.page_footer2),
            u'</div>',
            u'</div>',
            u'</div><!-- wrap -->', 
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

