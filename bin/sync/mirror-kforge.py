#!/usr/bin/env python

import os
here = os.path.dirname(__file__)
excludes_file = os.path.join(here, 'mirror-kforge-files.txt')
src_host = 'us0.okfn.org'

cmd1 = 'rsync -arvz --bwlimit=200 --delete -e "ssh -i /home/okfn/.ssh/okfn-rsync-key" okfn@%s:/home/kforge/ /home/kforge --include-from=%s' % (src_host, excludes_file)

os.system(cmd1)
