#!/usr/bin/python2.7

#1 fetch csv
#2 parse
# -  figure out site admins, site owners
# -  sort, uniq the site-owners, site-admins lists
#3 figure existing mailing list members of siteowners, siteadmins
#5 figure out which users should be removed from the mailling list
#6 remove users not present in siteowners list same for siteadmins
#7 add users present in siteowners, siteadmins but not in mailling list.
#8 update google spreadsheets for site-owners, admins

import urllib2
import gspread
import subprocess
from subprocess import call
import re
import logging
#import pickle
import configParser

config = ConfigParser.RawConfigParser()

config.read('/opt/scripts/config/config.ini')
g_doc_key=config.get('google', 'blog_site_admins_doc')
g_user=config.get('google', 'user')
g_password=config.get('google','pass')
g_doc_columns = { 'A' : 'Blog-sites', 'B': 'Blog-owners', 'C': 'Blog-admins' }

csv_url=config.get('other', 'csv')
default_list_admin = config.get('other', 'default_list_admin' )

blogsite_admins_list='blogsite-admins'
blogsite_owners_list='blogsite-owners'

list_members='/usr/sbin/list_members'  		#list_members list-name
remove_member='/usr/sbin/remove_members'	#remove_members listname <add1> <addr2> ...
add_members='/usr/sbin/add_members'			##echo 'foo@bar.com' | add_members -r - some-list
list_lists='/usr/sbin/list_lists'
newlist='/usr/sbin/newlist'					#newlist --urlhost=lists.okfn.org --emailhost=lists.okfn.org $listname someadmin@okfn.org <password>


all = {} 

#logging.basicConfig('filename='/var/log/blogsite-owners-update.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M', level=logging.INFO)


def notify(message):
	msg = MIMEText(message)
	msg['Subject'] = this_email['subject']
	msg['From'] = script_name
	msg['To'] = this_email['envelope_sender']
	
	s = smtplib.SMTP('localhost')
	s.sendmail(script_name, this_email['from'], msg.as_string())

def list_exists(name):
	out = subprocess.Popen([list_lists, '-b'], stdout=subprocess.PIPE)
	lists = out.stdout.read().split("\n")
	if name in lists:
		return True
	else:
		return False

def gen_password():
	import random
	import string
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(9))

def add_list(name):
	urlhost= '--urlhost=' + 'lists.okfn.org'
	emailhost= '--emailhost=' + 'lists.okfn.org'
	password=gen_password()
	admin=default_list_admin
	print 'adding list -> '	  +  name
	exit_status = call([ newlist, urlhost,  emailhost, name, admin, password ])
	return exit_status


def current_admins():
	
	so = []
	sa = []

	r = urllib2.Request(csv_url)
	r.add_header('User-agent', 'Not python.') 
	s = urllib2.urlopen(r).read()
		
	for line in s.split("\n"):
		if not line:
			continue
		i, domain, site_owner, site_admins = line.split(',')
		domain = domain.strip()
		domain = domain.lower()
		all[domain] = {}
		all[domain]['site_owners'] = []
		all[domain]['site_admins'] = ''
		site_owner = site_owner.strip()
		if site_owner:
			all[domain]['site_owners'].append(site_owner)
			if site_owner not in so:
				so.append(site_owner.lower())
		
		all[domain]['site_admins'] = site_admins
		for site_admin in site_admins.split(';'):
			site_admin = re.sub('\"','',site_admin)
			site_admin = site_admin.strip()
			if site_admin:
				if site_admin not in sa:
					sa.append(site_admin.lower())

	return [so , sa]

def previous_admins():
	
	blog_admins = []
	blog_owners = []

	if not list_exists(blogsite_admins_list):
		r = add_list(blogsite_admins_list)
		if not r == 0:
			print "failed to add list -> " +  blog_site_admins_list
		else:
			print "list added  -> " +  blogsite_admins_list
	else:
		out = subprocess.Popen([list_members, blogsite_admins_list], stdout=subprocess.PIPE)
		members = out.stdout.read().split("\n")
		for member in members:
			member = member.strip()
			if member:
				blog_admins.append(member.lower())	
	
	if not list_exists(blogsite_owners_list):
		r = add_list(blogsite_owners_list)
		if not r == 0:
			print "failed to add list -> " +  blog_owners_list
		else:
			print "list added -> " + blogsite_owners_list
	else:
		out = subprocess.Popen([list_members, blogsite_owners_list], stdout=subprocess.PIPE)
		members = out.stdout.read().split("\n")
		for member in members:
			member = member.strip()
			if member:
				blog_owners.append(member.lower())

	return [blog_owners, blog_admins]	

def manage_users(action, list, email_list):
	if email_list:
		for email in email_list:
			if action == 'add':
				#add user to list

				print 'adding user -> ' + email + ' to list ->' + list
				p1 = subprocess.Popen(['echo', email], stdout=subprocess.PIPE) 
				subprocess.Popen([add_members,'--admin-notify=n', '--welcome-msg=n', '-r', '-', list], stdin=p1.stdout)
			if action == 'del':
				print 'removing user -> ' + email + ' from list ->' + list
				subprocess.Popen(['remove_members', '--nouserack', '--noadminack', list, email], stdout=subprocess.PIPE)
	else:
		return

#fetch list of admins, owners
(cur_owners, cur_admins) = current_admins()
(prev_owners, prev_admins) = previous_admins()

##add new owners
add_owners = list(set(cur_owners) - set(prev_owners))
manage_users('add', blogsite_owners_list, add_owners)

##remove old owners
del_owners = list(set(prev_owners) - set(cur_owners))
manage_users('del', blogsite_owners_list, del_owners)

##add new admins
add_admins = list(set(cur_admins) - set(prev_admins))
manage_users('add', blogsite_admins_list, add_admins)

##remove old admins
del_owners = list(set(prev_admins) - set(cur_admins))
manage_users('del', blogsite_admins_list, del_owners)


#out= open('all.pickle', 'wb')
#pickle.dump(all,out)
#out.close()

#update google spreadsheet
try:
	g = gspread.login(g_user, g_password)
except:
	print 'failed to auth, spreadsheet update failed'
	exit(1)

try: 
	doc = g.open_by_key(g_doc_key)
	sheet = doc.get_worksheet(0)
except:
	msg  = 'Failed to open spreadsheet'
	exit(1)

#f = open('all.pickle','rb')
#a = pickle.load(f)

total_domains = len(all.keys())+1 #include the row heading
cell_list_domains = sheet.range('A1:A' + str(total_domains))
cell_list_siteowners =  sheet.range('B1:B' + str(total_domains)) 
cell_list_siteadmins = sheet.range('C1:C' + str(total_domains))

idx=1
cell_list_domains[0].value =  g_doc_columns['A']
cell_list_siteowners[0].value =  g_doc_columns['B']
cell_list_siteadmins[0].value =  g_doc_columns['C']

for domain in all.keys():
	cell_list_domains[idx].value=domain
	cell_list_siteowners[idx].value=a[domain]['site_owners'][0]
	cell_list_siteadmins[idx].value=a[domain]['site_admins'][0]
	idx += 1

sheet.update_cells(cell_list_domains)
sheet.update_cells(cell_list_siteowners)
sheet.update_cells(cell_list_siteadmins)

