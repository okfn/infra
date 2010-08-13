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
    
    in_ = """
= H1 and More =

<<TableOfContents>>

== H2 ==

{{{
Some pre stuff

Another line too
}}}

{{{#!html
Our own html
}}}


{{{#!html
<img src="http://www.okfn.org/images/myimage.png" title="xyz" alt="xyz" />
}}}

=== H3 ===

Some ''italics'', some '''strong''', some '''''strong and italics'''''.

==== H4 ====

Something = something else

{{http://www.okfn.org/images/image.png}}

===== H5 =====

 * [[http://rufuspollock.org/|website]] [[http://rufuspollock.org/|again]]

[[/relative|relative-link]]

[[about|absolute-link]]
    """
    expout = '''
# H1 and More

[toc title='Table of Contents']

## H2

<pre>
Some pre stuff

Another line too
</pre>

Our own html

<img src="http://www.okfn.org/images/myimage.png" title="xyz" alt="xyz" />

### H3

Some *italics*, some **strong**, some ***strong and italics***.

#### H4

Something = something else

<img src="http://www.okfn.org/images/image.png" alt="" />

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

    in2 = """
= About Us =

== Our Vision ==

We seek a world in which open knowledge is ubiquitous and routine. We seek to promote open knowledge because of its potential to deliver far-reaching societal benefits. Read more about [[vision/|our vision]].

== What is Open Knowledge? ==

'Open knowledge' is any content, information or data that people are free to use, re-use and redistribute -- without any legal, technological or social restriction. We detail '''exactly''' what openness entails in the [[http://opendefinition.org/1.0/|Open Knowledge Definition]]. The main principles are:

  1. Free and open '''access''' to the material
  2. Freedom to '''redistribute''' the material
"""

    expout2 = """
# About Us

## Our Vision

We seek a world in which open knowledge is ubiquitous and routine. We seek to promote open knowledge because of its potential to deliver far-reaching societal benefits. Read more about [our vision](/vision/).

##  What is Open Knowledge?

'Open knowledge' is any content, information or data that people are free to use, re-use and redistribute -- without any legal, technological or social restriction. We detail **exactly** what openness entails in the [Open Knowledge Definition](http://opendefinition.org/1.0/). The main principles are:

  1. Free and open **access** to the material
  2. Freedom to **redistribute** the material
"""
    def test_04(self):
        out = moin2mkd(self.in2)
        print out
        for line1,line2 in zip(self.expout2.split(), out.split()):
            assert line1 == line2, line2


def test_get_title():
    out = get_title(TestMoin2Mkd.in_)
    assert out == 'H1 and More', out

    in2_ = '''

== H2 ==

=== H3 ===
'''
    out = get_title(in2_)
    assert out == 'H2', out


