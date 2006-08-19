# -*- coding: iso-8859-1 -*-
from MoinMoin.theme import ThemeBase


class Theme(ThemeBase):
    """Merge moinmoin modern theme with okfn template (template_new.html)

    Configurable via moinmoin in following ways:
        * logo_string: will be used to generate title
        * navi_bar defines links for sidebar

    Notes
    =====

    Do not need content div as provided by moinmoin (page consists of content
    div nested in page div)

    Edit buttons only provided to users with write permission
    """

    name = "okfn"

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
            # self.emit_custom_html(self.cfg.page_header1),
            
            # Header
            u'''
	<div id="airlock">
		<div id="top_wrap">
			<div id="top">
            ''',
            self.logo(),
            # self.searchform(d),
            # self.username(d),
            # self.trail(d),
            #u'<hr id="pageline">',
            # u'<div id="pageline"><hr style="display:none;"></div>',
            self.msg(d),
            # self.editbar(d),
            u'''
            </div>
        </div><!-- /top_wrap -->
        <div id="content_wrap"> <!-- added to fix IE bugs -->
            ''',
            
            # Post header custom html (not recommended)
            # self.emit_custom_html(self.cfg.page_header2),
            
            # sidebar (ADDED by rgrp):
            self.sideBar(d),
            
            # Start of page
            self.startPage(),
            # self.navibar(d),
            # self.title(d),
        ]
        return u'\n'.join(html)
    
    def sideBar(self, d):
        """Use navibar to generate sidebar links.
        
        Borrowed from self.navibar in modern and modified to exclude userlinks
        etc
        """
        request = self.request
        items = [] # navibar items
        item = u'<li class="%s">%s</li>'
        heading = u'<h3>%s</h3>'
        current = d['page_name']
        default_heading = heading % u'Links'
        # Process config navi_bar
        if request.cfg.navi_bar:
            for text in request.cfg.navi_bar:
                if text.startswith(u'SECTIONHEADING:'):
                    if len(items) > 0: items.append(u'</ul>')
                    items.append(heading % text[15:])
                    items.append(u'<ul>')
                else:
                    if len(items) == 0: # no initial section heading
                        items.append(default_heading + u'<ul>')
                    pagename, link = self.splitNavilink(text)
                    cls = ''
                    if pagename == current:
                        cls = 'current'
                    items.append(item % (cls, link))
            items.append(u'</ul>')
        
        # Assemble html
        items = u'\n'.join(items)
        html = u"""<div id="sidebar">
            %s
        </div>
        """ % items
        return html
    
    def footer(self, d, **keywords):
        """ Assemble wiki footer
        
        @param d: parameter dictionary
        @keyword ...:...
        @rtype: unicode
        @return: page footer html
        """
        page = d['page']
        editbar = u''
        if self.userCanWrite(page):
            editbar = self.editbar(d)
        pagetrail = u'''
            <div id="div-pagetrail">'
                %s
            </div> <!-- /pagetrail -->''' % self.trail(d),
        html = [
            # End of page
            # self.pageinfo(page),
            self.endPage(),
            
            # Pre footer custom html (not recommended!)
            # self.emit_custom_html(self.cfg.page_footer1),
            
            # Footer
            u'''
    </div><!-- /content_wrap -->
    <div id="clear">
        &nbsp;
    </div><!-- /clear -->
        <!-- sidebar footer -->
		<div id="footer">
			<p>
				<a title="Valid XHTML 1.1" href="http://validator.w3.org/check/referer">Valid XHTML 1.1</a>
				&mdash;
				<a title="Valid CSS 1/2" href="http://jigsaw.w3.org/css-validator/check/referer">Valid CSS</a>
				<br />
				Licensed under a
				<a title="CC License" href="http://creativecommons.org/licenses/by/2.5/">
					Creative Commons Attribution License (v2.5)
				</a>
				<br />
				info [at] okfn.org
			</p>
		</div><!-- /footer sidebar -->
    <div id="footer_content">
            ''',
            editbar,
            # not used at present because css isn't working properly
            # pagetrail,
            u'''
        </div><!-- /footer -->
    </div><!-- /airlock --> 
            ''',
            
            # Post footer custom html
            self.emit_custom_html(self.cfg.page_footer2),
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

