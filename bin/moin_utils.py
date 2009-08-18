"""
Scripts to assist with setting up moinmoin wikis:
  1. Wiki creation and delet ion
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

class MoinUtilsTest(object):
    
    def setUp(self):
        import tempfile
        tempdir = tempfile.mkdtemp()
        self.moinUtils = MoinUtils(tempdir)
    
    def testCreateWiki(self):
        moinUtils = self.moinUtils
        wikiName = 'test-create-new-wiki'
        moinUtils.createWiki(wikiName)
        if not(moinUtils.wikiExists(wikiName)):
            print 'Error: new wiki does not exist'
            return
        moinUtils.removeWiki(wikiName)

if __name__ == '__main__':
    usage = 'moin_utils.py create {path}'
    import sys
    args = sys.argv
    if len(args) <= 2:
        print usage
        sys.exit(1)
    elif args[1] == 'create':
        utils = MoinUtils()
        utils.createWiki(args[2])
    else:
        print usage
        sys.exit(1)
