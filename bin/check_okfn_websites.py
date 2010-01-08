#!/usr/bin/env python
import unittest
import urllib2

class TestSites(unittest.TestCase):
    VERBOSE = True

    core_sites = [
            'http://www.okfn.org/',
            'http://blog.okfn.org/',
            'http://opendefinition.org/',
            'http://www.publicgeodata.org/',
            'http://m.okfn.org/',
            'http://dev.okfn.org/',
            'http://drn.okfn.org/',
            ]

    other_sites = [ 
            'http://www.witbd.org/',
            'http://www.freeculture.org.uk/',
            'http://www.publicdomainworks.net/',
            # 'http://www.wsfii.org/',
            'http://www.knowledgeforge.net/',
            'http://www.kforgeproject.com/',
            'http://www.openshakespeare.org/',
            'http://blog.openshakespeare.org/',
            'http://www.ckan.net',
            'http://www.publicdomainworks.net/',
            'http://www.openeconomics.net/',
            'http://www.isitopendata.org/',
            'http://www.wheredoesmymoneygo.org/',
            'http://www.openmilton.org/',
            ]

    def _print(self, msg):
        if self.VERBOSE:
            print(msg)

    def _check_site(self, url):
        self._print('Visiting: %s' % url)
        try:
            res = urllib2.urlopen(url)
            code = res.code
        except urllib2.HTTPError as e:
            code = e.code
            reason = e.read()
        except urllib2.URLError, e:
            code,info = e.reason
        assert code in [200,302], '\tFAILED (%s): %s' % (code,url)
        # o/w ok
        self._print('\tOK: %s' % url)

    def test_okfn(self):
        for url in self.core_sites:
            self._check_site(url)

    def test_others(self):
        for url in self.other_sites:
            self._check_site(url)

if __name__ == '__main__':
    unittest.main()
