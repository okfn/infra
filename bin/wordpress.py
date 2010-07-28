#!/usr/bin/env python
import os
import urllib
import pprint

# http://codex.wordpress.org/Installing/Updating_WordPress_with_Subversion
def install_svn(path, version='2.9.2'):
    cmd = 'svn co http://core.svn.wordpress.org/tags/%s %s' % (version, path)
    print 'Running: %s' % cmd
    os.system(cmd)

def secretkey():
    '''Obtain and print to stdout a wordpress secret key.'''
    # since 2.6
    url = 'https://api.wordpress.org/secret-key/1.1/'
    out = urllib.urlopen(url)
    print out.read()


import xmlrpclib
class Wordpress(object):
    '''Interact with an existing wordpress install via xml-rpc'''

    def __init__(self, wp_url, username, password, blog_id=0):
        self.user = username
        self.password = password
        self.server = xmlrpclib.ServerProxy(wp_url)
        self.blog_id = blog_id

    def get_page_list(self):
        '''http://codex.wordpress.org/XML-RPC_wp#wp.getPageList'''
        results = self.server.wp.getPageList(
            self.blog_id,
            self.user,
            self.password
        )
        return results

    def get_page(self, page_id):
        '''http://codex.wordpress.org/XML-RPC_wp#wp.getPage'''
        results = self.server.wp.getPage(
            self.blog_id,
            page_id,
            self.user,
            self.password
        )
        return results

    def get_pages(self):
        '''http://codex.wordpress.org/XML-RPC_wp#wp.getPages'''
        results = self.server.wp.getPages(
            self.blog_id,
            self.user,
            self.password
        )
        return results

    def new_page(self, **kwargs):
        '''http://codex.wordpress.org/XML-RPC_wp#wp.newPage
        
        :param **kwargs: all other possible arguments for content struct (see
        WP docs).
        '''
        content_struct = dict(kwargs)
        if not 'mt_allow_comments' in content_struct:
            content_struct['mt_allow_comments'] = 0
        if not 'mt_allow_pings' in content_struct:
            content_struct['mt_allow_pings'] = 0
        publish = True

        page_id = self.server.wp.newPage(
            self.blog_id,
            self.user,
            self.password,
            content_struct,
            publish
        )
        page_id = int(page_id)
        return page_id
        
    def delete_page(self, page_id):
        '''http://codex.wordpress.org/XML-RPC_wp#wp.deletePage'''
        result = self.server.wp.deletePage(
            self.blog_id,
            self.user,
            self.password,
            page_id
        )
        return bool(result)

    def delete_all_pages(self):
        for pagedict in self.get_page_list():
            self.delete_page(pagedict['page_id'])

    def edit_page(self, page_id, **kwargs):
        '''http://codex.wordpress.org/XML-RPC_wp#wp.editPage

        Note: editing a page leads to a new revision.

        :param **kwargs: attribute values for content struct (see wordpress docs).
        '''
        # existing values not in content_struct are *not* left alone but are
        # set to empty string!
        edit_struct = self.get_page(page_id)
        edit_struct.update(kwargs)
        result = self.server.wp.editPage(
            self.blog_id,
            page_id,
            self.user,
            self.password,
            edit_struct
        )
        return bool(result)

    def create_many_pages(self, pages_dict):
        '''Create many pages at once (and only create pages which do not already
        exist).

        pages_dict = {
            '/about/': {
                'title': 'ABC',
                'description': 'xxx'
            },
            '/about/people/': {
                'title': 'ABC',
                'description': 'xxx'
            }
        }
        '''
        ## get a list of existing pages keyed by their urls

        ## use get_page_list as that shows trash items as well as active
        pagelist = [ self.get_page(x['page_id']) for x in self.get_page_list()
                ]
        pagedict = dict([ (p['page_id'], p) for p in pagelist ])
        def get_page_url(page):
            parent_id = page['wp_page_parent_id']
            if parent_id == 0:
                return page['wp_slug']
            else:
                return get_page_url(pagedict[parent_id]) + '/' + page['wp_slug']
        existing_pages = dict(
                [(get_page_url(p), p) for p in pagelist]
        )
        pprint.pprint(existing_pages)
        changes = []
        # sort by key (url_path) so we can create in right order
        for url_path in sorted(pages_dict.keys()):
            v = pages_dict[url_path]
            content_struct = dict(v)
            if url_path.startswith('/'):
                url_path = url_path[1:]
            if url_path.endswith('/'):
                url_path = url_path[:-1]
            segments = url_path.split('/')
            content_struct['wp_slug'] = segments[-1]
            print url_path
            if len(segments) > 1:
                # must either already exist of have been created
                parent_url_path = '/'.join(segments[:-1])
                parent_page_id = existing_pages[parent_url_path]['page_id']
                content_struct['wp_page_parent_id'] = parent_page_id
            if not url_path in existing_pages:
                page_id = self.new_page(**content_struct)
                existing_pages[url_path] = { 'page_id': page_id }
                changes.append([page_id, 'new'])
            else:
                page_id = existing_pages[url_path]['page_id']
                self.edit_page(page_id, **content_struct)
                changes.append([page_id, 'edited'])
        return changes


