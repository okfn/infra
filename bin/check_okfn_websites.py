#!/usr/bin/env python
import twill.commands as web

import unittest

class TestSites(unittest.TestCase):

    core_sites = [
            'http://www.okfn.org/',
            'http://blog.okfn.org/',
            'http://okd.okfn.org/',
            'http://www.publicgeodata.org/',
            'http://m.okfn.org/',
            'http://dev.okfn.org/',
            'http://drn.okfn.org/',
            ]

    other_sites = [ 
            'http://www.witbd.org/',
            'http://www.freeculture.org.uk/',
            'http://www.publicdomainworks.net/',
            'http://www.wsfii.org/',
            'http://www.knowledgeforge.net/',
            'http://www.kforgeproject.com/',
            'http://www.openshakespeare.org/',
            'http://demo.openshakespeare.org/',
            'http://www.ckan.net',
            'http://db.publicdomainworks.net/',
            'http://www.openeconomics.net/'
            ]

    def test_okfn(self):
        for site in self.core_sites:
            web.go(site)
            web.code(200)

    def test_others(self):
        for site in self.other_sites:
            web.go(site)
            web.code(200)

if __name__ == '__main__':
    unittest.main()
