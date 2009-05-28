import os

# use maxdepth to avoid going into large (svn) directories
#  find  /home/kforge/knowledgeforge.net/var/project_data/ -maxdepth 5 -name 'trac.db'
envs = [
    '/home/kforge/knowledgeforge.net/var/project_data/consumotronic/trac/51',
    '/home/kforge/knowledgeforge.net/var/project_data/econ/trac/64',
    '/home/kforge/knowledgeforge.net/var/project_data/kforge/trac/10',
    '/home/kforge/knowledgeforge.net/var/project_data/okftext/trac/23',
    '/home/kforge/knowledgeforge.net/var/project_data/ukparse/trac/19',
    '/home/kforge/knowledgeforge.net/var/project_data/okr/trac/14',
    '/home/kforge/knowledgeforge.net/var/project_data/pdw/trac/33',
    '/home/kforge/knowledgeforge.net/var/project_data/shakespeare/trac/35',
    '/home/kforge/knowledgeforge.net/var/project_data/ckan/trac/28',
    '/home/kforge/knowledgeforge.net/var/project_data/facmin/trac/30',
    '/home/kforge/knowledgeforge.net/var/project_data/facmin/trac/31',
    '/home/kforge/knowledgeforge.net/var/project_data/domainmodel/trac/37',
    '/home/kforge/knowledgeforge.net/var/project_data/geometa/trac/49',
    '/home/kforge/knowledgeforge.net/var/project_data/tagopedia/trac/63',
    '/home/kforge/knowledgeforge.net/var/project_data/semwebparlparse/trac/69',
    '/home/kforge/knowledgeforge.net/var/project_data/mastercantabria/trac/74',
    '/home/kforge/knowledgeforge.net/var/project_data/geomaticlabs/trac/78',
    '/home/kforge/knowledgeforge.net/var/project_data/microfacts/trac/98',
    '/home/kforge/knowledgeforge.net/var/project_data/urakawa/trac/89',
    '/home/kforge/knowledgeforge.net/var/project_data/wikicursos/trac/108',
    '/home/kforge/knowledgeforge.net/var/project_data/wikicursos/trac/110',
    '/home/kforge/knowledgeforge.net/var/project_data/wikicursos/trac/111',
    '/home/kforge/knowledgeforge.net/var/project_data/ieparse/trac/118',
    '/home/kforge/knowledgeforge.net/var/project_data/okfn/trac/135',
    ]

# envs = [ '/home/kforge/tmp/test_trac' ]

testenvs = [ '/home/kforge/knowledgeforge.net/var/project_data/consumotronic/trac/51' ]

file_owner = 'www-data'

def run_cmd(cmd):
    newcmd = 'sudo -u %s %s' % (file_owner, cmd)
    print 'Running command: %s' % newcmd
    os.system(newcmd)

def upgrade_to_etch(env_path):
    # both an upgrade of sqlite and of trac
    print 'Processing: ', env_path
    db_fp = os.path.join(env_path, 'db', 'trac.db')
    db_bak_fp = os.path.join(env_path, 'db', 'trac.db.20070729')
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

def upgrade_to_Point11(env_path):
    upgrade_db_cmd = 'trac-admin %s upgrade ' % env_path
    upgrade_wiki_cmd = 'trac-admin %s wiki upgrade ' % env_path
    run_cmd(upgrade_db_cmd)
    run_cmd(upgrade_wiki_cmd)

def test_setup():
    os.system('rm -Rf /home/kforge/tmp/test_trac')
    os.system('cp /home/kforge/knowledgeforge.net/var/project_data/geometa/trac/49 /home/kforge/tmp/test_trac -R')
    os.system('chown www-data:www-data -R /home/kforge/tmp/test_trac/')

if __name__ == '__main__':
    import sys
    if not len(sys.argv) > 1:
        print 'Usage: python upgrade_trac.py list | test | upgrade'
    cmd = sys.argv[1]
    if cmd == 'list':
        print envs
    elif cmd == 'test':
        for env_path in testenvs:
            # upgrade_to_etch(env_path)
            upgrade_to_Point11(env_path)
    elif cmd == 'upgrade':
        for env_path in envs:
            upgrade_to_Point11(env_path)

