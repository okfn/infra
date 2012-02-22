#! /bin/env python
""" Merge two mailboxes by the Date: header value.
Fall back to X-List-Received-Date: if Date: not usable.
Should X-List-Received-Date: be first?

This is not well tested, and it assumes all messages in
both mbox files are parseable by email.message_from_file().

Usage: mbmerge path/to/mbox1 path/to/mbox2 > result

Then bin/arch --wipe list_name on new list so that archives are rebuilt ...

http://mail.python.org/pipermail/mailman-users/2008-March/060937.html
http://mail.python.org/pipermail/mailman-users/2006-January/048713.html
"""

import sys
import email
import mailbox

lasttime = 0
BIGTIME = 100. * 365.25 * 24. * 3600.

def main():
    if len(sys.argv) <> 3:
        print >> sys.stderr, \
            'Usage: ', sys.argv[0], ' mbox1 mbox2 > result'
        sys.exit(1)
    fp1 = open(sys.argv[1])
    mb1 = mailbox.UnixMailbox(fp1, email.message_from_file)
    fp2 = open(sys.argv[2])
    mb2 = mailbox.UnixMailbox(fp2, email.message_from_file)
    gen = email.Generator.Generator(sys.stdout)
    m1, t1 = get_next(mb1)
    m2, t2 = get_next(mb2)
    while m1 or m2:
        if t1 < t2:
            gen.flatten(m1, unixfrom=True)
            m1, t1 = get_next(mb1)
        else:
            gen.flatten(m2, unixfrom=True)
            m2, t2 = get_next(mb2)

def get_next(mb):
    global lasttime
    msg = mb.next()
    if msg is None:
        datime = BIGTIME
    else:
        datime = email.Utils.parsedate_tz(msg['date'])
        if datime:
            datime = email.Utils.mktime_tz(datime)
            lasttime = datime
        else:
            datime = email.Utils.parsedate_tz(msg['x-list-received-date'])
            if datime:
                datime = email.Utils.mktime_tz(datime)
                lasttime = datime
            else:
                datime = lasttime
    return msg, datime


if __name__ == '__main__':
    main()

