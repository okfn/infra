#!/usr/bin/env python

import os
here = os.path.dirname(__file__)
excludes_file = os.path.join(here, 'mirror-kforge-files.txt')
src_host = 'knowledgeforge.net'

cmd1 = 'rsync -arvz --delete -e "ssh -i mirror_key" root@%s:/home/kforge/ /home/kforge --include-from=%s' % (src_host, excludes_file)

os.system(cmd1)
