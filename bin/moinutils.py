#!/usr/bin/env python
"""
Scripts to assist with setting up moinmoin wikis:
  1. Wiki creation and deletion
  2. Automate upgrading moin wikis from version 1.2 to version 1.3
  3. Creation of apache config

TODO:
  1. apache config stuff
  2. sorting out wiki config automatically
  3. need to alter moin.cgi on install so it doesn't pick up farmconfig
"""
import os
import shutil
import logging
import re
import urllib2

logging.basicConfig()
# set the log level
# logging.basicConfig(level=logging.INFO) does NOT work for some reason
# this does work
logging.getLogger('').setLevel(logging.INFO)
logger = logging.getLogger('okfn.wiki')

moinShare = '/usr/share/moin'

class MoinUtils(object):
    
    def __init__(self, basePath=''):
        self.installedWikisBasePath = basePath
    
    def wikiPath(self, wikiName):
        return os.path.join(self.installedWikisBasePath, wikiName)

    def wikiExists(self, wikiName):
        return os.path.exists(self.wikiPath(wikiName))

    def createWiki(self, wikiName, withData = True):
        """
        Create a new wiki instance with default files.
        Written to work for moinmoin1.3
        [[TODO: allow for fastcgi]]
        """
        if self.wikiExists(wikiName):
            logger.warn('createWiki: wiki not created as it already exists')
            return
        newWikiBasePath = self.wikiPath(wikiName)
        logger.info('Creating new wiki: %s' % newWikiBasePath)
        os.makedirs(newWikiBasePath)
        if withData:
            shutil.copytree(os.path.join(moinShare, 'data'), os.path.join(newWikiBasePath, 'data'))
        shutil.copy(os.path.join(moinShare, 'config/wikiconfig.py'), newWikiBasePath)
        # do cgi-bin (do not install to cgi-bin but to base dir)
        # that way all paths will work out of the box
        # installCgiPath = os.path.join(newWikiBasePath, 'cgi-bin')
        # os.makedirs(installCgiPath)
        installCgiPath = newWikiBasePath
        shutil.copy(os.path.join(moinShare, 'server/moin.cgi'), installCgiPath)
        self.setPermissions(wikiName)

    def setPermissions(self, wikiName):
        newWikiBasePath = self.wikiPath(wikiName)
        # now set permissions
        # only webserver should have access
        if ( # os.system('sudo chown -R %s:%s %s' % ('www-data','www-data', newWikiBasePath))
            # and
            os.system('chmod -R ug+rwX %s' % newWikiBasePath)
            and
            os.system('chmod -R o-rwx %s' % newWikiBasePath)):
            logger.error('Failed to set permissions and owner correctly on %s' % newWikiBasePath)

    def removeWiki(self, wikiName):
        shutil.rmtree(self.wikiPath(wikiName))

    def migrateWikiData(self, dataSource, dataTarget):
        import re
        # moin migration scripts path
        scriptsPath = '/usr/lib/python2.3/site-packages/MoinMoin/scripts/migration'
        dataForMigration = os.path.join(scriptsPath, 'data')
        # delete all dirs named data* in scriptsPath dir
        tfiles  = os.listdir(scriptsPath)
        regexFilter  = re.compile("data.*", re.IGNORECASE)
        tfiles = filter(regexFilter.search, tfiles)
        for ff in tfiles:
            shutil.rmtree(os.path.join(scriptsPath, ff))
        shutil.copytree(dataSource, dataForMigration)
        scriptsToRun = [
            '12_to_13_mig01.py',
            '12_to_13_mig02.py',
            '12_to_13_mig03.py',
            '12_to_13_mig04.py',
            '12_to_13_mig05.py',
            '12_to_13_mig06.py',
            '12_to_13_mig07.py',
            '12_to_13_mig08.py',
            '12_to_13_mig09.py',
            '12_to_13_mig10.py',
            '12_to_13_mig11.py']# move the data to the right place
        # have to run the scripts from the local dir for it to work
        os.chdir(scriptsPath)
        print 'Migration: START'
        for script in scriptsToRun:
            os.system('./%s > /dev/null' % script)
        print 'Migration: COMPLETED'
        if os.path.exists(dataTarget):
            shutil.rmtree(dataTarget)
        shutil.copytree(dataForMigration, dataTarget)

    def migrateWiki(self, oldWikiPath, newWikiName):
        dataSource = os.path.join(oldWikiPath, 'data')
        dataTarget = os.path.join(self.wikiPath(newWikiName), 'data')
        # first create new wiki (without data dir)
        if self.wikiExists(newWikiName):
            self.removeWiki(newWikiName)
        self.createWiki(newWikiName, False)
        # now migrate
        self.migrateWikiData(dataSource,  dataTarget)
        # need to redo permissions because of data directory
        self.setPermissions(newWikiName)


import xml.dom.minidom
import urlparse
def _default_includer(url_path):
    '''Exclude all url paths starting with capital except FrontPage.
    '''
    # TODO: look through underlay directory?
    if ( url_path.startswith('/HelpOn') or
        url_path.startswith('/Wiki') or
        'Template' in url_path
        ):
        return False
    # pretty hardcore: exclude all items starting with uppercase
    elif re.match('^/[A-Z].*', url_path) and not url_path == '/FrontPage':
        return False
    else:
        return True

