
import sys
sys.path.insert(0, '../')
from wordpress import *


class TestWordpress:
    url = 'http://localhost/~rgrp/wp/wp3.0/'
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

