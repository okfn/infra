#!/usr/bin/env python

# This script trains SpamAssassin's Bayesian classifier using the held messages
# from one or more Mailman lists.
#
# After passing the messages to `sa-learn`, the held messages are discarded.
#
# Usage:
#
#     $ sudo python mailman-sa-learn.py list1 list2 ...
#

import argparse
import glob
import mailbox
import os
import cPickle as pickle
import subprocess
import sys

MAILMAN_DIR = '/usr/lib/mailman'
MAILMAN_DATA_DIR = '/var/lib/mailman/data'

def main(args):
    sys.path.append(MAILMAN_DIR)
    # add the messages to a temporary .mbox file
    mbox = mailbox.mbox('/tmp/spam.mbox')
    mbox.lock()
    os.chdir(MAILMAN_DATA_DIR)
    lists = args.lists
    try:
        held_messages = []
        for l in lists:
            list_glob = 'heldmsg-%s*' % l
            list_files = glob.glob(list_glob)
            held_messages.extend(list_files)
            if len(list_files) == 0:
                print 'No held messages found for %s' % l
                lists.pop(lists.index(l))
            else:
                print 'Adding held messages for %s' % l
                for f in list_files:
                    # held messages are pickled; unpickle them
                    # Mailman must be in the path to do this (above)
                    message = pickle.load(open(f))
                    mbox.add(message)
                    mbox.flush()
    finally:
        mbox.unlock()
    
    # call sa-learn
    print "Training SpamAssassin's Bayesian classifier with new spam..."
    subprocess.call(['sa-learn', '--spam', '--mbox', mbox._path])
  
    # clean up
    os.remove(mbox._path)
    print 'Discarding held messages for the following lists:'
    for l in lists:
        print l
    for f in held_messages:
        discard = os.path.join(MAILMAN_DIR, 'bin', 'discard')
        subprocess.call(['/usr/bin/sudo', discard, f])
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('lists', nargs='+')
    args = parser.parse_args()
    main(args)
