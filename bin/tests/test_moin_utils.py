import sys
sys.path.insert(0, '../')
from moin_utils import *

class TestMoinUtils(object):
    
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
    

def test_moin2mkd():
    out = moin2mkd("''abc''")
    assert out == '*abc*', out

    out = moin2mkd("'''abc'''")
    assert out == '**abc**', out
    
    in_ = '''
= H1 =

== H2 ==

=== H3 ===

==== H4 ====

===== H5 =====

 * [[http://rufuspollock.org/|website]] [[http://rufuspollock.org/|again]]
    '''
    expout = '''
# H1

## H2

### H3

#### H4

##### H5

 * [website](http://rufuspollock.org/) [again](http://rufuspollock.org/)
    '''
    out = moin2mkd(in_)
    # assert out == expout, out
    print out
    for line1,line2 in zip(expout.split(), out.split()):
        assert line1 == line2, line2
