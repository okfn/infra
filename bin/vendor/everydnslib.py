"""EveryDNS library module -- accessing EveryDNS programatically.

This is inspired by the EveryDNS PHP API:

    http://www.ultrize.com/everydns/

"""
__version__ = '0.2'

import base64
import cookielib
import re
import time
import urllib
import urllib2

EVERYDNS_HOSTNAME = 'www.everydns.com'
HTTP_USER_AGENT = 'PyEveryDNS/%s' % __version__
SESSION_TIMEOUT = 10 * 60   # 10 minute session


class LoginFailed(Exception):
    pass


class EveryDNS(object):
    """EveryDNS.com Python API.

    It tries to scrape EveryDNS's web interface to provide API to Python
    applications that need to modify DNS records on EveryDNS.

    """
    def __init__(self, username, password):
        """Create an EveryDNS API instance."""

        self.__username = username
        self.__password = password
        self.__lastlogin = None
        self.__cookie = cookielib.CookieJar()
        self.__opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(
            self.__cookie))
        self.__opener.addheaders = [
            ('Referer', 'http://%s/' % EVERYDNS_HOSTNAME),
            ('User-Agent', HTTP_USER_AGENT),
        ]
        self.__domains = None
        self.__records = None
        self.__reqcount = 0

    def add_domain(self, domain, secondary=None, dynamic=False, webhop=None):
        self.login()
        data = [
            ('action', 'addDomain'),
            ('newdomain', domain),
        ]
        if secondary:
            data.append(('sec', 'sec'))
            data.append(('ns', secondary))
        elif dynamic:
            data.append(('sec', 'dyn'))
        elif webhop:
            data.append(('sec', 'webhop'))
            data.append(('hop', webhop))

        self.fetchurl('dns.php', data)
        self.__domains = None

    def add_record(self, domain, host, rtype, value, mx='', ttl=7200):
        self.login()

        domain = domain.lower()
        rec = self.get_domain_rec(domain)

        host = host.lower()

        # we understand something without a period to be a label ;)
        if not host.endswith(domain) and not host.find('.') == -1:
            raise ValueError('%s is not a sub-domain or %s' % (host, domain))
        rtype = rtype.upper()
        try:
            rtype = {
                'A': '1',
                'CNAME': '2',
                'NS': '3',
                'MX': '4',
                'TXT': '5',
                'AAAA': '7',
            }[rtype]
        except KeyError:
            raise ValueError('Invalid record type "%s"' % rtype)

        if rec['type'] == 'dynamic':
            id_ = 'dynid'
            action = 'addDynamicRecord'
        else:
            id_ = 'did'
            action = 'addRecord'
        
        self.fetchurl('dns.php', [
            ('action', action),
            (id_, rec['did']),
            ('domain', domain),
            ('field1', host),
            ('type', rtype),
            ('field2', value),
            ('mxVal', str(mx or '')),
            ('ttl', str(ttl)),
        ])
        self.__records = None

    def cache_domains(self):
        if not self.__domains:
            self.__domains = self.list_domains()
        return self.__domains

    def cache_records(self, domain):
        if (not self.__records) or (self.__records[0] != domain):
            self.__records = domain, self.list_records(domain)
        return self.__records[1]

    def del_domain(self, domain):
        self.login()

        domain = domain.lower()
        rec = self.get_domain_rec(domain)
        did = rec['did']
        if rec['type'] == 'dynamic':
            self.fetchurl('dns.php', [
                ('action', 'delDomain'),
                ('dynid', did),
                ('t', 'dyn'),
            ])
            self.fetchurl('dns.php', [
                ('action', 'confDomain'),
                ('dynid', did)
            ])
        else:
            self.fetchurl('dns.php', [
                ('action', 'delDomain'),
                ('did', did)
            ])
            self.fetchurl('dns.php', [
                ('action', 'confDomain'),
                ('deldid', did)
            ])
        self.__domains = None

    def del_record(self, domain, rid):
        self.login()

        domain = domain.lower()
        rec = self.get_domain_rec(domain)

        if rec['type'] == 'dynamic':
            action = 'deleteDynamicRec'
            ridf = 'dynrid'
            didf = 'dynid'
        else:
            action = 'deleteRec'
            ridf = 'rid'
            didf = 'did'

        self.fetchurl('dns.php', [
            ('action', action),
            (ridf, rid),
            ('domain', base64.b64encode(domain)),
            (didf, rec['did'])
        ])
        self.__records = None

    def del_records(self, domain, host=None, rtype=None, value=None, mx=None,
            ttl=None):
        self.login()

        domain = domain.lower()
        host = host and host.lower()
        rtype = rtype and rtype.upper()

        did = self.get_did(domain)
        result = []
        for rec in self.cache_records(domain):
            if ((host is not None) and rec['host'] != host) or \
               ((rtype is not None) and rec['type'] != rtype) or \
               ((value is not None) and rec['value'] != value) or \
               ((mx is not None) and (rec['mx'] != mx)) or \
               ((ttl is not None) and (rec['ttl'] != ttl)):
                continue

            self.del_record(domain, rec['rid'])
            result.append(rec)

        if result:
            self.__records = None
        return result

    def fetchurl(self, uri, data=None):
        if isinstance(data, dict) or isinstance(data, list):
            data = urllib.urlencode(data)

        url = 'http://%s/%s' % (EVERYDNS_HOSTNAME, uri)
        res = self.__opener.open(url, data)
        res = res.read()
        if __debug__:
            self.__reqcount += 1
            debugfile = open('/tmp/everydns-%s.html' % self.__reqcount, 'wb')
            debugfile.write(url + '\n')
            debugfile.write(str(data) + '\n\n')
            debugfile.write(res)
            debugfile.close()
        if '<b>Logged Out</b>' in res:
            self.__lastlogin = None
            self.login()
            return self.fetchurl(uri, data)
        else:
            return res

    def get_did(self, domain):
        return self.get_domain_rec(domain)['did']

    def get_domain_rec(self, domain):
        domains = self.cache_domains()
        for rec in self.cache_domains():
            if rec['domain'] == domain:
                return rec
        raise ValueError('Domain "%s" does not exist' % domain)

    def list_domains(self):
        self.login()
        res = self.fetchurl('manage.php')

        # Primary domains
        all = re.findall(r'<a href="\.?/dns\.php\?action=editDomain\&did='
            r'(.*?)">\s*(?:<del>)?(?:<strong>)?(?:<font[^>]*>)?(.*?)<', res)
        result = [{
            'did': item[0],
            'domain': item[1].lower(),
            'type': 'primary',
        } for item in all]

        # Secondary domains
        all = re.findall(r'(?:<del>)?(?:<strong>)?(?:<font[^>]+>)?([^\s<]+)'
            r'(?:<\S*)?\s+<b>\(</b>(.*?)<b>\)</b>.*?'
            r'<a href="\.?/dns.php\?action=delDomain\&did=(.*?)\&t=sec"',
            res, re.S)
        result.extend([{
            'did': item[2],
            'domain': item[0],
            'secondary': item[1],
            'type': 'secondary',
        } for item in all])

        # Dynamic domains
        all = re.findall(r"<a href=(?:'|\")/?dns\.php\?action=editDynamic"
            r"\&dynid=(.*?)(?:'|\")>\s*(?:<del>)?(?:<strong>)?(?:<font[^>]*>)?"
            r'(.*?)<', res)
        result.extend([{
            'did': item[0],
            'domain': item[1],
            'type': 'dynamic',
        } for item in all])

        # Webhops
        all = re.findall(r'(?:<del>)?(?:<strong>)?(?:<font[^>]*>)?([^\s<]+)'
            r'(?:<\S*)? -> <input type=?"text" value="(.*?)".*?'
            r'<a href="\.?/dns.php\?action=delDomain\&did=(.*?)"', res, re.S)
        result.extend([{
            'did': item[2],
            'domain': item[0],
            'type': 'webhop',
            'webhop': item[1],
        } for item in all])

        return result

    def list_records(self, domain):
        self.login()

        domain = domain.lower()
        rec = self.get_domain_rec(domain)
        if rec['type'] == 'primary':
            id = 'did'
            action = 'editDomain'
        elif rec['type'] == 'dynamic':
            id = 'dynid'
            action = 'editDynamic'
        else:
            raise ValueError('Domain %s is not a primary or dynamic domain'
                % domain)

        res = self.fetchurl('manage.php', [
            ('action', action),
            (id, rec['did']),
            ('domain', base64.b64encode(domain))
        ])

        spos = res.find('Current Records:')
        if spos >= 0:
            spos = res.find('<table', spos)
            epos = res.find('</table>', spos)
            data = []
            while True:
                spos = res.find('<tr', spos, epos)
                if spos < 0:
                    break
                tr2 = res.find('</tr>', spos, epos)
                if tr2 < 0:
                    break
                raw = res[spos:tr2]
                row = re.findall(r'<td><div.*?><font.*?>(.*?)</font>', raw)

                if rec['type'] == 'dynamic':
                    if len(row) == 5:
                        row[3] = ''
                        row[4] = '300'
                    else: row.append('300')

                if len(row) == 5:
                    row = {
                        'host': row[0].lower(),
                        'type': row[1].upper(),
                        'value': row[2],
                        'mx': row[3],
                        'ttl': row[4],
                    }
                    match = re.search(r'<a href="\.?/dns.php\?action=delete'
                        r'(?:Dynamic)?Rec\&(?:dyn)?rid=(.*?)\&domain=', raw)
                    if match:
                        row['rid'] = match.group(1)
                    else:
                        row['rid'] = ''
                    data.append(row)
                spos = tr2 + 5
            return data

    def login(self):
        now = time.time()
        if self.__lastlogin and (now < (self.__lastlogin + SESSION_TIMEOUT)):
            return False
        if not self.__lastlogin:
            self.fetchurl('index.php')

        res = self.fetchurl('account.php', [
            ('action', 'login'),
            ('username', self.__username),
            ('password', self.__password)
        ])

        if ('Login failed, try again!' in res) or \
           ('Session errors. Try again later' in res):
            raise LoginFailed()
        else:
            self.__lastlogin = now
            return True


