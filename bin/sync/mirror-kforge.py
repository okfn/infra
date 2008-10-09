#!/usr/bin/env python

import os
excludes_file = '/home/okfn/bin/mirror/mirror-kforge-files.txt' 
src_host = 'us0.okfn.org'

cmd1 = 'rsync -arvz --bwlimit=10 --delete -e "ssh -i /home/okfn/.ssh/okfn-rsync-key" okfn@%s:/home/kforge/ /home/kforge --include-from=%s' % (src_host, excludes_file)

os.system(cmd1)
