#!/usr/bin/env python
from webunit import webunittest
import unittest

class VerifyOkfnSite(webunittest.WebTestCase):
    def setUp(self):
        self.setServer('okfn.org', 80)
    
    def testBaseSite(self):
        self.assertCode('/', 200)
    
    def testWikiOkfn(self):
        self.assertCode('/wiki', 200)
    
    def testDrn(self):
        self.assertCode('/drn/', 301)
        self.assertCode('/drn/node/65', 301)
        self.setServer('drn.okfn.org', 80)
        self.assertCode('/', 200)
        self.assertCode('/node/65', 200)    
    
    def testProjects(self):
        projects = ['/fcd/', '/geo/', '/iai/', '/kforge/']
        for project in projects:
            self.assertCode(project, 200)
    
    def testProjectFcd(self):
        self.assertCode('/fcd/wiki/', 200)
    
    def testProjectGeo(self):
        self.assertCode('/geo/private/', 401)
        self.setBasicAuth('geo','<geo_password>')
        self.assertCode('/geo/private/', 200)
        self.assertCode('/geo/private/www/', 200)
    
    def testProjectWsfii(self):
        self.assertCode('/wsfii/private/', 401)
        self.setBasicAuth('wsfii','<wsfii_password>')
        self.assertCode('/wsfii/private/', 200)
        self.assertCode('/wsfii/private/www/', 200)
        
if __name__ == '__main__':
    unittest.main()
