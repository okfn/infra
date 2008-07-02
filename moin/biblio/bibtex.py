# -*- coding: iso-8859-1 -*-
"""MoinMoin - Bibtex Parser

Configuration Options:

    bibtex_bib2html_cmd -- path and command name of bibtex2html, needs to
                           be set if not already in PATH
    bibtex_bst_path     -- path to bst-style files, needs to
                           be set if these are not found by bibtex
                           automatically

Notes: This parser depends on bibtex and bibtex2html

TODO:
 - attachement links

$Id: bibtex.py,v 1.1.1.1 2007-06-07 20:36:15 gber Exp $
Copyright 2007 by Guido Berhoerster <guido+moinmoin@berhoerster.name>
Licensed under the GNU GPL, see COPYING for details.

$Log: bibtex.py,v $
Revision 1.1.1.1  2007-06-07 20:36:15  gber
initial import into CVS

2008-07-02: Modified by Rufus Pollock to use bibtex2html rather than bib2xhtml.
"""

import os
import tempfile
import subprocess
import codecs
import re
from StringIO import StringIO

Dependencies = []

# subprocess.check_call and CalledProcessError are only available in
# Python 2.5, so recreate them here
class CalledProcessError(Exception):
    """ This exception is raised when a process run by check_call()
    returns a non-zero exit status.  The exit status will be stored in
    the returncode attribute. """
    def __init__(self, returncode, cmd):
        self.returncode = returncode
        self.cmd = cmd
    def __str__(self):
        return "Command '%s' returned non-zero exit status %d" \
                % (self.cmd, self.returncode)


class BibtexRenderer:
    """Abstracted bibtex renderer

    Arguments:
        bibtex  -- string containing bibtex markup to be rendered
        request -- request object

    Keyword arguments:
        citations     -- list with keys of bibtex entries to be
                         rendered (default: empty)
        abstracts     -- boolean, show abstracts or not
                         (default: False)
        chronological -- boolean or the string "reversed",
                         chronological or reversed chronological
                         sorting (default: False)
        style         -- string "empty", "plain", "alpha", "named",
                         "unsort", "unsortlist", determining the style
                         to use (default: None)

    Notes:
    Raises OSError if bib2xhtml is not found or CalledProcessError if
    bib2xhtml returns wit a non-zero exit status.

    """

    def __init__(self, bibtex, request, citations=[], abstracts=False,\
            label=False, chronological=False, style=None):
        cfg = request.cfg
        # self.bib2html_cmd = "bib2xhtml"
        self.bib2html_cmd = 'bibtex2html'
        self.bst_path = None

        # retrieve configuration
        try:
             self.bib2html_cmd = cfg.bibtex_bib2html
        except AttributeError:
             pass
        try:
             self.bst_path = cfg.bibtex_bst_path
        except AttributeError:
             pass

        # the original bibtex implementation is not 8-bit clean, replace
        # non-ASCII characters with "?"
        # rgrp: is this necesssary?
        self.bibtex = bibtex.encode("ascii", "replace")

        # bib2xthml had -u for conversion to unicode but best we an do is
        # --unicode (and this is not always present ...)
        self.args = [self.bib2html_cmd, '-nobibsource',
                '-noheader', '-nodoc',
                '-dl' # use definition lists
                ]
        self.citations = '\n'.join(citations)
        self.citations = self.citations.encode("ascii", "replace")

        if not abstracts:
            self.args.append("-noabstract")
        # no equivalent in bibtex2html
        # maybe -nokeys
        # if label:
        #    self.args.append("-k")
        if chronological and chronological == "reversed":
            self.args.extend(["-d", "-r"])
        elif chronological:
            self.args.append("-d")
        if style in ("empty", "plain", "alpha", "named", "unsort", "unsortlist"):
            # bibtex2html and bib2xhtml the same
            self.args.extend(["-s", style])

    def render(self):
        """Render the bibtex markup (if requested, only cited entries)
        and return HTML output in a string.
        """
        ftd2, output_file = tempfile.mkstemp('.html')
        # output_file = os.path.abspath('output.html')
        self.args += ['-o', '-']
        tfd, citations_file = tempfile.mkstemp()
        # citations_file = os.path.abspath('cites.txt')
        if self.citations:
            # write citations to temporary output file
            f = open(citations_file, "w")
            f.write(self.citations)
            f.close()
            self.args += ['-citefile', citations_file]

        output = []
        # create temporary files for Bibtex input and logging
        bibfd, bibfile = tempfile.mkstemp(".bib")
        # bibfile = os.path.abspath('myinput.bib')
        #logfd, logfile = tempfile.mkstemp(".log")
        self.args.append(bibfile)

        # write Bibtex input to temporary file
        f = open(bibfile, "w")
        f.write(self.bibtex)
        f.close()

        def clean_up():
            if self.citations:
                os.remove(citations_file)
            if os.path.exists(output_file):
                os.remove(output_file)
            os.remove(bibfile)
            #os.remove(logfile)

        # execute bib2xhtml converter subprocess on forementionened
        # temporary files, bib2xhtml creates its temporary files in the
        # current working directory, so set it to a reasonable location, set
        # the set the BSTINPUTS environment variable if required in order to
        # help Bibtex finds the needed .bst files
        if self.bst_path:
            bstinputs = {"BSTINPUTS": self.bst_path}
        else:
            bstinputs = None
        try:
            import sys
            retcode = subprocess.call(self.args,
                env=bstinputs, cwd=tempfile.gettempdir(),
                stdout=open(output_file, 'w'),
                stderr=open(os.devnull, "w"))
                # stderr=sys.stderr)
            #retcode = subprocess.call(self.args,
            #    env=bstinputs, cwd=tempfile.gettempdir(),
            #    stdout=open(os.devnull, "w"), stderr=open(logfile, "w"))
            if retcode:
                raise CalledProcessError(retcode, " ".join(self.args))
        except OSError, error:
            # bib2xhtml not found or not executable
            clean_up()
            raise
        except CalledProcessError, error:
            # non-zero exit status
            clean_up()
            raise

        name_pattern = re.compile('<a name="(?P<anchor>[^"]*)">', re.UNICODE)
        href_pattern = re.compile('<a href="#(?P<anchor>[^"]*)">', re.UNICODE)
        try:
            # read the output (encoded as utf-8) back in
            f = codecs.open(output_file, "r", encoding="utf-8")
            output = f.read()
            output = name_pattern.sub(ur'<a id="ref:\g<anchor>">', output)
            output = href_pattern.sub(ur'<a href="#ref:\g<anchor>">', output)
            f.close()
        except:
            clean_up()
            raise

        return output


