import os
import optparse
import sys
import urlparse
import pprint


def check_site_migration(dest, paths):
    '''Check a site migration to dest where `paths` is list of paths that
    should exist on dest.
    '''
    import check_okfn_websites
    results = []
    for path in paths:
        url = urlparse.urljoin(dest, path)
        code,info = check_okfn_websites.TestSites.check_url(url)
        if code not in [200]:
            results.append([url,code,info])
    print('=== Missing ===')
    for item in results:
        print(item[0], item[1])


def check_opendefinition():
    import moinutils
    src = 'http://www.opendefinition.org'
    dest = 'http://staging.opendefinition.org'
    check_site_migration(dest, moin_utils.page_list(src))


def migrate_okfn_dot_org(wordpress_site_url=''):
    '''Migrate okfn.org to new wordpress site.

    1. Get page list from moin.
    2. Create pages_dict by iterating through pages downloading contents and
    converting
        1. Download
        2. Extract page title (top level header)
        3. Convert main text to markdown
            * Do not delete page title as we will suppress that in the theme
    '''
    import moinutils
    import wordpress
    cache_fp = 'okfn.org-moin-pages-cache.json'
    site_url = 'http://www.okfn.org/'
    print 'Retrieving page list'
    pages = moinutils.page_list(site_url)
    pages = [ p for p in pages
                if p not in [ u'/FrontPage', '/testfp', '/newfrontpage' ]
            ]
    print 'Retrieving individual pages'
    pages_dict = moinutils.convert_moin(site_url, pages)
    print 'Caching retrieved pages'
    import json
    json.dump(pages_dict, open(cache_fp, 'w'), indent=4)

    # pages_dict = json.load(open(cache_fp))
    # print pages_dict['/about']['description']

    # remap and filter page urls!
    for page_url in pages_dict.keys():
        if page_url in [
                '/pdw', '/datapkg', '/ckan', '/microfacts',
                '/vdm', '/econ', '/sysadmin', '/shakespeare', '/wdmmg',
                '/fcd', '/iai', '/kforge', '/kforge/overview',
                '/okftext',
                ]:
            pages_dict['/projects%s' % page_url] = pages_dict[page_url]
            del pages_dict[page_url]
        if page_url in [ '/communia' ] or page_url.startswith('/okforums'):
            pages_dict['/events%s' % page_url] = pages_dict[page_url]
            del pages_dict[page_url]
        if ( page_url in [ '/' ] or
            page_url.startswith('/old_open_knowledge_trail') ):
            del pages_dict[page_url]

    print 'Initializing wordpress'
    wp = wordpress.Wordpress.init_from_config('config.ini')
    wp.verbose =True
    print 'Creating pages in wordpress'
    changes = wp.create_many_pages(pages_dict)
    print 'Summary of changes'
    pprint.pprint(changes)


if __name__ == '__main__':
    usage = '''%prog {action}

    migrate_okfn_dot_org: migrate okfn.org to new wordpress site
    check_opendefinition: check open definition migration
    '''
    parser = optparse.OptionParser(usage)
    options, args = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        sys.exit(1)
    action = args[0] 
    if action == 'migrate_okfn_dot_org':
        migrate_okfn_dot_org()
    else:
        parser.print_help()
        sys.exit(1)

