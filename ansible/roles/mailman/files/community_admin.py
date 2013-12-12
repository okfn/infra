#!/usr/bin/python2.7

import sha
import paths
from Mailman import Utils
from Mailman import MailList
import configparser

community_lists='/etc/mailman/community_lists'

config = configparser.RawConfigParser()
config.read('/etc/mailman/community_admin.conf')

admin_email=config.get('mailman', 'admin_email')
admin_pass=config.get('mailman', 'admin_pass')


p = sha.new(admin_pass).hexdigest()

f = open(community_lists)
lists = f.read().splitlines()
f.close()

active_lists = Utils.list_names()

def add_moderator(list):
        mlist = MailList.MailList(list, lock=0)
        if admin_email not in mlist.moderator:
                print '-> Adding ' + admin_email + ' to ' + list
                try:   
                        mlist.Lock()
                        mlist.moderator.append(admin_email)
                        mlist.mod_password = p
                        mlist.Save()
                finally:
                        mlist.Unlock()
        else:  
                print '-> Admin ' + admin_email + ' already present, skipping..'
                return

for list in lists:
        if list in active_lists:
                print list
                add_moderator(list)