def setup_adsense_for_domain(edns, domain, pubid):
    """Set up Google AdSense for Domain.
    
    Domain must already exist on EveryDNS. The publisher ID should be the one
    showing on the top-right.
    
    """
    edns.del_records(domain, host=domain, rtype='A')
    edns.add_record(domain, domain, 'A', '216.239.32.21')
    edns.add_record(domain, domain, 'A', '216.239.34.21')
    edns.add_record(domain, domain, 'A', '216.239.36.21')
    edns.add_record(domain, domain, 'A', '216.239.38.21')
    edns.add_record(domain, 'www.' + domain, 'CNAME',
        pubid + '.afd.ghs.google.com')


def setup_gmail(edns, domain):
    """Set up Gmail MX for this domain.

    See http://www.google.com/support/a/bin/answer.py?hl=en&answer=33352

    Domain must already exist on EveryDNS. It will also wipe out all the
    existing MX records.

    """
    edns.del_records(domain, rtype='MX')
    edns.add_record(domain, domain, 'MX', 'aspmx.l.google.com', 1, 3600)
    edns.add_record(domain, domain, 'MX', 'alt1.aspmx.l.google.com', 5, 3600)
    edns.add_record(domain, domain, 'MX', 'alt2.aspmx.l.google.com', 5, 3600)
    edns.add_record(domain, domain, 'MX', 'aspmx2.googlemail.com', 10, 3600)
    edns.add_record(domain, domain, 'MX', 'aspmx3.googlemail.com', 10, 3600)


def setup_google_hosting(edns, domain, host):
    """Set up Google hosting for this domain/host.

    This is used by Google Apps to replace docs/calendar/mail/site/etc with a
    hostname on your own domain.

    """
    edns.add_record(domain, host, 'CNAME', 'ghs.google.com')


def setup_gtalk(edns, domain):
    raise NotImplementedError('Not implemented as EveryDNS does not '
        'support SRV records')
