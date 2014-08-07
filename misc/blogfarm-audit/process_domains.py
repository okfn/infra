#!/usr/bin/env python
# This script helps check if all the domains in the blogfarm are pointing to
# the blogfarm and if all the domains pointing to the blogfarm are in the
# blogfarm

import argparse
import csv
import socket


def clean_domains():
    '''
    Get all entries in the CSV file from DNSMadeEasy which point to the
    blogfarm. Not very accurate.
    '''
    with open('domains-pointing.csv', 'r') as f:
        domain_reader = csv.reader(f)
        for row in domain_reader:
            if 'blogfarm' in row[3] or row[3] == '178.79.130.212':
                yield row


def domains_pointing():
    '''
    Return a list of domains pointing to the blogfarm.
    '''
    domains = clean_domains()
    for row in domains:
        if row[1]:
            yield '.'.join([row[1], row[0]])
        else:
            yield row[0]


def blogfarm_domains():
    '''
    Parse a text file with a list of domains into a python list
    '''
    with open('domains.txt', 'r') as f:
        return map(lambda x: x.replace('\n', ''), list(f))


def domain_in_blogfarm():
    '''
    Check if a domain pointing to the blogfarm is configured in the blogfarm.
    '''
    # Get list of domains configured in blogfarm
    blog_domains = blogfarm_domains()

    # Loop through all domains pointing to blogfarm
    for domain in domains_pointing():
        if domain in blog_domains:

            # If a domain pointing to blogfarm is in blogfarm_domains, remove
            # it from the list
            blog_domains.remove(domain)
        else:

            # This domains are pointing to blogfarm but not configured in the
            # blogfarm
            print "{0} not in blogfarm domains".format(domain)

    # These domains are configured in the blogfarm but not in our DNS
    # provider's list. May be externally configured.
    print blog_domains


def blogfarm_domains_to_blogfarm():
    '''
    Check if a domain in blogfarm actually points to blogfarm.
    '''
    # Get list of blogfarm domains from the list
    blog_domains = blogfarm_domains()
    for domain in blog_domains:
        try:

            # Get the IP address of each domain
            ip = socket.gethostbyname(domain)
        except socket.gaierror:

            # This domain is not configured to point anywhere
            print domain, 'not configured'
            continue

        # Hard-coded IP for blogfarm and old IP for blogfarm. If the IP points
        # to either of them, they are correctly pointing to the blogfarm
        if ip == '178.79.130.212' or ip == '178.79.131.171':
            continue

       # This domain does not point to the blogfarm
        print "{0} points to {1} and not blogfarm".format(domain, ip)


def main():
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process domain information'
                                     'for the blogfarm')
    parser.add_argument('--blogfarm', action='store_const', const=True,
                        help='Query blogs on the blogfarm and check which ones'
                        ' actually point to the blogfarm.')
    parser.add_argument('--domain', action='store_const', const=True, help=
                        'Query domain information about blogs in the blogfarm '
                        'and if they exist in the list of domains that live '
                        'at the blogfarm.')
    args = parser.parse_args()
    if args.blogfarm is True:
        domain_in_blogfarm()
    elif args.domain is True:
        blogfarm_domains_to_blogfarm()
    else:
        parser.error('Select blogfarm or domain option')
