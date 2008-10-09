#!/usr/bin/env python

import os
excludes_file = '/home/okfn/bin/mirror/mirror-okfn-excludes.txt' 
src_host = 'us0.okfn.org'

cmd1 = 'rsync -avz --delete -e "ssh -i /home/okfn/.ssh/okfn-rsync-key" okfn@%s:/home/okfn/kforge /home/okfn --exclude-from=%s' % (src_host, excludes_file)
cmd2 = 'rsync -avz --delete -e "ssh -i /home/okfn/.ssh/okfn-rsync-key" okfn@%s:/home/okfn/var /home/okfn --exclude-from=%s' % (src_host, excludes_file)

os.system(cmd1)
os.system(cmd2)
