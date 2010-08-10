import sys
sys.path.insert(0, '../')
from moinutils import *

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
    

class TestMoin2Mkd:
    def test_01(self):
        out = moin2mkd("''abc''")
        assert out == '*abc*', out

    def test_02(self):
        out = moin2mkd("'''abc'''")
        assert out == '**abc**', out
    
    in_ = '''
= H1 =

<<TableOfContents>>

== H2 ==

{{{
Some pre stuff

Another line too
}}}

{{{#!html
Our own html
}}}

=== H3 ===

==== H4 ====

===== H5 =====

 * [[http://rufuspollock.org/|website]] [[http://rufuspollock.org/|again]]

[[/relative|relative-link]]

[[about|absolute-link]]
    '''
    expout = '''
# H1

[toc title='Table of Contents']

## H2

<pre>
Some pre stuff

Another line too
</pre>

Our own html

### H3

#### H4

##### H5

 * [website](http://rufuspollock.org/) [again](http://rufuspollock.org/)

[relative-link](relative)

[absolute-link](/about)
    '''
    def test_03(self):
        out = moin2mkd(self.in_)
        # assert out == expout, out
        print out
        for line1,line2 in zip(self.expout.split(), out.split()):
            assert line1 == line2, line2


def test_get_title():
    out = get_title(TestMoin2Mkd.in_)
    assert out == 'H1', out

    in2_ = '''

== H2 ==

=== H3 ===
'''
    out = get_title(in2_)
    assert out == 'H2', out


