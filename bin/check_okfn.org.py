#!/usr/bin/env python
import twill.commands as web
import unittest

## TODO: use linkchecker

class VerifyOkfnSite(unittest.TestCase):

    base_url = 'http://www.okfn.org'
    # set this ...
    geo_password = '######'

    def url(self, offset):
        url = self.base_url + offset
        return url
        
    def assertCode(self, offset, code=200):
        url = self.base_url + offset
        web.go(url)
        web.code(code)
    
    def testBaseSite(self):
        self.assertCode('/', 200)
        self.assertCode('/ok_trail/', 200)
        self.assertCode('/okd/', 200)
        self.assertCode('/okforums/', 200)
    
    def testWikiOkfn(self):
        self.assertCode('/wiki', 200)
    
    def testDrn(self):
        self.assertCode('/drn/', 301)
        self.assertCode('/drn/node/65', 301)

    def testProjects(self):
        projects = ['/fcd/', '/geo/', '/iai/', '/kforge/']
        for project in projects:
            self.assertCode(project, 200)
    
    def testProjectFcd(self):
        # works in browser but not from here!
        # self.assertCode('/fcd/wiki/', 200)
        pass
    
    def testProjectGeo(self):
        offset = '/geo/dav/'
        self.assertCode(offset, 401)
        # realm = 'Open Knowledge Foundation Restricted Area' 
        # just ignore realm as it is simpler
        web.config('with_default_realm', True)
        realm = ''
        url = self.url(offset)
        web.add_auth('', url, 'geo', self.geo_password)
        self.assertCode('/geo/dav/', 200)
        self.assertCode('/geo/dav/www/', 200)
    

if __name__ == '__main__':
    unittest.main()