class TestWordpress:
    url = 'http://localhost/~rgrp/wp/wp3.0/xmlrpc.php'
    wordpress = Wordpress(url, 'admin', 'pass')

    @classmethod
    def teardown_class(cls):
        cls.wordpress.delete_all_pages()

    def test_01_all(self):
        w = self.wordpress
        # get_pages and get_page_list differ in their treatment of deleted (in
        # trash) pages. Former does not return them, latter does ...
        pages_start = w.get_pages()

        title = 'test title' 
        content = 'test content, from python'
        new_page_id = w.new_page(title=title, description=content)
        assert new_page_id > 0

        pages = w.get_pages()
        assert len(pages) == len(pages_start) + 1, (pages, pages_start)
        page = w.get_page(new_page_id)
        assert page['title'] == title, page
        assert page['description'] == content, page

        new_title = 'test title updated'
        edited = w.edit_page(new_page_id, title=new_title)
        assert edited
        page = w.get_page(new_page_id)
        assert page['title'] == new_title, page
        assert page['description'] == content, page

        deleted = w.delete_page(new_page_id)
        pages = w.get_pages()
        pages2 = w.get_page_list()
        # see above re difference in set of pages returned
        assert pages != pages2, (len(pages), len(pages2))
        assert len(pages) == len(pages_start), (pages, pages_start)
    
    def test_02_create_many_pages(self):
        url1 = '/testpage/'
        url2 = url1 + 'subpage'
        pages_dict = {
            url1: {
                'title': 'Test Page',
                'description': 'xxx'
            },
            url2: {
                'title': 'ABC',
                'description': 'subpage xxx'
            }
        }
        self.wordpress.create_many_pages(pages_dict)
        def _check():
            pages = dict(
                    [ (p['title'],p) for p in self.wordpress.get_pages() ]
                    )
            assert len(pages) == 2
            testpage = pages_dict[url1]
            outtestpage = pages[testpage['title']]
            assert outtestpage['description'] == testpage['description'], outtestpage

            subpage = pages_dict[url2]
            assert pages[subpage['title']]['title'] == subpage['title'], pages
        _check()

        # now repeat to check we edit rather than create
        changes = self.wordpress.create_many_pages(pages_dict)
        assert len(changes) == 2
        _check()
        assert [ x[1] for x in changes ] == 2*['edited'], changes

if __name__ == '__main__':
    import optparse
    import sys
    usage = '''%prog {action}

    install-svn path  # install wp via svn method to path
    secretkey # generate secret keys for config
    '''
    parser = optparse.OptionParser(usage)
    parser.add_option('-w', '--wp-version',
            help='Wordpress version (e.g. 2.9.2) to use',
            default='2.9.2')
    options, args = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        sys.exit(1)
    action = args[0] 
    if action == 'install-svn':
        path = args[1]
        install_svn(path, options.wp_version)
    elif action == 'secretkey':
        secretkey()
    else:
        parser.print_help()
        sys.exit(1)

