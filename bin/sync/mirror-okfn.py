#!/usr/bin/env python

import os
excludes_file = '/home/okfn/bin/sync/mirror-okfn-excludes.txt' 
src_host = 'eu0.okfn.org'

cmd1 = 'rsync -avz --delete -e "ssh -i /home/okfn/.ssh/okfn-rsync-key" okfn@%s:/home/okfn/var /home/okfn/sync/slave --exclude-from=%s' % (src_host, excludes_file)

os.system(cmd1)
