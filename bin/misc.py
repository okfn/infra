import urlparse

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

import moin_utils
src = 'http://www.opendefinition.org'
dest = 'http://staging.opendefinition.org'
check_site_migration(src, dest, moin_utils.page_list(src))

