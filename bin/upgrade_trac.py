import os

# envs = [ '/home/kforge/tmp/test_trac' ]

file_owner = 'www-data'

def run_cmd(cmd):
    newcmd = 'sudo -u %s %s' % (file_owner, cmd)
    print 'Running command: %s' % newcmd
    os.system(newcmd)

def process(env_path):
    print 'Processing: ', env_path
    db_fp = os.path.join(env_path, 'db', 'trac.db')
    db_bak_fp = os.path.join(env_path, 'db', 'trac.db.bak')
    mv_cmd = 'mv %s %s' % (db_fp, db_bak_fp)
    to_sqlite3_cmd = 'sqlite %s .dump | sqlite3 %s' % (db_bak_fp, db_fp) 
    upgrade_db_cmd = 'trac-admin %s upgrade ' % env_path
    upgrade_wiki_cmd = 'trac-admin %s wiki upgrade ' % env_path
    run_cmd(mv_cmd)
    run_cmd(to_sqlite3_cmd)
    run_cmd(upgrade_db_cmd)
    run_cmd(upgrade_wiki_cmd)

    # to remove
    # find . -name 'trac.db.bak.20070729' -exec rm -f {} \;

def process_all():
    for env_path in envs:
        process(env_path)

def test_setup():
    os.system('rm -Rf /home/kforge/tmp/test_trac')
    os.system('cp some_existing_trac_install /home/kforge/tmp/test_trac -R')
    os.system('chown www-data:www-data -R /home/kforge/tmp/test_trac/')

if __name__ == '__main__':
    # print envs
    test_setup()
    process_all()
