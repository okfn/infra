#!/usr/bin/env python

"""
Import moin wiki pages into a Trac database (with version
history).

Thomas Munro <munro@ip9.org>
"""

import sys
import os
import trac.env

def convert(trac_path, moin_path):
    # connect to trac DB
    print "Connecting to trac environment: %s" % (trac_path)
    env = trac.env.Environment(trac_path)
    db = env.get_db_cnx()
    db.autocommit = 0

    # build an index of moin users
    users = {}
    for user_id in os.listdir("%s/user" % moin_path):
        if not user_id.endswith(".trail"):
            f = open("%s/user/%s" % (moin_path, user_id), "r")
            for line in f.readlines():
                if line.startswith("name="):
                    users[user_id] = line.strip()[5:]
            f.close()

    # step through the pages directory looking for wiki pages...
    cursor = db.cursor()
    for page in os.listdir("%s/pages" % moin_path):
        # it's only a valid page if it has an edit-log
        log_file_name = "%s/pages/%s/edit-log" % (moin_path, page)
        if not os.path.isfile(log_file_name):
            continue
        print "Importing", page
        cursor.execute("DELETE FROM wiki WHERE name = %s", (page,))
        log_file = open(log_file_name, "r")
        for line in log_file.readlines():
            # extract meta data from line
            (time, revision, operation, dunno, ip, dns, user_id, x, comment) = line.split("\t")
            data_file_name = "%s/pages/%s/revisions/%s" % (moin_path, page, revision)
            if revision == "99999999" or not os.path.isfile(data_file_name):
                continue # missing revision?
            #print time, revision, operation, dunno, ip, dns, user_id
            if user_id == "":
                user_name = ""
            else:
                user_name = users[user_id]
            time = time[:-6]
            comment = comment.strip()
            # read in body of page
            data_file = open(data_file_name, "r")
            body = data_file.read()
            data_file.close()
            # insert into database
            cursor.execute("INSERT INTO wiki (name, version, time, author, ipnr, text, comment, readonly) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (page, revision, time, user_name, ip, body, comment, 0))
        log_file.close()
        
    db.commit()

    print "Finished."

def usage():
    print "moin2trac.py - imports moin wiki pages into trac"
    print
    print "Usage: moin2trac.py <trac-env-path> <moin-data-path>"
    print
    print "<moin-data-path> should be the full path to the moin data"
    print "directory containing 'user' and 'data'."
    print
    sys.exit(0)

def main():
    if len (sys.argv) != 3:
        usage()
    trac_env = sys.argv[1]
    pages = sys.argv[2]
    convert(trac_env, pages)

if __name__ == '__main__':
    main()
