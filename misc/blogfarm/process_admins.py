#!/usr/bin/env python

import csv
import argparse


def split_admin_list(string):
    return string.split(';')


def main(owners=False, admins=False):
    user_list = []
    with open('site-admins.csv', 'r') as f:
        users = csv.reader(f)
        for row in users:

            # Exclude site ID 1. It's not an active site anymore, but the admin
            # landing site
            if row[1] == 'okblogfarm.org':
                continue

            # Add owners to the list if requested
            if owners:
                user_list.append(row[2])

            # Add admins to the list if requested
            if admins:
                user_list.extend(split_admin_list(row[3]))

            # If both are set to false, raise an exception and don't run the
            # loop unnecessarily
            if not (owners or admins):
                raise Exception('Admins or Owners need to be selected!')

    # Print each email in it's own line for mailman
    for user in set(user_list):
        print user.strip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process the CSV file that '
                                     'has all the site owners and admins.')
    parser.add_argument('--owners', action='store_const', const=True,
                        help='List of unique site owner email IDs')
    parser.add_argument('--admins', action='store_const', const=True, help=
                        'List of unique site admin email IDs')
    parser.add_argument('--both', action='store_const', const=True, help=
                        'List of unique site admin and owner email IDs')
    args = parser.parse_args()
    if args.owners is True:
        main(owners=True)
    elif args.admins is True:
        main(admins=True)
    elif args.both is True:
        main(owners=True, admins=True)
    else:
        parser.error('Select --admin, --owners, or --both option')