def page_list(site_url, includer=_default_includer):
    '''Get a list of pages associated with moinmoin site at `site_url`.

    Attempt to strip out standard 'underlay' wiki pages (e.g. HelpOn*)

    :param includer: filter method for page url pathes
    '''
    sitemap = '%s?action=sitemap' % site_url
    print sitemap
    content = urllib2.urlopen(sitemap).read()
    doc = xml.dom.minidom.parseString(content)
    urls = doc.documentElement.getElementsByTagName('url')
    def process(tag):
        loc = tag.getElementsByTagName('loc')[0].childNodes[0].nodeValue
        path = urlparse.urlsplit(loc).path
        lastmod = tag.getElementsByTagName('lastmod')[0].childNodes[0].nodeValue
        return [path, lastmod]
    results = map(process, urls)
    # strip out lastmods -- only paths are needed
    results = map(lambda x: x[0], results)
    results = filter(includer, results)
    return results


def moin2mkd(fileobj_or_str):
    '''Convert moin markup to markdown
    
    :param fileobj_or_str: file-like object or string containing moin text to
        convert.
    :return: converted text.

    TODO:
        * tables: || || ...
    '''
    if isinstance(fileobj_or_str, basestring):
        text = fileobj_or_str
    else:
        text = fileobj_or_str.read()
    flags = re.UNICODE | re.MULTILINE | re.DOTALL | re.VERBOSE
    regex = re.compile("'''''(.+?)'''''", flags)
    text = regex.sub(r'***\1***', text)

    regex = re.compile("'''(.+?)'''", flags)
    text = regex.sub(r'**\1**', text)

    regex = re.compile("''(.+?)''", flags)
    text = regex.sub(r'*\1*', text)

    ## headings
    ## do from bottom level up (i.e. start with =====, and finish with =)
    for x in reversed(range(1,6)):
        moin_head = '=' * x
        section = re.compile('^\s*%s(.+?)%s' % (moin_head, moin_head), flags)
        def _heading(heading):
            return '%s %s' % ('#'*x, heading.group(1).strip())
        text = section.sub(_heading, text)
    
    # links
    regex = re.compile(r'\[\[ ([^|]+) \| ([^]]+) \]\]', flags)
    def link_maker(match):
        url = match.group(1)
        # moin relative links start with '/'
        if url.startswith('/'):
            url = url.lstrip('/')
        # not a normal full url so absolute url
        elif not '://' in url:
            url = '/' + url
        return '[%s](%s)' % (match.group(2).strip(), url)

    text = regex.sub(link_maker, text)
    # for html
    # text = regex.sub(r'<a href="\1">\2</a>', text)

    text = text.replace('<<TableOfContents>>', "[toc title='Table of Contents']")
    
    # verbatim and stuff and special blocks
    regex = re.compile(r'{{{\#!html\s*\n (.+?) }}}', flags)
    text = regex.sub(r'\1', text)
    regex = re.compile(r'{{{\s*\n (.+?) }}}', flags)
    text = regex.sub(r'<pre>\n\1</pre>', text)

    ## img links
    ## must be done after verbatim
    regex = re.compile(r'{{(.+?)}}', flags)
    text = regex.sub(r'<img src="\1" alt="" />', text)


    return text


def get_title(content):
    '''Get the title of moinmoin page (i.e. content of first main (1st or 2nd
    level) heading.

    '''
    t = re.findall(r'^=([^=].+?)=', content, re.MULTILINE)
    if not t:
        t = re.findall('^==([^=].+?)==', content, re.MULTILINE)
    if not t: # no match at 1st or 2nd level so assume no title!
        return ''
    else:
        t = t[0]
        return t.strip()


def convert_moin(site_url, page_list):
    '''Convert set of moin pages to 'page dict' form with content in markdown
    form.

    :param site_url: base url (without trailing slash) for moin site.
    :param pagelist: list of page url pathes (as output by `page_list` method
        above).
    :return: dictionary of pages in page dict form::

            {
                page_url: {
                    'title': title,
                    'description': description
                    }
                ...
            }
    '''
    results = {}
    for count,page_url in enumerate(page_list):
        urlfo = urllib2.urlopen(site_url + page_url + '?action=raw')
        content = urlfo.read()
        urlfo.close()
        title = get_title(content)
        description = moin2mkd(content)
        description = description.replace('\r\n', '\n')
        results[page_url] = {
            'title': title,
            'description': description
            }
    return results


import optparse
import sys
if __name__ == '__main__':
    usage = '''%(prog)s {action} [args]

actions:
    create {path}: create wiki at path
    page_list {url}: list page in wiki at url using sitemap (attempt to exclude
        all standard moinmoin pages)
    moin2mkd {file-path}: convert material in file at {file-path} (- for stdin)
        in moin markup to markdown and print to stdout.
    '''
    parser = optparse.OptionParser(usage)
    options, args = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)
    action = args[0]
    utils = MoinUtils()
    if action  == 'create':
        utils.createWiki(args[2])
    elif action == 'page_list':
        out = page_list(args[1])
        print '\n'.join(out)
    elif action == 'moin2mkd':
        fp = args[1]
        if fp == '-':
            input = sys.stdin.read()
        else:
            input = open(fp).read()
        out = moin2mkd(input)
        print out
    else:
        print usage
        sys.exit(1)

