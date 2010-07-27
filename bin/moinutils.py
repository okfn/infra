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

import urllib2
import xml.dom.minidom
import urlparse
import re
def page_list(site_url, strict_exclude=True):
    '''Get a list of pages associated with moinmoin site at `site_url`.

    Attempt to strip out standard 'underlay' wiki pages (e.g. HelpOn*)

    @param strict_exclude: exclude all url paths starting with capital except
    FrontPage.
    '''
    sitemap = '%s?action=sitemap' % site_url
    content = urllib2.urlopen(sitemap).read()
    doc = xml.dom.minidom.parseString(content)
    urls = doc.documentElement.getElementsByTagName('url')
    def process(tag):
        loc = tag.getElementsByTagName('loc')[0].childNodes[0].nodeValue
        path = urlparse.urlsplit(loc).path
        lastmod = tag.getElementsByTagName('lastmod')[0].childNodes[0].nodeValue
        return [path, lastmod]
    results = map(process, urls)
    def exclude(item):
        path = item[0]
        # TODO: look through underlay directory?
        if ( path.startswith('/HelpOn') or
            path.startswith('/Wiki') or
            'Template' in path
            ):
            return False
        # pretty hardcore: exclude all items starting with uppercase
        elif re.match('^/[A-Z].*', path) and not path == '/FrontPage':
            return False
        else:
            return True
    results = filter(exclude, results)
    # return results
    # only return paths -- lastmods aren't needed
    return map(lambda x: x[0], results)


def moin2mkd(fileobj_or_str):
    '''Convert moin markup to markdown
    
    TODO:
        * tables: || || ...
        * pre: {{{ }}}
        * moinmoin absolute and relative links
    '''
    if isinstance(fileobj_or_str, basestring):
        text = fileobj_or_str
    else:
        text = fileobj_or_str.read()
    flags = re.UNICODE | re.MULTILINE
    regex = re.compile("'''''(.+)''''", flags)
    text = regex.sub(r'***\1***', text)

    regex = re.compile("'''(.*)'''", flags)
    text = regex.sub(r'**\1**', text)

    regex = re.compile("''(.+)''", flags)
    text = regex.sub(r'*\1*', text)

    # headings
    for x in reversed(range(1,6)):
        moin_head = '=' * x
        section = re.compile('%s\s*(.+)\s*%s' % (moin_head, moin_head), flags)
        text = section.sub('%s \\1' % ('#' * x), text)
    
    # links
    regex = re.compile(r'\[\[([^|]+)\|([^]]+)\]\]', flags)
    text = regex.sub(r'[\2](\1)', text)
    # for html
    # text = regex.sub(r'<a href="\1">\2</a>', text)
    return text


import optparse
import sys
if __name__ == '__main__':
    usage = '''%(prog)s {action} [args]

actions:
    create {path}: create wiki at path
    page_list {url}: list page in wiki at url using sitemap
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