class Parser:
    """Parse Bibtex markup."""

    extensions = ['.bib']
    Dependencies = []

    def __init__(self, raw, request, **kw):
        self.request = request
        self.show = True
        self.abstracts = False
        self.label = True
        self.chronological = False
        self.style = "named"
        self.raw = raw
        self.request = request
        self._ = request.getText

        # parse format arguments
        from MoinMoin import wikiutil
        attrs, msg = wikiutil.parseAttributes(self.request, kw.get(
                                                             'format_args',''))
        if not msg:
            if attrs.get('show','"on"')[1:-1].lower() not in ('on', 'true',
                                                                        'yes'):
                self.show = False
            if attrs.get('abstracts','"off"')[1:-1].lower() in ('on', 'true',
                                                                        'yes'):
                self.abstracts = True
            if attrs.get('label','"on"')[1:-1].lower() not in ('on', 'true',
                                                                        'yes'):
                self.label = False
            if attrs.get('chronological','"off"')[1:-1].lower() in ('on',
                                                                'true', 'yes'):
                self.chronological = True
            elif attrs.get('chronological','"off"')[1:-1].lower() in (
                                                        'reverse', 'reversed'):
                self.chronological = "reversed"
            if attrs.get('style','"empty"')[1:-1].lower() in ('empty', 'plain',
                                     'alpha', 'named', 'unsort', 'unsortlist'):
                self.style = attrs.get('style','')[1:-1].lower()

    def format(self, formatter):
        """Format Bibtex markup as HTML and write output."""

        if not self.show: return

        _ = self._

        bib_renderer = BibtexRenderer(self.raw, self.request,
                abstracts=self.abstracts, label=self.label,
                chronological=self.chronological, style=self.style)
        try:
            output = bib_renderer.render()
        except OSError, error:
            self.request.write(formatter.sysmsg(1))
            self.request.write(formatter.escapedText(
                       _("Error: %(bib2html_cmd)s could not be found.") %
                       {"bib2html_cmd": self.bib2html_cmd}))
            self.request.write(formatter.sysmsg(0))
            return
        except CalledProcessError, error:
            msg = (_("An error occured while executing %(bib2html_cmd)s:" %
                                          {"bib2html_cmd": self.bib2html_cmd}))
            self.request.write(formatter.sysmsg(1))
            self.request.write(formatter.escapedText(msg))
            self.request.write(formatter.sysmsg(0))
            return

        # write through the rawHTML formatter if possible, otherwise write
        # just the Bibtex markup as preformatted text
        self.request.write(formatter.div(1, css_class="bibliography"))
        self.request.write(formatter.heading(1, 1))
        self.request.write(formatter.escapedText(_("Bibliography")))
        self.request.write(formatter.heading(0, 1))
        try:
            self.request.write(formatter.rawHTML(output))
        except:
            self.request.write(formatter.preformatted(1))
            self.request.write(formatter.text(self.raw.expandtabs()))
            self.request.write(formatter.preformatted(0))

