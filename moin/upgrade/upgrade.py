import os
import shutil

moinscript = os.path.abspath('moin-1.7.1/MoinMoin/script/moin.py')
# moinscript = os.path.abspath('moin-1.6.4/MoinMoin/script/moin.py')
sudo = 'sudo -u www-data '
base = sudo + moinscript + ' --config-dir %s '
cleancache = ' maint cleancache'
# config-dir is path to wikiconfig.py
upgrade = ' --wiki-url %s migration data' 

src_path = './okfn_main_site/data'
data_path = 'data'
def prepare():
    print 'RUNNING PREPARE'
    print 'Removing ', data_path
    os.system('sudo rm -Rf %s' % data_path)
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

def moinmigrate():
    cmd2 = base + upgrade
    print 
    print cmd2
    cmd2 = cmd2 % (config_dir, 'http://www.okfn.org/')
    print cmd2
    os.system(cmd2)

config_dir = 'moin-1.7.1'
# config_dir = 'moin-1.6.4'
def main():
    # prepare()
    # clean()
    moinmigrate()

if __name__ == '__main__':
    main()
