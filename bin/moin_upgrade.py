#!/usr/bin/env python
'''Automated upgrading of moinmoin wikis (way too painful!).

  * Main item is: 1.5 -> 1.6
  * Post 1.6 nothing much needed

Links:
  * http://moinmo.in/RickVanderveer/UpgradingFromMoin15ToMoin16
'''
import os
import shutil

moinscript = os.path.abspath('moin-1.6.4/MoinMoin/script/moin.py')
sudo = 'sudo -u www-data '
base = sudo + moinscript + ' --config-dir %s '
cleancache = ' maint cleancache'
# config-dir is path to NEW wikiconfig.py
config_dir = 'moin-1.6.4'

# should be data_dir as set up in moin-1.6.4/wikiconfig.py i.e. moin-1.6.4/data
data_path = os.path.join('moin-1.6.4', 'wiki', 'data')
def prepare(src_path):
    print 'RUNNING PREPARE'
    print 'Removing ', data_path
    # also remove any old stuff such as data.pre160 by adding * to end
    os.system('sudo rm -Rf %s*' % data_path)
    print 'Copying data from ', src_path, ' to ', data_path
    shutil.copytree(src_path, data_path)
    cmd = 'sudo chown -R www-data %s' % data_path
    print cmd
    os.system(cmd)

def clean():
    cmd = base + cleancache
    cmd = cmd % config_dir
    print cmd
    os.system(cmd)

def moinmigrate_to_1point6(wiki_url):
    # may be needed
    cmd1 = sudo + ' /usr/share/python-support/python-moinmoin/MoinMoin/script/old/migration/152_to_1050300.py %s' % data_path
    print cmd1
    os.system(cmd1)

    cmd2 = base + ' --wiki-url %s migration data' 
    cmd2 = cmd2 % (config_dir, wiki_url)
    print cmd2
    os.system(cmd2)

    print 'Renaming files (assume no renames - almost never are)'
    os.rename('moin-1.6.4/wiki/data/rename1.txt',
            'moin-1.6.4/wiki/data/rename2.txt')

    print cmd2
    os.system(cmd2)


import optparse
if __name__ == '__main__':
    usage = '''%prog src_path wiki_url
    
    src_path: path to wiki data directory
    wiki_url: url of wiki
    
    Output put in ./data
    '''
    parser = optparse.OptionParser(usage)
    options, args = parser.parse_args()

    src_path =  args[0]
    wiki_url = args[1]
    prepare(src_path)
    clean()
    moinmigrate_to_1point6(wiki_url)

