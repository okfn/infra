# -*- coding: iso-8859-1 -*-
"""
    MoinMoin modern theme

    @copyright: (c) 2003-2004 by Nir Soffer, Thomas Waldmann
    @license: GNU GPL, see COPYING for details.
"""

from MoinMoin.theme import ThemeBase


class Theme(ThemeBase):

    name = "fcuk"

# Public functions #####################################################

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
            self.logo(),
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
            self.sideBarFcuk(),
            
            # Start of page
            self.startPage(),
            # self.title(d),
        ]
        return u'\n'.join(html)
    
    def newNaviBar(self):
        pass
        
    def sideBarFcuk(self):
        html = u"""
        <div id="sidewrap">
	        <div id="sidebartop">
	          <span>&nbsp;</span>
	        </div><!-- /sidebartop -->
	        
	        <div id="sidebar">
              <h3>
                Projects
              </h3>
              <ul>
                <li><a href="http://www.freeculture.org.uk/PublicDomainBurn">Public Domain Burn</a></li>
                <li><a href="http://www.freeculture.org.uk/creative_archive/">BBC Creative Archive</a></li>
                <li><a href="http://www.freeculture.org.uk/creative_commons/">Creative Commons</a></li>
                <li><a href="http://www.freeculture.org.uk/term_extn/">Recording Copyright Extension</a></li>
              </ul>
	        </div><!-- /sidebar -->
	        
        </div><!-- /sidewrap -->
        """
        return html
    
    def footer(self, d, **keywords):
        """ Assemble wiki footer
        
        @param d: parameter dictionary
        @keyword ...:...
        @rtype: unicode
        @return: page footer html
        """
        page = d['page']
        html = [
            # End of page
            self.pageinfo(page),
            self.endPage(),
            
            # Pre footer custom html (not recommended!)
            self.emit_custom_html(self.cfg.page_footer1),
            
            # Footer
            u'<div id="footer">',
            self.editbar(d),
            # self.credits(d),
            # self.showversion(d, **keywords),
            # added by rgrp:
            u'<div id="div-pagetrail">',
            self.trail(d),
            u'</div>',
            self.extraFooter(),
            u'</div>',
            
            # Post footer custom html
            self.emit_custom_html(self.cfg.page_footer2),
            ]
        return u'\n'.join(html)
    
    def extraFooter(self):
        return u"""
        <div id="new-credits">
        <p>
            Content licensed under <a href="http://creativecommons.org/licenses/by-sa/2.5/">Creative Commons Attribution-ShareAlike</a>
        </p>
        <p>
	        
        </p>
        <p>
	        Designed by <a href="http://whiteink.com/">WhiteInk</a>, 2005
            &mdash;
            <a href="http://validator.w3.org/check/referer">HTML4.01</a> | 
	        <a href="http://jigsaw.w3.org/css-validator/check/referer">CSS</a>
	        &mdash; <a href="http://creativecommons.org/licenses/by-sa/2.5/">"Some Rights Reserved"</a>
	    </p>
        </div>
	      <!--
	      <rdf:RDF xmlns="http://web.resource.org/cc/"
	          xmlns:dc="http://purl.org/dc/elements/1.1/"
	          xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
	      <Work rdf:about="">
	         <dc:type rdf:resource="http://purl.org/dc/dcmitype/Interactive" />
	         <license rdf:resource="http://creativecommons.org/licenses/by-sa/2.5/" />
	      </Work>
	      <License rdf:about="http://creativecommons.org/licenses/by-sa/2.5/">
	         <permits rdf:resource="http://web.resource.org/cc/Reproduction" />
	         <permits rdf:resource="http://web.resource.org/cc/Distribution" />
	         <requires rdf:resource="http://web.resource.org/cc/Notice" />
	         <requires rdf:resource="http://web.resource.org/cc/Attribution" />
	         <permits rdf:resource="http://web.resource.org/cc/DerivativeWorks" />
	         <requires rdf:resource="http://web.resource.org/cc/ShareAlike" />
	      </License>
	      </rdf:RDF>
	      -->"""
        
def execute(request):
    """
    Generate and return a theme object
        
    @param request: the request object
    @rtype: MoinTheme
    @return: Theme object
    """
    return Theme(request)

